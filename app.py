"""
智能标书审查系统 - 主应用
"""

import streamlit as st
import os
from datetime import datetime
from modules.document_parser import DocumentParser
from modules.ai_service import ClaudeService
from modules.database import DatabaseManager

# 页面配置
st.set_page_config(
    page_title="智能标书审查系统",
    page_icon="📋",
    layout="wide"
)

# 初始化
@st.cache_resource
def init_services():
    """初始化服务（缓存）"""
    try:
        ai_service = ClaudeService()
        db_manager = DatabaseManager()
        document_parser = DocumentParser()
        return ai_service, db_manager, document_parser
    except Exception as e:
        st.error(f"初始化失败: {str(e)}")
        st.info("请检查 .env 文件中的 ANTHROPIC_API_KEY 是否配置正确")
        st.stop()

# 确保上传目录存在
os.makedirs("database", exist_ok=True)

# 初始化 Session State
if 'current_record_id' not in st.session_state:
    st.session_state.current_record_id = None
if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = None
if 'bidding_response' not in st.session_state:
    st.session_state.bidding_response = None
if 'uploaded_files_info' not in st.session_state:
    st.session_state.uploaded_files_info = {}
if 'uploaded_files_content' not in st.session_state:
    st.session_state.uploaded_files_content = {}
if 'files_processed' not in st.session_state:
    st.session_state.files_processed = set()  # 记录已处理的文件


def main():
    """主函数"""
    ai_service, db_manager, document_parser = init_services()

    # 标题
    st.title("📋 智能标书审查系统")
    st.markdown("---")

    # 侧边栏 - 历史记录
    with st.sidebar:
        st.header("📚 历史记录")

        # 搜索框
        search_keyword = st.text_input("搜索项目", placeholder="输入项目名称")

        if search_keyword:
            records = db_manager.search_records(search_keyword)
        else:
            records = db_manager.get_all_records(limit=20)

        if records:
            for record in records:
                with st.expander(f"📁 {record.project_name}", expanded=False):
                    st.write(f"**创建时间**: {record.create_time.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**状态**: {record.status}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📂 加载", key=f"load_{record.id}", use_container_width=True):
                            load_record(record)
                            st.rerun()
                    with col2:
                        if st.button("🗑️ 删除", key=f"delete_{record.id}", use_container_width=True, type="secondary"):
                            # 使用 session_state 存储待删除记录ID
                            st.session_state.confirm_delete_id = record.id
                            st.rerun()

                    # 显示删除确认对话框
                    if st.session_state.get('confirm_delete_id') == record.id:
                        st.warning("⚠️ 确认删除此项目？")
                        st.markdown(f"**将删除**:")
                        st.markdown(f"- 数据库记录: {record.project_name}")

                        # 显示关联文件
                        import json
                        if record.uploaded_files:
                            files_dict = json.loads(record.uploaded_files)
                            if files_dict:
                                st.markdown(f"- 关联文件: {len(files_dict)} 个")
                                for cat, filename in files_dict.items():
                                    st.markdown(f"  - {filename}")

                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("✅ 确认删除", key=f"confirm_yes_{record.id}", type="primary", use_container_width=True):
                                delete_record_with_files(db_manager, record)
                                st.session_state.confirm_delete_id = None
                                st.success("删除成功！")
                                st.rerun()
                        with col_no:
                            if st.button("❌ 取消", key=f"confirm_no_{record.id}", use_container_width=True):
                                st.session_state.confirm_delete_id = None
                                st.rerun()
        else:
            st.info("暂无历史记录")

        st.markdown("---")
        if st.button("➕ 新建项目"):
            reset_session()
            st.rerun()

    # 主界面 - 使用 tabs
    tab1, tab2, tab3 = st.tabs(["📄 文件上传", "📊 标书分析", "📝 投标文件生成"])

    # Tab 1: 文件上传
    with tab1:
        file_upload_tab(db_manager, document_parser)

    # Tab 2: 标书分析
    with tab2:
        analysis_tab(ai_service, db_manager, document_parser)

    # Tab 3: 投标文件生成
    with tab3:
        generation_tab(ai_service, db_manager)


def file_upload_tab(db_manager, document_parser):
    """文件上传标签页"""
    st.header("📤 上传标书文件")

    # 项目名称
    project_name = st.text_input(
        "项目名称",
        value=st.session_state.get('project_name', ''),
        placeholder="请输入项目名称"
    )

    st.markdown("### 上传文件（可选）")
    st.info("支持 PDF、Word、Excel 格式。每类文件都是可选的，可根据实际情况上传。")

    # 文件类型配置（参考智标领航系统）
    # 前两项为招标文件，后四项为招标文件附件
    file_categories = [
        {
            "name": "招标文件正文",
            "types": ["pdf", "docx", "doc", "xlsx", "xls"],
            "help": "招标文件正文，支持PDF、Word、Excel等格式",
            "category": "招标文件"
        },
        {
            "name": "技术要求附件",
            "types": ["pdf", "docx", "doc", "xlsx", "xls"],
            "help": "技术规范、技术要求等附件",
            "category": "招标文件"
        },
        {
            "name": "工程量清单",
            "types": ["pdf", "xlsx", "xls", "docx", "doc"],
            "help": "工程量清单、报价表等（通常为Excel）",
            "category": "招标文件附件"
        },
        {
            "name": "评审标准附件",
            "types": ["pdf", "docx", "doc", "xlsx", "xls"],
            "help": "评分标准、评审办法等",
            "category": "招标文件附件"
        },
        {
            "name": "施工设计说明",
            "types": ["pdf", "docx", "doc", "dwg"],
            "help": "施工图纸、设计说明等",
            "category": "招标文件附件"
        },
        {
            "name": "方案建议书附件",
            "types": ["pdf", "docx", "doc", "xlsx", "xls"],
            "help": "其他方案建议相关文件",
            "category": "招标文件附件"
        }
    ]

    # 从 session_state 恢复已有的文件信息（如果存在）
    uploaded_files_info = st.session_state.get('uploaded_files_info', {}).copy()
    uploaded_files_content = st.session_state.get('uploaded_files_content', {}).copy()

    # 分组显示：招标文件 和 招标文件附件
    st.markdown("#### 📋 招标文件")
    bidding_docs = [cat for cat in file_categories if cat['category'] == '招标文件']
    cols1 = st.columns(2)

    for idx, category in enumerate(bidding_docs):
        with cols1[idx % 2]:
            st.markdown(f"**{category['name']}**")
            uploaded_file = st.file_uploader(
                category['name'],
                type=category['types'],
                help=category['help'],
                key=f"upload_{category['name']}",
                label_visibility="collapsed"
            )

            if uploaded_file:
                # 生成文件唯一标识
                file_id = f"{category['name']}_{uploaded_file.name}_{uploaded_file.size}"

                # 检查是否已经处理过
                if file_id not in st.session_state.files_processed:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_ext = uploaded_file.name.split('.')[-1]
                    safe_filename = f"{category['name']}_{timestamp}.{file_ext}"
                    file_path = os.path.join("database", safe_filename)

                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    uploaded_files_info[category['name']] = safe_filename
                    st.session_state.files_processed.add(file_id)

                    # 解析文件
                    try:
                        parsed_result = document_parser.parse(file_path)
                        uploaded_files_content[category['name']] = parsed_result['content']

                        # 立即更新 session_state
                        st.session_state.uploaded_files_info[category['name']] = safe_filename
                        st.session_state.uploaded_files_content[category['name']] = parsed_result['content']

                        st.success(f"✅ 已上传并解析: {uploaded_file.name}")
                        if 'metadata' in parsed_result:
                            meta = parsed_result['metadata']
                            if 'sheets' in meta:
                                st.caption(f"📊 包含 {meta['sheets']} 个工作表")
                            elif 'pages' in meta:
                                st.caption(f"📄 共 {meta['pages']} 页")
                    except Exception as e:
                        st.error(f"❌ 解析失败: {str(e)}")
                else:
                    # 已处理，从session获取
                    if category['name'] in st.session_state.uploaded_files_info:
                        uploaded_files_info[category['name']] = st.session_state.uploaded_files_info[category['name']]
                    if category['name'] in st.session_state.uploaded_files_content:
                        uploaded_files_content[category['name']] = st.session_state.uploaded_files_content[category['name']]
                    st.info(f"📌 已加载: {uploaded_file.name}")

    st.markdown("#### 📎 招标文件附件")
    attachments = [cat for cat in file_categories if cat['category'] == '招标文件附件']
    cols2 = st.columns(2)

    for idx, category in enumerate(attachments):
        with cols2[idx % 2]:
            st.markdown(f"**{category['name']}**")
            uploaded_file = st.file_uploader(
                category['name'],
                type=category['types'],
                help=category['help'],
                key=f"upload_{category['name']}",
                label_visibility="collapsed"
            )

            if uploaded_file:
                # 生成文件唯一标识
                file_id = f"{category['name']}_{uploaded_file.name}_{uploaded_file.size}"

                # 检查是否已经处理过
                if file_id not in st.session_state.files_processed:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_ext = uploaded_file.name.split('.')[-1]
                    safe_filename = f"{category['name']}_{timestamp}.{file_ext}"
                    file_path = os.path.join("database", safe_filename)

                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    uploaded_files_info[category['name']] = safe_filename
                    st.session_state.files_processed.add(file_id)

                    # 解析文件
                    try:
                        parsed_result = document_parser.parse(file_path)
                        uploaded_files_content[category['name']] = parsed_result['content']

                        # 立即更新 session_state
                        st.session_state.uploaded_files_info[category['name']] = safe_filename
                        st.session_state.uploaded_files_content[category['name']] = parsed_result['content']

                        st.success(f"✅ 已上传并解析: {uploaded_file.name}")
                        if 'metadata' in parsed_result:
                            meta = parsed_result['metadata']
                            if 'sheets' in meta:
                                st.caption(f"📊 包含 {meta['sheets']} 个工作表")
                            elif 'pages' in meta:
                                st.caption(f"📄 共 {meta['pages']} 页")
                    except Exception as e:
                        st.error(f"❌ 解析失败: {str(e)}")
                else:
                    # 已处理，从session获取
                    if category['name'] in st.session_state.uploaded_files_info:
                        uploaded_files_info[category['name']] = st.session_state.uploaded_files_info[category['name']]
                    if category['name'] in st.session_state.uploaded_files_content:
                        uploaded_files_content[category['name']] = st.session_state.uploaded_files_content[category['name']]
                    st.info(f"📌 已加载: {uploaded_file.name}")

    st.markdown("---")

    # 保存按钮
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("💾 保存项目", type="primary", use_container_width=True):
            if not project_name:
                st.error("请输入项目名称")
            else:
                # 保存到数据库
                if st.session_state.current_record_id:
                    # 更新现有记录
                    record = db_manager.update_record(
                        st.session_state.current_record_id,
                        project_name=project_name,
                        uploaded_files=uploaded_files_info
                    )
                    st.success(f"✅ 项目已更新: {project_name}")
                else:
                    # 创建新记录
                    record = db_manager.create_record(
                        project_name=project_name,
                        uploaded_files=uploaded_files_info
                    )
                    st.session_state.current_record_id = record.id
                    st.success(f"✅ 项目已保存: {project_name}")

                # 保存到 session
                st.session_state.project_name = project_name
                st.session_state.uploaded_files_content = uploaded_files_content
                st.session_state.uploaded_files_info = uploaded_files_info

    # 显示已上传文件（从session_state读取，确保显示所有文件）
    display_files = st.session_state.get('uploaded_files_info', {})
    if display_files:
        st.markdown("### 已上传文件")
        for category, filename in display_files.items():
            st.text(f"• {category}: {filename}")


def analysis_tab(ai_service, db_manager, document_parser):
    """标书分析标签页"""
    st.header("🔍 标书智能分析")

    # 检查是否有上传的文件
    if not st.session_state.get('uploaded_files_content'):
        st.warning("⚠️ 请先在'文件上传'标签页上传标书文件")
        return

    uploaded_files_content = st.session_state.uploaded_files_content

    # 显示文件概览
    st.markdown("### 📑 已加载文件")
    for category in uploaded_files_content.keys():
        st.text(f"• {category}")

    st.markdown("---")

    # 分析按钮
    if st.button("🚀 开始结构化解析", type="primary", use_container_width=True):
        # 计算输入token数（粗略估算：中文字符数/2）
        total_chars = sum(len(content) for content in uploaded_files_content.values())
        estimated_tokens = total_chars // 2

        st.info(f"📊 预估输入: {total_chars:,} 字符 ≈ {estimated_tokens:,} tokens")

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("正在调用 Claude AI 进行结构化解析...")
            progress_bar.progress(10)

            # 调用结构化解析
            analysis_report = ai_service.parse_bidding_document_structured(uploaded_files_content)
            progress_bar.progress(60)

            # 保存到 session 和数据库
            st.session_state.analysis_report = analysis_report
            progress_bar.progress(70)

            if st.session_state.current_record_id:
                db_manager.update_record(
                    st.session_state.current_record_id,
                    analysis_report=analysis_report,
                    status='analyzed'
                )
            progress_bar.progress(80)

            status_text.text("正在自动提取评审标准...")
            # 自动提取评审标准
            try:
                evaluation_criteria = ai_service.extract_evaluation_criteria(analysis_report)
                st.session_state.evaluation_criteria = evaluation_criteria
                progress_bar.progress(100)

                if st.session_state.current_record_id:
                    db_manager.update_record(
                        st.session_state.current_record_id,
                        bidding_response=evaluation_criteria
                    )

                status_text.empty()
                progress_bar.empty()
                st.success("✅ 结构化解析完成！✅ 评审标准已自动提取！")
            except Exception as e:
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                st.success("✅ 结构化解析完成！")
                st.warning(f"⚠️ 评审标准自动提取失败，请手动点击提取: {str(e)}")

            st.rerun()

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ 解析失败: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return

    # 显示解析结果 - 左右分栏布局
    if st.session_state.get('analysis_report'):
        st.markdown("---")

        # 导出和提取按钮
        col_export1, col_export2, col_extract = st.columns([1, 1, 2])
        with col_export1:
            st.download_button(
                label="📥 导出解析报告(MD)",
                data=st.session_state.analysis_report,
                file_name=f"招标文件解析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_export2:
            st.download_button(
                label="📥 导出解析报告(TXT)",
                data=st.session_state.analysis_report,
                file_name=f"招标文件解析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_extract:
            # 显示评审标准提取状态
            if st.session_state.get('evaluation_criteria'):
                st.success("✅ 评审标准已提取")
            else:
                if st.button("📋 手动提取评审标准", type="secondary", use_container_width=True):
                    with st.spinner("正在提取评审标准..."):
                        try:
                            evaluation_criteria = ai_service.extract_evaluation_criteria(
                                st.session_state.analysis_report
                            )
                            st.session_state.evaluation_criteria = evaluation_criteria

                            if st.session_state.current_record_id:
                                db_manager.update_record(
                                    st.session_state.current_record_id,
                                    bidding_response=evaluation_criteria
                                )

                            st.success("✅ 评审标准提取完成！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 提取失败: {str(e)}")

        # 显示评审标准（如果已提取）
        if st.session_state.get('evaluation_criteria'):
            st.markdown("---")
            with st.expander("📋 评审标准", expanded=False):
                st.markdown(st.session_state.evaluation_criteria)

        st.markdown("---")

        # 左右分栏：左侧显示结构化解析结果，右侧显示原文
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("### 📊 结构化解析结果")

            # 将解析报告按照 ## 标题分割成各个大类
            sections = st.session_state.analysis_report.split('\n## ')

            for i, section in enumerate(sections):
                if not section.strip():
                    continue

                # 第一个section前面没有 ##，需要特殊处理
                if i == 0:
                    lines = section.split('\n')
                    # 跳过顶部的说明文字，找到第一个 ## 开头的内容
                    continue

                # 提取标题和内容
                lines = section.split('\n', 1)
                title = lines[0].strip()
                content = lines[1] if len(lines) > 1 else ""

                # 使用 expander 显示每个大类
                with st.expander(f"📁 {title}", expanded=(i == 1)):
                    st.markdown(content)

        with col_right:
            st.markdown("### 📄 招标文件原文")

            # 选择要查看的文件
            if uploaded_files_content:
                selected_file = st.selectbox(
                    "选择查看文件",
                    options=list(uploaded_files_content.keys()),
                    key="original_doc_selector"
                )

                if selected_file and selected_file in uploaded_files_content:
                    # 显示文件内容
                    file_content = uploaded_files_content[selected_file]

                    # 显示文件信息
                    char_count = len(file_content)
                    st.caption(f"文件字符数: {char_count:,}")

                    # 使用text_area显示，更可靠
                    st.text_area(
                        "文件内容",
                        value=file_content,
                        height=600,
                        label_visibility="collapsed"
                    )
                else:
                    st.info("请选择要查看的文件")
            else:
                st.warning("暂无文件内容")


def generation_tab(ai_service, db_manager):
    """投标文件生成标签页"""
    st.header("📝 技术标文件生成")

    # 检查是否有评审标准
    if not st.session_state.get('evaluation_criteria'):
        st.warning("⚠️ 请先在'标书分析'标签页完成解析并提取评审标准")
        return

    # 初始化 session state
    if 'technical_outline' not in st.session_state:
        st.session_state.technical_outline = None
    if 'generated_sections' not in st.session_state:
        st.session_state.generated_sections = {}

    # 步骤1: 生成技术标目录
    st.markdown("### 步骤1: 生成技术标目录结构")

    if st.button("🏗️ 生成技术标目录", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("正在生成技术标目录结构...")
            progress_bar.progress(20)

            # 从解析报告中提取项目需求（取前5000字符）
            project_requirements = st.session_state.get('analysis_report', '')[:5000]

            # 检查是否有评审标准
            if not st.session_state.get('evaluation_criteria'):
                st.error("❌ 请先提取评审标准")
                progress_bar.empty()
                status_text.empty()
                return

            progress_bar.progress(40)

            outline = ai_service.generate_technical_proposal_outline(
                project_requirements=project_requirements,
                evaluation_criteria=st.session_state.evaluation_criteria
            )

            progress_bar.progress(90)

            st.session_state.technical_outline = outline
            progress_bar.progress(100)

            progress_bar.empty()
            status_text.empty()
            st.success("✅ 技术标目录生成完成！")
            st.rerun()

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ 生成失败: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

            # 显示调试信息
            with st.expander("调试信息"):
                st.write("project_requirements length:", len(st.session_state.get('analysis_report', '')))
                st.write("evaluation_criteria available:", bool(st.session_state.get('evaluation_criteria')))
                if st.session_state.get('evaluation_criteria'):
                    st.write("evaluation_criteria length:", len(st.session_state.evaluation_criteria))

    # 显示目录结构
    if st.session_state.technical_outline:
        st.markdown("---")
        st.markdown("### 📑 技术标目录结构")

        outline_data = st.session_state.technical_outline

        # 如果是原始文本格式
        if outline_data.get('raw'):
            st.markdown(outline_data['outline'])
        else:
            # JSON 格式的目录
            display_outline_tree(outline_data)

        st.markdown("---")

        # 步骤2: 分步生成章节
        st.markdown("### 步骤2: 分步生成技术标章节")

        # 提取所有章节供选择
        sections_list = extract_sections_from_outline(outline_data)

        if sections_list:
            selected_section = st.selectbox(
                "选择要生成的章节",
                options=range(len(sections_list)),
                format_func=lambda i: f"{sections_list[i]['title']} (建议{sections_list[i].get('word_count', 1000)}字)",
                key="section_selector"
            )

            section_info = sections_list[selected_section]

            col_gen, col_view = st.columns([1, 3])

            with col_gen:
                if st.button("✍️ 生成此章节", type="primary", use_container_width=True):
                    with st.spinner(f"正在生成 {section_info['title']}..."):
                        try:
                            section_content = ai_service.generate_technical_proposal_section(
                                section_title=section_info['title'],
                                word_count=section_info.get('word_count', 1000),
                                section_requirements=section_info.get('description', ''),
                                project_info=st.session_state.get('analysis_report', '')[:3000],
                                evaluation_criteria=st.session_state.evaluation_criteria
                            )

                            # 保存到 session
                            st.session_state.generated_sections[section_info['title']] = section_content
                            st.success("✅ 章节生成完成！")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ 生成失败: {str(e)}")

            with col_view:
                # 显示已生成的章节数量
                total_sections = len(sections_list)
                generated_count = len(st.session_state.generated_sections)
                st.info(f"📊 进度: {generated_count}/{total_sections} 个章节已生成")

        # 显示已生成的章节
        if st.session_state.generated_sections:
            st.markdown("---")
            st.markdown("### 📄 已生成章节")

            for section_title, content in st.session_state.generated_sections.items():
                with st.expander(f"📝 {section_title}", expanded=False):
                    st.markdown(content)

                    # 字数统计
                    word_count = len(content.replace(' ', '').replace('\n', ''))
                    st.caption(f"字数: {word_count}")

            # 合并导出按钮
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                # 合并所有章节
                merged_content = merge_all_sections(
                    st.session_state.technical_outline,
                    st.session_state.generated_sections
                )

                st.download_button(
                    label="📥 导出完整技术标(MD)",
                    data=merged_content,
                    file_name=f"技术标_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col2:
                st.download_button(
                    label="📥 导出完整技术标(TXT)",
                    data=merged_content,
                    file_name=f"技术标_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )


def display_outline_tree(outline_data):
    """显示目录树结构"""
    if 'outline' in outline_data and isinstance(outline_data['outline'], list):
        for item in outline_data['outline']:
            display_outline_item(item, level=0)
    else:
        st.markdown(str(outline_data))


def display_outline_item(item, level=0):
    """递归显示目录项"""
    indent = "  " * level
    title = item.get('title', '')
    word_count = item.get('word_count', '')
    description = item.get('description', '')

    if word_count:
        st.markdown(f"{indent}- **{title}** (建议{word_count}字)")
    else:
        st.markdown(f"{indent}- **{title}**")

    if description:
        st.markdown(f"{indent}  _{description}_")

    # 递归显示子项
    if 'children' in item and item['children']:
        for child in item['children']:
            display_outline_item(child, level + 1)


def extract_sections_from_outline(outline_data):
    """从目录结构中提取所有章节"""
    sections = []

    if outline_data.get('raw'):
        # 原始文本格式，无法提取
        return []

    if 'outline' in outline_data and isinstance(outline_data['outline'], list):
        for item in outline_data['outline']:
            extract_sections_recursive(item, sections)

    return sections


def extract_sections_recursive(item, sections, parent_title=''):
    """递归提取章节"""
    title = item.get('title', '')
    full_title = f"{parent_title} {title}".strip() if parent_title else title

    # 如果有 word_count，说明是可生成的章节
    if 'word_count' in item:
        sections.append({
            'title': full_title,
            'word_count': item['word_count'],
            'description': item.get('description', '')
        })

    # 递归处理子项
    if 'children' in item and item['children']:
        for child in item['children']:
            extract_sections_recursive(child, sections, full_title)


def merge_all_sections(outline, generated_sections):
    """合并所有已生成的章节为完整文档"""
    content_parts = [
        "# 技术标文档\n\n",
        f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n",
        "---\n\n"
    ]

    # 如果有目录结构
    if not outline.get('raw'):
        content_parts.append("## 目录\n\n")
        # 这里可以添加目录生成逻辑
        content_parts.append("\n---\n\n")

    # 添加所有生成的章节
    for section_title, section_content in generated_sections.items():
        content_parts.append(f"\n\n{section_content}\n\n")
        content_parts.append("---\n\n")

    return "".join(content_parts)


def load_record(record):
    """加载历史记录"""
    st.session_state.current_record_id = record.id
    st.session_state.project_name = record.project_name
    st.session_state.analysis_report = record.analysis_report
    st.session_state.bidding_response = record.bidding_response

    # 加载文件信息
    import json
    if record.uploaded_files:
        uploaded_files_info = json.loads(record.uploaded_files)
        st.session_state.uploaded_files_info = uploaded_files_info

        # 重新解析文件内容
        document_parser = DocumentParser()
        uploaded_files_content = {}
        for category, filename in uploaded_files_info.items():
            file_path = os.path.join("database", filename)
            if os.path.exists(file_path):
                try:
                    parsed_result = document_parser.parse(file_path)
                    uploaded_files_content[category] = parsed_result['content']
                except:
                    pass
        st.session_state.uploaded_files_content = uploaded_files_content


def reset_session():
    """重置 session"""
    st.session_state.current_record_id = None
    st.session_state.project_name = ''
    st.session_state.analysis_report = None
    st.session_state.bidding_response = None
    st.session_state.uploaded_files_content = {}
    st.session_state.uploaded_files_info = {}
    st.session_state.files_processed = set()


def delete_record_with_files(db_manager, record):
    """
    删除记录及其关联文件

    Args:
        db_manager: 数据库管理器
        record: 要删除的记录对象
    """
    import json

    # 1. 删除关联的文件
    if record.uploaded_files:
        try:
            files_dict = json.loads(record.uploaded_files)
            for category, filename in files_dict.items():
                file_path = os.path.join("database", filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        st.warning(f"无法删除文件 {filename}: {str(e)}")
        except Exception as e:
            st.warning(f"解析文件信息失败: {str(e)}")

    # 2. 删除数据库记录
    try:
        db_manager.delete_record(record.id)
    except Exception as e:
        st.error(f"删除数据库记录失败: {str(e)}")


if __name__ == "__main__":
    main()

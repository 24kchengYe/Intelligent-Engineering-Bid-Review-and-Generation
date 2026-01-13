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
os.makedirs("uploads", exist_ok=True)

# 初始化 Session State
if 'current_record_id' not in st.session_state:
    st.session_state.current_record_id = None
if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = None
if 'bidding_response' not in st.session_state:
    st.session_state.bidding_response = None


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
                    if st.button("加载", key=f"load_{record.id}"):
                        load_record(record)
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

    # 文件类型配置（可扩展）
    file_categories = [
        {"name": "PDF规范", "types": ["pdf"], "help": "工程规范、技术要求等PDF文件"},
        {"name": "Word方案", "types": ["docx", "doc"], "help": "技术方案、商务方案等Word文件"},
        {"name": "Excel清单", "types": ["xlsx", "xls"], "help": "工程量清单、报价表等Excel文件"},
        {"name": "其他附件", "types": ["pdf", "docx", "doc", "xlsx", "xls"], "help": "其他相关文件"}
    ]

    uploaded_files_info = {}
    uploaded_files_content = {}

    # 创建列布局
    cols = st.columns(2)

    for idx, category in enumerate(file_categories):
        with cols[idx % 2]:
            st.markdown(f"**{category['name']}**")
            uploaded_file = st.file_uploader(
                category['name'],
                type=category['types'],
                help=category['help'],
                key=f"upload_{category['name']}",
                label_visibility="collapsed"
            )

            if uploaded_file:
                # 保存文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = uploaded_file.name.split('.')[-1]
                safe_filename = f"{category['name']}_{timestamp}.{file_ext}"
                file_path = os.path.join("uploads", safe_filename)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                uploaded_files_info[category['name']] = safe_filename

                # 解析文件
                try:
                    parsed_result = document_parser.parse(file_path)
                    uploaded_files_content[category['name']] = parsed_result['content']
                    st.success(f"✅ 已上传并解析: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ 解析失败: {str(e)}")

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

    # 显示已上传文件
    if uploaded_files_info:
        st.markdown("### 已上传文件")
        for category, filename in uploaded_files_info.items():
            st.text(f"• {category}: {filename}")


def analysis_tab(ai_service, db_manager, document_parser):
    """标书分析标签页"""
    st.header("🔍 标书智能分析")

    # 检查是否有上传的文件
    if not st.session_state.get('uploaded_files_content'):
        st.warning("⚠️ 请先在"文件上传"标签页上传标书文件")
        return

    uploaded_files_content = st.session_state.uploaded_files_content

    # 显示文件概览
    st.markdown("### 📑 已加载文件")
    for category in uploaded_files_content.keys():
        st.text(f"• {category}")

    st.markdown("---")

    # 分析按钮
    if st.button("🚀 开始AI分析", type="primary", use_container_width=True):
        with st.spinner("正在调用 Claude AI 分析标书，这可能需要几十秒..."):
            try:
                # 调用 AI 分析
                analysis_report = ai_service.analyze_bidding_document(uploaded_files_content)

                # 保存到 session 和数据库
                st.session_state.analysis_report = analysis_report

                if st.session_state.current_record_id:
                    db_manager.update_record(
                        st.session_state.current_record_id,
                        analysis_report=analysis_report,
                        status='analyzed'
                    )

                st.success("✅ 分析完成！")

            except Exception as e:
                st.error(f"❌ 分析失败: {str(e)}")
                return

    # 显示分析报告
    if st.session_state.get('analysis_report'):
        st.markdown("### 📊 分析报告")
        st.markdown(st.session_state.analysis_report)

        # 下载按钮
        st.download_button(
            label="📥 下载分析报告",
            data=st.session_state.analysis_report,
            file_name=f"标书分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )


def generation_tab(ai_service, db_manager):
    """投标文件生成标签页"""
    st.header("📝 投标文件生成")

    # 检查是否有分析报告
    if not st.session_state.get('analysis_report'):
        st.warning("⚠️ 请先在"标书分析"标签页完成分析")
        return

    st.markdown("### 📋 基于分析报告生成投标文件")

    # 额外要求
    additional_requirements = st.text_area(
        "特殊要求（可选）",
        placeholder="例如：突出我司在XX领域的优势，强调XX项目经验等",
        height=100
    )

    # 生成按钮
    if st.button("✨ 生成投标文件", type="primary", use_container_width=True):
        with st.spinner("正在生成投标文件，这可能需要几十秒..."):
            try:
                # 调用 AI 生成
                bidding_response = ai_service.generate_bidding_response(
                    analysis_report=st.session_state.analysis_report,
                    document_contents=st.session_state.get('uploaded_files_content', {}),
                    requirements=additional_requirements if additional_requirements else None
                )

                # 保存到 session 和数据库
                st.session_state.bidding_response = bidding_response

                if st.session_state.current_record_id:
                    db_manager.update_record(
                        st.session_state.current_record_id,
                        bidding_response=bidding_response,
                        status='completed'
                    )

                st.success("✅ 投标文件生成完成！")

            except Exception as e:
                st.error(f"❌ 生成失败: {str(e)}")
                return

    # 显示生成的投标文件
    if st.session_state.get('bidding_response'):
        st.markdown("### 📄 投标响应文件")
        st.markdown(st.session_state.bidding_response)

        # 下载按钮
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 下载投标文件（Markdown）",
                data=st.session_state.bidding_response,
                file_name=f"投标文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        with col2:
            st.download_button(
                label="📥 下载投标文件（文本）",
                data=st.session_state.bidding_response,
                file_name=f"投标文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )


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
            file_path = os.path.join("uploads", filename)
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


if __name__ == "__main__":
    main()

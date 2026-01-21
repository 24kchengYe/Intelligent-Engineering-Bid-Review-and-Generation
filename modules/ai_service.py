"""
AI 服务模块
支持多种AI模型：OpenAI GPT-4o、Claude等
"""

import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
from .ai_provider import get_ai_provider, AIProvider
from .text_processor import TextProcessor, ContentCompressor
from .prompts import (
    BIDDING_DOCUMENT_ANALYSIS_PROMPT,
    EVALUATION_CRITERIA_EXTRACTION_PROMPT,
    TECHNICAL_PROPOSAL_OUTLINE_PROMPT,
    TECHNICAL_PROPOSAL_SECTION_PROMPT
)

# 加载环境变量
load_dotenv()


class ClaudeService:
    """
    AI 服务封装（支持多种AI模型）

    注意：虽然叫ClaudeService，但实际支持OpenAI、Claude等多种模型
    为了保持向后兼容，类名不变
    """

    def __init__(self, provider: Optional[AIProvider] = None):
        """
        初始化 AI 服务

        Args:
            provider: AI Provider实例，如果不提供则从环境变量自动选择
        """
        if provider:
            self.provider = provider
        else:
            # 从环境变量自动选择provider
            self.provider = get_ai_provider()

    def analyze_bidding_document(self, document_contents: Dict[str, str]) -> str:
        """
        分析标书文件

        Args:
            document_contents: 字典，键为文件类型（如"PDF规范"），值为文件内容

        Returns:
            分析报告文本
        """
        # 构建提示词
        prompt = self._build_analysis_prompt(document_contents)

        # 调用 AI Provider
        return self.provider.generate(prompt, max_tokens=8000, temperature=0.3)

    def generate_bidding_response(
        self,
        analysis_report: str,
        document_contents: Dict[str, str],
        requirements: Optional[str] = None
    ) -> str:
        """
        生成投标文件

        Args:
            analysis_report: 之前生成的分析报告
            document_contents: 原始标书内容
            requirements: 额外的生成要求

        Returns:
            生成的投标文件内容
        """
        prompt = self._build_generation_prompt(
            analysis_report,
            document_contents,
            requirements
        )

        # 调用 AI Provider
        return self.provider.generate(prompt, max_tokens=8000, temperature=0.5)

    def _build_analysis_prompt(self, document_contents: Dict[str, str]) -> str:
        """构建标书分析提示词"""
        prompt_parts = [
            "你是一位资深的工程类标书审查专家。请仔细分析以下标书文件，并生成详细的审查报告。\n",
            "=== 标书文件内容 ===\n"
        ]

        # 添加各个文件的内容
        for file_type, content in document_contents.items():
            if content and content.strip():
                prompt_parts.append(f"\n【{file_type}】\n{content}\n")

        prompt_parts.append("""
=== 审查要求 ===

请从以下几个方面进行深入分析：

1. **项目概况总结**
   - 项目名称、规模、预算
   - 关键时间节点
   - 项目目标和范围

2. **技术要求分析**
   - 技术规范摘要
   - 关键技术指标
   - 特殊技术要求

3. **商务条款解读**
   - 投标保证金
   - 付款方式和进度
   - 履约保证金
   - 质保期要求

4. **资质要求清单**
   - 企业资质要求
   - 人员资格要求
   - 业绩要求

5. **风险点识别**
   - 技术风险
   - 商务风险
   - 合规风险
   - 时间风险

6. **重点关注事项**
   - 容易遗漏的要求
   - 特别强调的条款
   - 评分权重分析

7. **投标建议**
   - 应对策略建议
   - 需要准备的材料
   - 注意事项

请以结构化、清晰的方式呈现报告，确保覆盖所有关键信息。
""")

        return "".join(prompt_parts)

    def _build_generation_prompt(
        self,
        analysis_report: str,
        document_contents: Dict[str, str],
        requirements: Optional[str]
    ) -> str:
        """构建投标文件生成提示词"""
        prompt_parts = [
            "你是一位经验丰富的投标文件编写专家。基于以下标书分析报告和原始标书文件，请生成一份专业的投标响应文件。\n",
            "=== 标书分析报告 ===\n",
            analysis_report,
            "\n\n=== 原始标书要点 ===\n"
        ]

        # 添加简要的标书内容
        for file_type, content in document_contents.items():
            if content and content.strip():
                # 只添加前2000字符，避免太长
                truncated = content[:2000] + "..." if len(content) > 2000 else content
                prompt_parts.append(f"\n【{file_type}】\n{truncated}\n")

        if requirements:
            prompt_parts.append(f"\n=== 特殊要求 ===\n{requirements}\n")

        prompt_parts.append("""
=== 生成要求 ===

请生成一份包含以下内容的投标响应文件：

1. **技术方案响应**
   - 针对招标文件技术要求的逐条响应
   - 技术实施方案
   - 项目组织架构
   - 进度计划

2. **商务条款响应**
   - 商务条款逐条确认
   - 偏离说明（如有）
   - 服务承诺

3. **资质证明材料清单**
   - 需要提供的资质文件列表
   - 业绩证明材料

4. **质量保证措施**
   - 质量管理体系
   - 质量控制措施

5. **售后服务方案**
   - 服务内容
   - 响应时间承诺

请生成专业、规范的投标文件，确保：
- 完全响应招标要求
- 突出我方优势
- 语言专业、格式规范
- 无遗漏关键要求
""")

        return "".join(prompt_parts)

    def parse_bidding_document_structured(self, document_contents: Dict[str, str]) -> str:
        """
        结构化解析招标文件（7类分析）- 支持大文档自动压缩

        Args:
            document_contents: 文件内容字典

        Returns:
            结构化解析报告
        """
        # 合并所有文件内容
        combined_content = []
        for file_type, content in document_contents.items():
            if content and content.strip():
                combined_content.append(f"\n【{file_type}】\n{content}\n")

        document_text = "\n".join(combined_content)

        # 估算token数
        total_tokens = TextProcessor.estimate_tokens(document_text)
        print(f"[AI Service] 文档总token数: {total_tokens:,}")

        # 从环境变量读取配置
        compression_ratio = float(os.getenv('COMPRESSION_RATIO', '1.0'))

        print(f"[AI Service] 压缩率设置: {compression_ratio}")

        # 仅按照用户设置的压缩率处理，不自动判断
        if compression_ratio < 1.0:
            # 计算目标token数
            target_tokens = int(total_tokens * compression_ratio)

            print(f"[AI Service] 开始智能压缩 ({total_tokens:,} → {target_tokens:,} tokens)")

            # 压缩策略：保留关键信息（标题、要求、数值等）
            compressed_text = ContentCompressor.compress_for_analysis(
                document_text,
                target_ratio=compression_ratio
            )

            document_text = compressed_text
            final_tokens = TextProcessor.estimate_tokens(document_text)
            actual_ratio = final_tokens / total_tokens
            print(f"[AI Service] 压缩完成: {final_tokens:,} tokens，实际压缩率: {actual_ratio*100:.1f}%")
        else:
            print(f"[AI Service] 不压缩（COMPRESSION_RATIO=1.0）")

        # 使用新的解析提示词
        prompt = BIDDING_DOCUMENT_ANALYSIS_PROMPT.format(
            document_content=document_text
        )

        # 调用 AI Provider
        return self.provider.generate(prompt, max_tokens=16000, temperature=0.2)

    def extract_evaluation_criteria(self, analysis_report: str) -> str:
        """
        从解析报告中提取评审标准

        Args:
            analysis_report: 招标文件解析报告

        Returns:
            评审标准总结
        """
        prompt = EVALUATION_CRITERIA_EXTRACTION_PROMPT.format(
            analysis_report=analysis_report
        )

        # 调用 AI Provider
        return self.provider.generate(prompt, max_tokens=8000, temperature=0.3)

    def generate_technical_proposal_outline(
        self,
        project_requirements: str,
        evaluation_criteria: str
    ) -> Dict:
        """
        生成技术标目录结构

        Args:
            project_requirements: 项目需求
            evaluation_criteria: 评审标准

        Returns:
            目录结构（JSON格式）
        """
        prompt = TECHNICAL_PROPOSAL_OUTLINE_PROMPT.format(
            project_requirements=project_requirements,
            evaluation_criteria=evaluation_criteria
        )

        # 调用 AI Provider
        response_text = self.provider.generate(prompt, max_tokens=8000, temperature=0.4)

        # 尝试从响应中提取JSON
        try:
            # 尝试解析JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                return json.loads(json_text)
            else:
                # 如果没有代码块，尝试直接解析
                return {"outline": response_text, "raw": True}
        except:
            return {"outline": response_text, "raw": True}

    def generate_technical_proposal_section(
        self,
        section_title: str,
        word_count: int,
        section_requirements: str,
        project_info: str,
        evaluation_criteria: str
    ) -> str:
        """
        生成技术标的单个章节

        Args:
            section_title: 章节标题
            word_count: 建议字数
            section_requirements: 章节要求
            project_info: 项目基本信息
            evaluation_criteria: 评审标准

        Returns:
            章节内容
        """
        prompt = TECHNICAL_PROPOSAL_SECTION_PROMPT.format(
            section_title=section_title,
            word_count=word_count,
            section_requirements=section_requirements,
            project_info=project_info,
            evaluation_criteria=evaluation_criteria
        )

        # 调用 AI Provider
        return self.provider.generate(prompt, max_tokens=8000, temperature=0.5)

    def chat(self, message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        通用对话接口

        Args:
            message: 用户消息
            conversation_history: 对话历史，格式为 [{"role": "user/assistant", "content": "..."}]

        Returns:
            AI 回复
        """
        # chat方法暂不支持provider（需要conversation_history）
        # 如果需要使用，请直接调用Claude或OpenAI的原生接口
        raise NotImplementedError("chat方法暂不支持多provider，请使用parse或generate方法")

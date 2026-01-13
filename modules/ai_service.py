"""
AI 服务模块
封装 Claude API 调用
"""

import anthropic
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ClaudeService:
    """Claude AI 服务封装"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Claude 服务

        Args:
            api_key: API密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("未找到 ANTHROPIC_API_KEY，请在 .env 文件中配置")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # 使用最新的 Sonnet 模型

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

        # 调用 Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text

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

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0.5,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text

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

    def chat(self, message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        通用对话接口

        Args:
            message: 用户消息
            conversation_history: 对话历史，格式为 [{"role": "user/assistant", "content": "..."}]

        Returns:
            AI 回复
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=messages
        )

        return response.content[0].text

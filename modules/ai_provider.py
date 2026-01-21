"""
AI Provider 抽象层
支持多种AI模型：OpenAI GPT-4o、Claude等
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AIProvider:
    """AI Provider基类"""

    def generate(self, prompt: str, max_tokens: int = 8000, temperature: float = 0.3) -> str:
        """生成文本"""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4 Provider（支持OpenRouter等第三方平台）"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请先安装openai: pip install openai")

        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY，请在 .env 文件中配置")

        # 支持自定义base_url（如OpenRouter、国内镜像等）
        base_url = os.getenv('OPENAI_BASE_URL')
        if base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=self.api_key)

        # 从环境变量读取模型
        # 注意：OpenRouter的模型格式是 "openai/gpt-4o-mini"
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')

        print(f"[AI Provider] 使用OpenAI - 模型: {self.model}")
        if base_url:
            print(f"[AI Provider] API端点: {base_url}")

    def generate(self, prompt: str, max_tokens: int = 8000, temperature: float = 0.3) -> str:
        """调用OpenAI API生成文本"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content


class ClaudeProvider(AIProvider):
    """Claude (Anthropic) Provider"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            import anthropic
        except ImportError:
            raise ImportError("请先安装anthropic: pip install anthropic")

        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("未找到 ANTHROPIC_API_KEY，请在 .env 文件中配置")

        # 支持OpenRouter或其他代理
        base_url = os.getenv('ANTHROPIC_BASE_URL')
        if base_url:
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=base_url
            )
            self.model = os.getenv('ANTHROPIC_MODEL', 'anthropic/claude-sonnet-4')
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')

        print(f"[AI Provider] 使用Claude - 模型: {self.model}")
        if base_url:
            print(f"[AI Provider] API端点: {base_url}")

    def generate(self, prompt: str, max_tokens: int = 8000, temperature: float = 0.3) -> str:
        """调用Claude API生成文本"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text


def get_ai_provider() -> AIProvider:
    """
    根据环境变量选择AI Provider

    环境变量配置：
    AI_PROVIDER=openai    → 使用OpenAI GPT-4o
    AI_PROVIDER=claude    → 使用Claude（默认）
    """
    provider_type = os.getenv('AI_PROVIDER', 'claude').lower()

    if provider_type == 'openai':
        return OpenAIProvider()
    elif provider_type == 'claude':
        return ClaudeProvider()
    else:
        raise ValueError(f"不支持的AI Provider: {provider_type}，请设置为 'openai' 或 'claude'")

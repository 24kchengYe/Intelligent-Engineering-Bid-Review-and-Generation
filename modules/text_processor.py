"""
文本处理模块
智能分批、token计数、内容压缩
"""

import re
from typing import List, Dict


class TextProcessor:
    """文本处理器"""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        估算文本的token数量

        简化算法：
        - 中文：1字符 ≈ 1.5 tokens
        - 英文：1单词 ≈ 1.3 tokens
        """
        if not text:
            return 0

        # 统计中文字符数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # 统计英文单词数
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        # 其他字符（数字、符号等）
        other_chars = len(text) - chinese_chars - english_words

        # 估算token数
        tokens = int(chinese_chars * 1.5 + english_words * 1.3 + other_chars * 0.5)
        return tokens

    @staticmethod
    def smart_truncate(text: str, max_tokens: int, keep_structure: bool = True) -> str:
        """
        智能截断文本，保留结构和重要信息

        Args:
            text: 原始文本
            max_tokens: 最大token数
            keep_structure: 是否保持文档结构（章节标题等）

        Returns:
            截断后的文本
        """
        current_tokens = TextProcessor.estimate_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # 计算截断比例
        ratio = max_tokens / current_tokens

        if keep_structure:
            # 保持结构：提取标题和重要内容
            return TextProcessor._structured_truncate(text, ratio)
        else:
            # 简单截断：头 + 尾
            return TextProcessor._simple_truncate(text, max_tokens)

    @staticmethod
    def _structured_truncate(text: str, ratio: float) -> str:
        """结构化截断（保留标题和章节）"""
        lines = text.split('\n')
        result = []
        current_tokens = 0
        target_tokens = int(TextProcessor.estimate_tokens(text) * ratio)

        # 标题模式
        title_patterns = [
            r'^#{1,6}\s+',  # Markdown标题
            r'^第[一二三四五六七八九十百\d]+[章节条]',  # 第X章
            r'^\d+\.\d+',  # 1.1
            r'^【.*】',  # 【文件类型】
            r'^==',  # 分隔线
        ]

        for line in lines:
            # 检查是否是标题
            is_title = any(re.match(pattern, line.strip()) for pattern in title_patterns)

            line_tokens = TextProcessor.estimate_tokens(line)

            # 标题总是保留
            if is_title:
                result.append(line)
                current_tokens += line_tokens
            # 内容根据剩余空间决定
            elif current_tokens + line_tokens <= target_tokens:
                result.append(line)
                current_tokens += line_tokens
            # 超出限制，添加省略标记
            elif current_tokens < target_tokens * 0.95:
                result.append("... (内容过长，已省略部分) ...")
                break

        return '\n'.join(result)

    @staticmethod
    def _simple_truncate(text: str, max_tokens: int) -> str:
        """简单截断（头 + 尾）"""
        current_tokens = TextProcessor.estimate_tokens(text)

        if current_tokens <= max_tokens:
            return text

        # 计算字符截断位置（粗略估算）
        ratio = max_tokens / current_tokens
        head_chars = int(len(text) * ratio * 0.7)
        tail_chars = int(len(text) * ratio * 0.2)

        head = text[:head_chars]
        tail = text[-tail_chars:]

        return f"{head}\n\n... (内容过长，已省略中间部分) ...\n\n{tail}"

    @staticmethod
    def split_into_batches(
        document_contents: Dict[str, str],
        max_tokens_per_batch: int = 60000
    ) -> List[Dict[str, str]]:
        """
        将文档内容分批，每批不超过max_tokens

        Args:
            document_contents: {文件类型: 内容} 字典
            max_tokens_per_batch: 每批最大token数

        Returns:
            批次列表 [{文件类型: 内容}, ...]
        """
        batches = []
        current_batch = {}
        current_tokens = 0

        for file_type, content in document_contents.items():
            file_tokens = TextProcessor.estimate_tokens(content)

            # 单个文件超过限制，需要截断
            if file_tokens > max_tokens_per_batch * 0.8:
                # 截断此文件
                truncated = TextProcessor.smart_truncate(
                    content,
                    int(max_tokens_per_batch * 0.8),
                    keep_structure=True
                )
                file_tokens = TextProcessor.estimate_tokens(truncated)
                content = truncated

            # 检查是否需要新批次
            if current_tokens + file_tokens > max_tokens_per_batch and current_batch:
                # 当前批次已满，保存并开始新批次
                batches.append(current_batch)
                current_batch = {}
                current_tokens = 0

            # 添加到当前批次
            current_batch[file_type] = content
            current_tokens += file_tokens

        # 添加最后一个批次
        if current_batch:
            batches.append(current_batch)

        return batches


class ContentCompressor:
    """内容压缩器（保留关键信息）"""

    @staticmethod
    def compress_for_analysis(text: str, target_ratio: float = 0.5) -> str:
        """
        压缩文本用于分析（保留关键信息）

        策略：
        1. 保留所有标题
        2. 保留包含数字/要求/标准的句子
        3. 删除重复内容
        4. 简化描述性段落
        """
        lines = text.split('\n')
        result = []
        seen_content = set()

        # 关键词模式
        important_patterns = [
            r'第[一二三四五六七八九十\d]+[章节条]',  # 章节
            r'\d+\.\d+',  # 编号
            r'[≥≤><]',  # 数值要求
            r'不得|必须|应当|应|禁止|要求',  # 强制性词汇
            r'GB|JGJ|CJJ|标准',  # 标准
            r'\d+%|\d+元|\d+天|\d+年',  # 数值
        ]

        for line in lines:
            line_stripped = line.strip()

            # 空行跳过
            if not line_stripped:
                continue

            # 标题和重要行保留
            is_important = any(re.search(pattern, line_stripped) for pattern in important_patterns)

            # 去重（相似内容只保留一次）
            content_hash = line_stripped[:50]  # 用前50字符做哈希

            if is_important or content_hash not in seen_content:
                result.append(line)
                seen_content.add(content_hash)

        compressed = '\n'.join(result)

        # 如果压缩后仍超出目标，进一步截断
        if TextProcessor.estimate_tokens(compressed) > TextProcessor.estimate_tokens(text) * target_ratio:
            compressed = TextProcessor.smart_truncate(
                compressed,
                int(TextProcessor.estimate_tokens(text) * target_ratio)
            )

        return compressed

"""
文档解析模块
支持 PDF、Word、Excel 等格式的文件解析
"""

import fitz  # PyMuPDF
from docx import Document
import openpyxl
import pandas as pd
from typing import Dict, Optional
import os


class DocumentParser:
    """文档解析器"""

    def __init__(self):
        self.supported_formats = {
            'pdf': self.parse_pdf,
            'docx': self.parse_word,
            'doc': self.parse_word,
            'xlsx': self.parse_excel,
            'xls': self.parse_excel
        }

    def parse(self, file_path: str) -> Dict[str, str]:
        """
        解析文档

        Args:
            file_path: 文件路径

        Returns:
            解析结果字典，包含 content（文本内容）和 metadata（元数据）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower().strip('.')

        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {file_ext}")

        # 调用对应的解析方法
        parser_func = self.supported_formats[file_ext]
        return parser_func(file_path)

    def parse_pdf(self, file_path: str) -> Dict[str, str]:
        """解析 PDF 文件"""
        try:
            doc = fitz.open(file_path)
            content = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    content.append(f"--- 第 {page_num + 1} 页 ---\n{text}")

            doc.close()

            return {
                'content': '\n\n'.join(content),
                'metadata': {
                    'type': 'PDF',
                    'pages': len(doc),
                    'file_name': os.path.basename(file_path)
                }
            }
        except Exception as e:
            return {
                'content': '',
                'metadata': {'type': 'PDF', 'error': str(e)}
            }

    def parse_word(self, file_path: str) -> Dict[str, str]:
        """解析 Word 文件"""
        try:
            doc = Document(file_path)
            content = []

            # 提取段落
            for para in doc.paragraphs:
                if para.text.strip():
                    content.append(para.text)

            # 提取表格
            if doc.tables:
                content.append("\n--- 表格内容 ---")
                for table_idx, table in enumerate(doc.tables):
                    content.append(f"\n表格 {table_idx + 1}:")
                    for row in table.rows:
                        row_data = [cell.text.strip() for cell in row.cells]
                        content.append(" | ".join(row_data))

            return {
                'content': '\n'.join(content),
                'metadata': {
                    'type': 'Word',
                    'paragraphs': len(doc.paragraphs),
                    'tables': len(doc.tables),
                    'file_name': os.path.basename(file_path)
                }
            }
        except Exception as e:
            return {
                'content': '',
                'metadata': {'type': 'Word', 'error': str(e)}
            }

    def parse_excel(self, file_path: str) -> Dict[str, str]:
        """解析 Excel 文件（支持多sheet、中英文混合）"""
        try:
            # 使用 pandas 读取，支持多个工作表
            # engine='openpyxl' 支持 .xlsx, engine='xlrd' 支持 .xls
            file_ext = os.path.splitext(file_path)[1].lower()
            engine = 'openpyxl' if file_ext == '.xlsx' else 'xlrd'

            excel_file = pd.ExcelFile(file_path, engine=engine)
            content = []
            total_rows = 0

            for sheet_name in excel_file.sheet_names:
                # 读取时保持字符串格式，避免数字转换问题
                df = pd.read_excel(
                    excel_file,
                    sheet_name=sheet_name,
                    dtype=str,  # 保持原始字符串格式
                    na_filter=False  # 不将空值转为 NaN
                )

                content.append(f"\n{'='*50}")
                content.append(f"工作表: {sheet_name}")
                content.append(f"{'='*50}")

                # 转换为文本格式
                if not df.empty:
                    # 使用 to_string 保持表格格式，支持中英文对齐
                    content.append(df.to_string(index=False, max_colwidth=100))
                    total_rows += len(df)
                else:
                    content.append("(空表)")

            return {
                'content': '\n'.join(content),
                'metadata': {
                    'type': 'Excel',
                    'sheets': len(excel_file.sheet_names),
                    'sheet_names': excel_file.sheet_names,
                    'total_rows': total_rows,
                    'file_name': os.path.basename(file_path)
                }
            }
        except Exception as e:
            return {
                'content': '',
                'metadata': {'type': 'Excel', 'error': str(e)}
            }


def extract_text_from_file(file_path: str) -> str:
    """
    便捷函数：从文件提取文本

    Args:
        file_path: 文件路径

    Returns:
        提取的文本内容
    """
    parser = DocumentParser()
    result = parser.parse(file_path)
    return result.get('content', '')

"""
国家/地方标准文件管理模块
负责国标文件的上传、存储和检索
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .document_parser import DocumentParser

Base = declarative_base()


class StandardDocument(Base):
    """国标文件数据模型"""
    __tablename__ = 'standard_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    standard_code = Column(String(100), unique=True, nullable=False)  # 如: GB50500-2013
    standard_name = Column(String(500), nullable=False)  # 标准名称
    file_name = Column(String(500), nullable=False)  # 原始文件名
    file_path = Column(String(1000), nullable=False)  # 存储路径
    file_hash = Column(String(64), nullable=False)  # 文件哈希（防重复）
    file_size = Column(Integer)  # 文件大小（字节）
    category = Column(String(100))  # 分类：国标/行标/地标
    content_preview = Column(Text)  # 内容预览（前500字）
    upload_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        """转为字典"""
        return {
            'id': self.id,
            'standard_code': self.standard_code,
            'standard_name': self.standard_name,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'category': self.category,
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M:%S') if self.upload_time else '',
            'content_preview': self.content_preview[:200] + '...' if self.content_preview and len(self.content_preview) > 200 else self.content_preview
        }


class StandardsManager:
    """国标文件管理器"""

    def __init__(self, db_path='data/standards.db', storage_path='data/standards'):
        """
        Args:
            db_path: 数据库路径
            storage_path: 文件存储路径
        """
        self.db_path = db_path
        self.storage_path = storage_path

        # 创建目录
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(storage_path, exist_ok=True)

        # 初始化数据库
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # 文档解析器
        self.parser = DocumentParser(enable_ocr=True)

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件SHA256哈希"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _extract_standard_code(self, file_name: str, content: str) -> Optional[str]:
        """从文件名或内容中提取标准编号"""
        import re

        # 常见标准编号模式
        patterns = [
            r'GB[\/T]?\s*\d+[-—]\d{4}',  # GB/T 50500-2013
            r'GB\s*\d+',  # GB 50500
            r'JGJ\s*\d+[-—]\d{4}',  # JGJ 59-2011
            r'CJJ\s*\d+[-—]\d{4}',  # CJJ 1-2008
            r'JTG\s*[A-Z]\d+[-—]\d{4}',  # JTG D50-2017
            r'DB\d{2}[\/T]?\s*\d+[-—]\d{4}',  # DB11/T 695-2009
        ]

        # 先从文件名提取
        for pattern in patterns:
            match = re.search(pattern, file_name, re.IGNORECASE)
            if match:
                return match.group(0).replace('/', '/').replace('—', '-')

        # 再从内容前1000字符提取
        if content:
            content_head = content[:1000]
            for pattern in patterns:
                match = re.search(pattern, content_head, re.IGNORECASE)
                if match:
                    return match.group(0).replace('/', '/').replace('—', '-')

        return None

    def _categorize_standard(self, standard_code: str) -> str:
        """分类标准"""
        if not standard_code:
            return '其他'

        code_upper = standard_code.upper()
        if code_upper.startswith('GB'):
            return '国家标准'
        elif code_upper.startswith('JGJ') or code_upper.startswith('JTG'):
            return '行业标准'
        elif code_upper.startswith('CJJ'):
            return '行业标准'
        elif code_upper.startswith('DB'):
            return '地方标准'
        else:
            return '其他'

    def add_standard(self, uploaded_file, standard_name: str = None) -> Dict:
        """
        添加国标文件

        Args:
            uploaded_file: Streamlit上传的文件对象
            standard_name: 标准名称（可选，如果为空则从文件名提取）

        Returns:
            {'success': bool, 'message': str, 'data': dict}
        """
        try:
            # 获取文件信息
            file_name = uploaded_file.name
            file_size = uploaded_file.size

            # 保存临时文件
            temp_path = os.path.join(self.storage_path, f"temp_{file_name}")
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            # 计算文件哈希
            file_hash = self._calculate_file_hash(temp_path)

            # 检查是否已存在
            session = self.Session()
            existing = session.query(StandardDocument).filter_by(file_hash=file_hash).first()
            if existing:
                session.close()
                os.remove(temp_path)
                return {
                    'success': False,
                    'message': f'文件已存在: {existing.standard_code} - {existing.standard_name}'
                }

            # 解析文件内容
            parsed = self.parser.parse(temp_path)
            content = parsed.get('content', '')
            content_preview = content[:500] if content else ''

            # 提取标准编号
            standard_code = self._extract_standard_code(file_name, content)
            if not standard_code:
                # 使用文件名作为编号
                standard_code = os.path.splitext(file_name)[0]

            # 检查编号是否重复
            existing_code = session.query(StandardDocument).filter_by(standard_code=standard_code).first()
            if existing_code:
                session.close()
                os.remove(temp_path)
                return {
                    'success': False,
                    'message': f'标准编号已存在: {standard_code}'
                }

            # 确定标准名称
            if not standard_name:
                standard_name = os.path.splitext(file_name)[0]

            # 确定分类
            category = self._categorize_standard(standard_code)

            # 重命名文件（使用标准编号）
            safe_code = standard_code.replace('/', '_').replace('\\', '_')
            file_ext = os.path.splitext(file_name)[1]
            final_name = f"{safe_code}{file_ext}"
            final_path = os.path.join(self.storage_path, final_name)

            # 移动文件
            os.rename(temp_path, final_path)

            # 保存到数据库
            standard = StandardDocument(
                standard_code=standard_code,
                standard_name=standard_name,
                file_name=file_name,
                file_path=final_path,
                file_hash=file_hash,
                file_size=file_size,
                category=category,
                content_preview=content_preview
            )
            session.add(standard)
            session.commit()

            result = standard.to_dict()
            session.close()

            return {
                'success': True,
                'message': f'国标文件添加成功: {standard_code}',
                'data': result
            }

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return {
                'success': False,
                'message': f'添加失败: {str(e)}'
            }

    def get_all_standards(self, category: str = None) -> List[Dict]:
        """获取所有国标文件"""
        session = self.Session()
        query = session.query(StandardDocument)

        if category and category != '全部':
            query = query.filter_by(category=category)

        query = query.order_by(StandardDocument.upload_time.desc())
        standards = query.all()
        result = [s.to_dict() for s in standards]
        session.close()
        return result

    def get_standard_by_id(self, standard_id: int) -> Optional[Dict]:
        """根据ID获取国标文件"""
        session = self.Session()
        standard = session.query(StandardDocument).filter_by(id=standard_id).first()
        result = standard.to_dict() if standard else None
        session.close()
        return result

    def get_standard_content(self, standard_id: int) -> str:
        """获取国标文件完整内容"""
        session = self.Session()
        standard = session.query(StandardDocument).filter_by(id=standard_id).first()

        if not standard:
            session.close()
            return ""

        # 重新解析文件获取完整内容
        if os.path.exists(standard.file_path):
            parsed = self.parser.parse(standard.file_path)
            content = parsed.get('content', '')
        else:
            content = ""

        session.close()
        return content

    def delete_standard(self, standard_id: int) -> Dict:
        """删除国标文件"""
        session = self.Session()
        try:
            standard = session.query(StandardDocument).filter_by(id=standard_id).first()

            if not standard:
                return {'success': False, 'message': '文件不存在'}

            # 删除物理文件
            if os.path.exists(standard.file_path):
                os.remove(standard.file_path)

            # 删除数据库记录
            session.delete(standard)
            session.commit()
            session.close()

            return {'success': True, 'message': '删除成功'}

        except Exception as e:
            session.rollback()
            session.close()
            return {'success': False, 'message': f'删除失败: {str(e)}'}

    def search_standards(self, keyword: str) -> List[Dict]:
        """搜索国标文件"""
        session = self.Session()
        query = session.query(StandardDocument).filter(
            (StandardDocument.standard_code.like(f'%{keyword}%')) |
            (StandardDocument.standard_name.like(f'%{keyword}%'))
        ).order_by(StandardDocument.upload_time.desc())

        standards = query.all()
        result = [s.to_dict() for s in standards]
        session.close()
        return result

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        session = self.Session()

        total = session.query(StandardDocument).count()
        by_category = {}

        categories = ['国家标准', '行业标准', '地方标准', '其他']
        for cat in categories:
            count = session.query(StandardDocument).filter_by(category=cat).count()
            by_category[cat] = count

        session.close()

        return {
            'total': total,
            'by_category': by_category
        }

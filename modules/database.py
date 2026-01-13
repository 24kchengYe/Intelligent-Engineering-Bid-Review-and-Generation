"""
数据库模块
管理标书审查历史记录
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import json

Base = declarative_base()


class BiddingRecord(Base):
    """标书审查记录表"""
    __tablename__ = 'bidding_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(200))  # 项目名称
    create_time = Column(DateTime, default=datetime.now)  # 创建时间
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    # 文件信息（JSON 格式存储）
    uploaded_files = Column(Text)  # {"PDF规范": "file1.pdf", "Word方案": "file2.docx"}

    # 分析报告
    analysis_report = Column(Text)

    # 投标文件
    bidding_response = Column(Text)

    # 状态：draft(草稿), analyzed(已分析), completed(已完成)
    status = Column(String(20), default='draft')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'project_name': self.project_name,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'uploaded_files': json.loads(self.uploaded_files) if self.uploaded_files else {},
            'analysis_report': self.analysis_report,
            'bidding_response': self.bidding_response,
            'status': self.status
        }


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = 'data/bidding_system.db'):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径
        """
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 创建数据库引擎
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)

        # 创建所有表
        Base.metadata.create_all(self.engine)

        # 创建会话
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_record(
        self,
        project_name: str,
        uploaded_files: dict = None
    ) -> BiddingRecord:
        """
        创建新记录

        Args:
            project_name: 项目名称
            uploaded_files: 上传的文件信息

        Returns:
            创建的记录对象
        """
        record = BiddingRecord(
            project_name=project_name,
            uploaded_files=json.dumps(uploaded_files or {}, ensure_ascii=False)
        )
        self.session.add(record)
        self.session.commit()
        return record

    def update_record(
        self,
        record_id: int,
        **kwargs
    ) -> BiddingRecord:
        """
        更新记录

        Args:
            record_id: 记录ID
            **kwargs: 要更新的字段

        Returns:
            更新后的记录
        """
        record = self.session.query(BiddingRecord).filter_by(id=record_id).first()
        if not record:
            raise ValueError(f"记录不存在: {record_id}")

        # 特殊处理 uploaded_files
        if 'uploaded_files' in kwargs and isinstance(kwargs['uploaded_files'], dict):
            kwargs['uploaded_files'] = json.dumps(kwargs['uploaded_files'], ensure_ascii=False)

        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)

        record.update_time = datetime.now()
        self.session.commit()
        return record

    def get_record(self, record_id: int) -> BiddingRecord:
        """获取单条记录"""
        return self.session.query(BiddingRecord).filter_by(id=record_id).first()

    def get_all_records(self, limit: int = 50) -> list:
        """
        获取所有记录

        Args:
            limit: 最多返回的记录数

        Returns:
            记录列表
        """
        return self.session.query(BiddingRecord)\
            .order_by(BiddingRecord.update_time.desc())\
            .limit(limit)\
            .all()

    def delete_record(self, record_id: int):
        """删除记录"""
        record = self.get_record(record_id)
        if record:
            self.session.delete(record)
            self.session.commit()

    def search_records(self, keyword: str) -> list:
        """
        搜索记录

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的记录列表
        """
        return self.session.query(BiddingRecord)\
            .filter(BiddingRecord.project_name.like(f'%{keyword}%'))\
            .order_by(BiddingRecord.update_time.desc())\
            .all()

    def close(self):
        """关闭数据库连接"""
        self.session.close()

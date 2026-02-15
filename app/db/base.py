from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """공통 속성과 테이블 이름 자동 생성을 위한 베이스 클래스"""
    id = Column(Integer, primary_key=True, index=True)  # 기본 키
    created_at = Column(DateTime, default=func.now(), nullable=False)  # 생성 시간
    updated_at = Column(DateTime, default=func.now(),
                        onupdate=func.now(), nullable=False)  # 업데이트 시간

    @declared_attr
    def __tablename__(cls) -> str:
        """테이블 이름 자동 생성 (클래스 이름을 소문자로 사용)"""
        return cls.__name__.lower()

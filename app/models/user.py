from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    # 기본 필드
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    profile_pic = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # 사용자 타입 (google, apple, guest 등)
    provider = Column(String, nullable=False, default="google")
    provider_id = Column(String, nullable=True)  # OAuth provider's user ID

    # 관계 설정
    tokens = relationship("Token", back_populates="user")
    ideas = relationship("StartupIdea", back_populates="user")
    consulting_sessions = relationship("ConsultingSession", back_populates="user")

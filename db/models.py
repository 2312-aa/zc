"""SQLAlchemy 模型定义：用户、会话、消息"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    crisis = "crisis"


class User(Base):
    """用户档案表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), unique=True, nullable=False, index=True, comment="外部用户标识")
    nickname = Column(String(128), nullable=True, comment="昵称")
    age = Column(Integer, nullable=True, comment="年龄")
    gender = Column(String(16), nullable=True, comment="性别")
    risk_level = Column(String(16), default="low", comment="当前风险等级")
    created_at = Column(DateTime, default=datetime.utcnow, comment="注册时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, risk_level={self.risk_level})>"


class Conversation(Base):
    """会话表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(64), unique=True, nullable=False, index=True, comment="会话ID")
    user_id = Column(String(64), ForeignKey("users.user_id"), nullable=False, comment="用户ID")
    title = Column(String(256), nullable=True, comment="会话标题")
    agent_route = Column(String(64), nullable=True, comment="路由到的智能体")
    risk_level = Column(String(16), default="low", comment="本次会话风险等级")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.conversation_id}, agent={self.agent_route})>"


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(64), ForeignKey("conversations.conversation_id"), nullable=False, index=True)
    role = Column(String(32), nullable=False, comment="角色: user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    agent_name = Column(String(64), nullable=True, comment="生成该消息的智能体")
    risk_score = Column(Float, nullable=True, comment="风险评分 0-1")
    created_at = Column(DateTime, default=datetime.utcnow, comment="消息时间")

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, agent={self.agent_name})>"

from datetime import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(128), nullable=True)
    name = Column(String(256), nullable=True)
    user_type = Column(String(16), nullable=True)  # "individual" | "legal"
    company_name = Column(String(256), nullable=True)
    phone_no = Column(String(32), nullable=True)
    region = Column(String(256), nullable=True)
    district = Column(String(256), nullable=True)
    address_detail = Column(Text, nullable=True)
    account_number = Column(String(64), nullable=True)
    lang_code = Column(String(8), nullable=True, default="uz")
    is_registered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    requests = relationship("Request", back_populates="user")


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_text = Column(Text, nullable=False)
    request_category = Column(String(64), nullable=True)  # ← new
    request_type = Column(String(64), nullable=True)  # ← new
    admin_message_id = Column(BigInteger, nullable=True)
    admin_chat_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_replied = Column(Boolean, default=False)

    user = relationship("User", back_populates="requests")

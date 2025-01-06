from database import Base

from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = 'Users'
    
    u_id: Mapped[int] = mapped_column(String(36), primary_key=True, autoincrement=True)
    u_name: Mapped[str] = mapped_column(String(32), nullable=False)
    u_email: Mapped[str] = mapped_column(String(64), nullable=False)
    u_password: Mapped[str] = mapped_column(String(64), nullable=True)
    u_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    u_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

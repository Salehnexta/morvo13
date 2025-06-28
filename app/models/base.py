from datetime import datetime

from sqlalchemy import Column, DateTime

from app.models import Base


class TimestampedBase(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

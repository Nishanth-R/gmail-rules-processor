from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    message_id = Column(String, unique=True)
    thread_id = Column(String)
    from_address = Column(String)
    to_address = Column(String)
    subject = Column(String)
    received_date = Column(String)
    body = Column(String)
    is_read = Column(Boolean, default=False)
    label_ids = Column(String)
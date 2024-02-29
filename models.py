from sqlalchemy import BigInteger, Column, Date, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class St_Accounts(Base):
    __tablename__ = 'st_accounts'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(350), nullable=False)
    email = Column(String(100), nullable=False)
    room_no = Column(String(10), nullable=False)
    roll_no = Column(String(15), nullable=False)


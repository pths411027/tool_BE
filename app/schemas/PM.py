# for development
from sqlalchemy.orm import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, Date, Boolean, Float, JSON, TEXT, Index, ForeignKey



class MainProject(Base):
    __tablename__ = "main_project"
    pro_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String(255), primary_key=False, index=True)
    KYC = Column(String(255), index=False)
    des = Column(String(255), primary_key=False, index=False)
    start_day = Column(Date, index=False)
    end_day = Column(Date, index=False)
    tag = Column(String(255), index=False)

class SubProject(Base):
    __tablename__ = "sub_project"
    pro_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_pro_id = Column(Integer, ForeignKey('main_project.pro_id'), index=True)
    project_name = Column(String(255), primary_key=False, index=True)
    des = Column(String(255), primary_key=False, index=False)
    tag = Column(String(255), index=False)

class Member(Base):
    __tablename__ = "member"
    pro_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chineseName = Column(String(255), primary_key=False, index=False)
    englishName = Column(String(255), primary_key=False, index=False)
    email = Column(String(255), primary_key=False, index=False)
    department = Column(String(255), primary_key=False, index=False)
    team = Column(String(255), primary_key=False, index=False)
    level = Column(String(255), primary_key=False, index=False)
    manager = Column(String(255), primary_key=False, index=False)




   
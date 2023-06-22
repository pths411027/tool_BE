# for development
from sqlalchemy import Column, Integer, String, Date, Boolean, Float, JSON, TEXT, Index, ForeignKey, DateTime
from app.database.sqlite import Base


class MainProject(Base):
    __tablename__ = "WL_main_project"
    pro_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String(255), primary_key=False, index=True)
    KPI = Column(Integer, index=False)
    created_time = Column(DateTime, index=False)
    updated_time = Column(DateTime, index=False)
    team = Column(Integer, index=False)

class Option_Answer(Base):
    __tablename__ = "WL_optionn_ans"
    option_project = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, primary_key=True, index=True)
    option_name = Column(String(255), primary_key=False, index=True)
    option_revise = Column(Boolean, primary_key=False, index=False)
    option_color = Column(String(255), primary_key=False, index=False)

class Member(Base):
    __tablename__ = "WL_member"
    pro_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    englishName = Column(String(255), primary_key=True, index=False)
    email = Column(String(255), primary_key=False, index=False)
    team = Column(Integer, primary_key=False, index=False)
    level = Column(String(255), primary_key=False, index=False)

class Team(Base):
    __tablename__ = "WL_team"
    pro_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teamName = Column(String(255), primary_key=False, index=False)
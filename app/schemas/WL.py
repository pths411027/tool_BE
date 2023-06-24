# for development
from sqlalchemy import Column, Integer, String, Date, Boolean, Float, JSON, TEXT, Index, ForeignKey, DateTime
from app.database.sqlalchemy import Base

class WLMainProject(Base):
    __tablename__ = "WL_main_project"
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String(255), primary_key=False, index=True)
    KPI = Column(Integer, index=False)
    created_time = Column(DateTime, index=False)
    updated_time = Column(DateTime, index=False)
    team = Column(Integer, index=False)
    

class WLOption_Answer(Base):
    __tablename__ = "WL_optionn_ans"
    project_id = Column(Integer, primary_key=True, index=True)
    option_id = Column(Integer, primary_key=True, index=True)
    option_name = Column(String(255), primary_key=False, index=True)
    option_revise = Column(Boolean, primary_key=False, index=False)
    option_color = Column(String(255), primary_key=False, index=False)

class WLTeam(Base):
    __tablename__ = "WL_team"
    team_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teamName = Column(String(255), primary_key=False, index=False)


class WLMember(Base):
    __tablename__ = "WL_member"
    member_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    englishName = Column(String(255), index=False)
    email = Column(String(255), primary_key=False, index=False)
    team_id = Column(Integer, primary_key=False, index=False)
    level = Column(String(255), primary_key=False, index=False)

class WLFile(Base):
    __tablename__ = "WL_file"
    file_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(255), primary_key=False, index=False)
    created_time = Column(DateTime, primary_key=False, index=False)
    project_id = Column(Integer, primary_key=False, index=False)

class WLData(Base):
    __tablename__ = "WL_data"
    file_id =  Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer, primary_key=True, index=True)
    row_data = Column(String, primary_key=False, index=False)
    row_complete = Column(String, primary_key=False, index=False)
    row_customed = Column(String, primary_key=False, index=False)
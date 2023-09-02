# for development
from sqlalchemy import (
    JSON,
    TEXT,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
)

from app.database.sqlalchemy import Base


def normal_column(type_):
    return Column(type_, primary_key=False, index=False)


class WLMainProject(Base):
    __tablename__ = "WL_main_project"
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String(255), primary_key=False, index=True)
    KPI = Column(Integer, index=False)
    created_time = Column(Integer, index=False)
    updated_time = Column(Integer, index=False)
    team = Column(Integer, index=False)
    file_format = Column(String(255), index=False)
    distinct_col = Column(String(255), index=False)


class WLOption_Answer(Base):
    __tablename__ = "WL_optionn_ans"
    option_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, primary_key=False, index=False)
    # option_id = Column(Integer, primary_key=True, index=True)
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
    memberName = Column(String(255), index=False)
    memberPhoto = Column(String(255), index=False)
    email = Column(String(255), primary_key=False, index=False)
    team_id = Column(Integer, primary_key=False, index=False)
    level = Column(String(255), primary_key=False, index=False)


class WLFile(Base):
    __tablename__ = "WL_file"
    file_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(255), primary_key=False, index=False)
    created_time = Column(Integer, primary_key=False, index=False)
    project_id = Column(Integer, primary_key=False, index=False)
    file_type = Column(String(255), primary_key=False, index=False)
    file_extension = Column(String(255), primary_key=False, index=False)
    file_size = Column(Integer, primary_key=False, index=False)
    file_finish = Column(Boolean, primary_key=False, index=False)
    file_status = Column(Integer, primary_key=False, index=False)
    file_priority = Column(Integer, primary_key=False, index=False)
    # ＊file_status: 1: processing, 2: finish, 3: stop


class WLData(Base):
    __tablename__ = "WL_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = normal_column(Integer)
    row_id = normal_column(Integer)
    row_data = normal_column(String(255))
    row_complete = normal_column(String(255))
    row_customed = normal_column(String(255))
    row_completed = normal_column(Boolean)
    row_modify_time = normal_column(Integer)
    row_member_id = normal_column(Integer)
    row_distinct_detemine = normal_column(String(255))

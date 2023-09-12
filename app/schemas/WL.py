# for development
from sqlalchemy import Boolean, Column, Integer, String

from app.database.sqlalchemy import Base


def normal_column(type_):
    return Column(type_, primary_key=False, index=False)


class WLMainProject(Base):
    __tablename__ = "WL_main_project"
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = normal_column(String(255))
    project_kpi = normal_column(Integer)
    project_created_time = normal_column(Integer)
    project_updated_time = normal_column(Integer)
    team_id = normal_column(Integer)
    project_file_format = normal_column(String(255))
    project_distinct_col = normal_column(String(255))


class WLOption_Answer(Base):
    __tablename__ = "WL_optionn_ans"
    option_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = normal_column(Integer)
    option_name = normal_column(String(255))
    option_revise = normal_column(Boolean)
    option_color = normal_column(String(255))


class WLTeam(Base):
    __tablename__ = "WL_team"
    team_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_name = normal_column(String(255))


class WLMember(Base):
    __tablename__ = "WL_member"
    member_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_name = normal_column(String(255))
    member_password = normal_column(String(255))
    member_photo = normal_column(String(255))
    member_email = normal_column(String(255))
    team_id = normal_column(Integer)
    member_level = normal_column(String(255))


class WLFile(Base):
    __tablename__ = "WL_file"
    file_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = normal_column(String(255))
    file_created_time = normal_column(Integer)
    project_id = normal_column(Integer)
    file_type = normal_column(String(255))
    file_extension = normal_column(String(255))
    file_size = normal_column(Integer)
    file_finish = normal_column(Boolean)
    file_status = normal_column(Integer)
    file_priority = normal_column(Integer)
    # ＊file_status: 1: processing, 2: finish, 3: stop


class WLData(Base):
    __tablename__ = "WL_data"
    data_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = normal_column(Integer)
    row_id = normal_column(Integer)
    row_data = normal_column(String(255))
    row_complete = normal_column(Integer)
    row_customed = normal_column(String(255))
    row_completed = normal_column(Boolean)
    row_modify_time = normal_column(Integer)
    row_member_id = normal_column(Integer)
    row_distinct_detemine = normal_column(String(255))


class WLLog(Base):
    __tablename__ = "WL_log"
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_time = normal_column(Integer)
    project_id = normal_column(Integer)
    file_id = normal_column(Integer)
    memober_id = normal_column(Integer)
    data_id = normal_column(Integer)
    log_type = normal_column(Integer)
    # log_type: 1: ask, 2: submit, 3: onhold


class WLKPI(Base):
    __tablename__ = "WL_KPI"
    KPI_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_id = normal_column(Integer)
    KPI_start_time = normal_column(Integer)
    KPI_end_time = normal_column(Integer)
    KPI_content = normal_column(String(255))
    KPI_amount = normal_column(Integer)
    KPI_record_time = normal_column(Integer)

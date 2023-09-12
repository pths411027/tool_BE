# for development
from sqlalchemy import TEXT, Boolean, Column, Integer, String, Time

from app.database.sqlalchemy import Base


class DataSuiteTask(Base):
    __tablename__ = "DS_task"
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_name = Column(String(255), primary_key=False, index=True)
    task_url = Column(String(255), primary_key=False, index=False)
    task_sheet_name = Column(String(255), primary_key=False, index=False)
    task_start_cell = Column(String(255), primary_key=False, index=False)
    task_include_header = Column(Boolean, primary_key=False, index=False)
    task_query = Column(TEXT, primary_key=False, index=False)
    task_frequency = Column(String(255), primary_key=False, index=False)
    run_time = Column(Time, primary_key=False, index=False)


class DataSuiteWorkFlow(Base):
    __tablename__ = "DS_workflows"
    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    work_flow_name = Column(String(255), primary_key=False, index=True)
    work_flow_frequency = Column(String(255), primary_key=False, index=False)
    """
    頻率定義：
    1. daily: 'daily, 12'
    2. hourly: 'hourly, None'
    """
    last_run_time = Column(Integer, primary_key=False, index=False)
    last_run_status = Column(String(255), primary_key=False, index=False)
    last_modify_time = Column(Integer, primary_key=False, index=False)
    create_time = Column(Integer, primary_key=False, index=False)
    create_person = Column(String(255), primary_key=False, index=False)
    work_flow_subtask = Column(String(255), primary_key=False, index=False)
    work_flow_status = Column(String(255), primary_key=False, index=False)

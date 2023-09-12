from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine(
    "postgresql+psycopg2://postgres:abcd@db:5432/postgres",  # 根据你的docker-compose文件中的配置来填写
    pool_pre_ping=True,
    pool_recycle=300,
    echo=True,
)

# 创建会话工厂
Session = sessionmaker(bind=engine)


# 创建基类

Base = declarative_base()

# Importing models to ensure they are registered with Base.metadata
from app.schemas.WL import (
    WLMainProject,
    WLOption_Answer,
    WLTeam,
    WLMember,
    WLFile,
    WLData,
    WLLog,
)  # noqa

from app.schemas.DS import DataSuiteTask, DataSuiteWorkFlow  # noqa
from app.schemas.User import User  # noqa
from app.schemas.PM import MainProject, SubProject, Member  # noqa

Base.metadata.create_all(engine)

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

"""
engine = create_engine(
    'sqlite:///app/Side_Project.db',
    pool_pre_ping=True, 
    pool_recycle=300,
    echo=True
)
"""

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
from app.schemas.DS import DataSuiteTask
from app.schemas.PM import MainProject, Member, SubProject
from app.schemas.User import User
from app.schemas.WL import WLMainProject, WLMember, WLOption_Answer, WLTeam

Base.metadata.create_all(engine)

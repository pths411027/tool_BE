from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base



engine = create_engine(
    'sqlite:///Side_Project.db',
    pool_pre_ping=True, 
    pool_recycle=300,
    echo=True
)

# 创建会话工厂
Session = sessionmaker(bind=engine)

# 创建基类
Base = declarative_base()
from app.schemas.PM import MainProject, SubProject, Member
from app.schemas.WL import WLMainProject , WLOption_Answer, WLMember, WLTeam

Base.metadata.create_all(engine)

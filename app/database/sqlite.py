import sys
sys.path.append('/Users/marcus.tsai/Desktop/my-tool-BE')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.PM import Base
engine = create_engine(
    'sqlite:///PM.db',
    pool_pre_ping=True, 
    pool_recycle=300,
    echo=True
)
Base.metadata.create_all(engine)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
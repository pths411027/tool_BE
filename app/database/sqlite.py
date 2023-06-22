import sys
sys.path.append('/Users/marcus.tsai/Desktop/my-tool-BE')
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine(
    'sqlite:///Side_Project.db',
    pool_pre_ping=True, 
    pool_recycle=300,
    echo=True
)
Base.metadata.create_all(engine)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmarker

SQLALCHEMY_DATABASE_URL = ""

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmarker(autocommit=False, autoflush=False, bind=engine)
BaseModel = declarative_base()
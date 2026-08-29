from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.settings import settings


SQLALCHEMY_DATABASE_URL = settings.db_connection_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BaseModel = declarative_base()
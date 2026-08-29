from app.database import BaseModel

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import (
    Integer,
    String,
    DateTime,
    Numeric
)


class Fuel(BaseModel):

    __tablename__ = "fuels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    measure_unit = Column(String(50), nullable=False)
    date_added = Column(DateTime, nullable=False, server_default=func.now())
    date_updated = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class WeeklyPrice(BaseModel):

    __tablename__ = "weekly_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    week_start = Column(DateTime, nullable=False)
    week_end = Column(DateTime, nullable=False)
    year = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    fuel = relationship("Fuel")


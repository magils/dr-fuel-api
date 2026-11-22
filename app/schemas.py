from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List


class FuelResponse(BaseModel):
    id: Optional[int] = None
    name: str = Field(max_length=255)
    description: str = Field(max_length=512)
    code: str = Field(max_length=50)
    measure_unit: str = Field(max_length=50)
    date_added: Optional[datetime] = None
    date_updated: Optional[datetime] = None


class FuelListResponse(BaseModel):
    fuels: List[FuelResponse]


class WeeklyFuelDetail(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    code: str
    price: float


class WeeklyFuelBaseSchema(BaseModel):
    year: int
    week: int
    week_start: date
    week_end: date
    prices: List[WeeklyFuelDetail]


class WeeklyFuelRequest(WeeklyFuelBaseSchema):
    pass


class WeeklyFuelResponse(WeeklyFuelBaseSchema):
    pass

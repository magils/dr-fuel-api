from pydantic import BaseModel, Field
from datetime import datetime
from typing import  Optional

class FuelSchema(BaseModel):
    id: Optional[int] = None
    name: str = Field(max_length=255)
    description: str = Field(max_length=512)
    code: str = Field(max_length=50)
    measure_unit: str = Field(max_length=50)
    date_added: Optional[datetime] = None
    date_updated: Optional[datetime] = None
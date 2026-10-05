from fastapi import APIRouter
from app.schemas import FuelSchema
from app.services.fuel_service import (
    create_fuel,
    convert_to_fuel_schema
)

router = APIRouter()

@router.get("/fuel-types")
async def get_fuel_types():
    pass


@router.post("/fuel-types")
def add_fuel_type(fuel: FuelSchema):
    new_fuel = create_fuel(fuel)
    resp = convert_to_fuel_schema(new_fuel)
    return resp

from fastapi import APIRouter
from app.schemas import (
    FuelResponse,
    FuelListResponse,
    WeeklyFuelRequest,
    WeeklyFuelResponse,
)
from app.services.fuel_service import (
    create_fuel,
    convert_to_fuel_schema,
    get_fuels,
    create_fuel_weekly_prices,
)

router = APIRouter()


@router.get("/fuel-types", response_model=FuelListResponse)
async def get_fuel_types():
    return {"fuels": get_fuels()}


@router.post("/fuel-types")
async def add_fuel_type(fuel: FuelResponse):
    new_fuel = create_fuel(fuel)
    resp = convert_to_fuel_schema(new_fuel)
    return resp


@router.get("/prices/current")
async def current_prices():
    return {}


@router.post("/admin/prices", response_model=WeeklyFuelResponse)
async def add_fuel_weekly_prices(data: WeeklyFuelRequest):
    weekly_prices = create_fuel_weekly_prices(data)
    return weekly_prices

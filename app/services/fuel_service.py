from app.database import Session
from app.models import Fuel
from app.schemas import FuelSchema


def get_fuels():
    with Session() as s:
        result = s.query(Fuel).all()
        return result

def create_fuel(fuel_data):
    with Session() as s:
        fuel = Fuel(
            name = fuel_data.name,
            description = fuel_data.description,
            code = fuel_data.code,
            measure_unit=fuel_data.measure_unit,
        )
        s.add(fuel)
        s.commit()
        s.refresh(fuel)

        return fuel

def convert_to_fuel_schema(fuel_model):
    fuel_schema = FuelSchema(
        id = fuel_model.id,
        name = fuel_model.name,
        description = fuel_model.description,
        code = fuel_model.code,
        measure_unit= fuel_model.measure_unit
    )

    return fuel_schema
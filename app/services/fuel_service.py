from app.database import Session
from app.models import Fuel, WeeklyPrice
from app.schemas import FuelResponse
from app.errors import FuelNotFoundError
from sqlalchemy.orm import joinedload


def get_fuels():
    with Session() as s:
        result = s.query(Fuel).all()
        return result


def create_fuel(fuel_data):
    with Session() as s:
        fuel = Fuel(
            name=fuel_data.name,
            description=fuel_data.description,
            code=fuel_data.code,
            measure_unit=fuel_data.measure_unit,
        )
        s.add(fuel)
        s.commit()
        s.refresh(fuel)

        return fuel


def convert_to_fuel_schema(fuel_model):
    fuel_schema = FuelResponse(
        id=fuel_model.id,
        name=fuel_model.name,
        description=fuel_model.description,
        code=fuel_model.code,
        measure_unit=fuel_model.measure_unit,
    )

    return fuel_schema


def create_fuel_weekly_prices(weekly_price_data):
    with Session(expire_on_commit=False) as s:
        fuel_ids = {}
        created = []

        for fuel_price in weekly_price_data.prices:
            fuel = fuel_ids.get(fuel_price.code)

            if not fuel:
                fuel_code = fuel_price.code
                fuel = s.query(Fuel).filter(Fuel.code == fuel_code).one_or_none()

                if fuel is None:
                    s.rollback()
                    raise FuelNotFoundError(fuel_code)

                fuel_ids[fuel_code] = fuel

            wp = WeeklyPrice(
                year=weekly_price_data.year,
                week=weekly_price_data.week,
                week_start=weekly_price_data.week_start,
                week_end=weekly_price_data.week_end,
                fuel=fuel,
                price=fuel_price.price,
            )

            s.add(wp)
            created.append(wp)

        s.commit()

        weekly_price_data.prices = [
            {
                "id": wp.id,
                "name": wp.fuel.name,
                "code": wp.fuel.code,
                "price": wp.price,
            }
            for wp in created
        ]
        return weekly_price_data


def query_current_fuel_prices():
    with Session() as s:
        result = (
            s.query(WeeklyPrice)
            .options(joinedload(WeeklyPrice.fuel))
            .distinct(WeeklyPrice.fuel_id)
            .order_by(WeeklyPrice.fuel_id, WeeklyPrice.week_end.desc())
            .all()
        )
        return result


def get_current_fuel_prices():
    prices = query_current_fuel_prices()

    if not prices:
        return {}

    metadata = prices[0]

    return {
        "year": metadata.year,
        "week": metadata.week,
        "period_start": metadata.week_start,
        "period_end": metadata.week_end,
        "prices": prices,
    }

class FuelNotFoundError(Exception):
    def __init__(self, fuel_name):
        super().__init__(f"Fuel with code '{fuel_name}' not found")

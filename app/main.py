from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(title="Dominican Fuel Prices API")

app.include_router(api_router)
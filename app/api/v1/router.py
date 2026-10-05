from fastapi import APIRouter
from app.api.v1.endpoints.fuels import router as fuel_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(fuel_router)

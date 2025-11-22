# Main API router
# app/api/v1/router.py

from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/")
async def root():
    return {"message": "Welcome to Civi Chat API"}
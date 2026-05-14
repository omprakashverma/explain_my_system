from fastapi import APIRouter

from backend.app.api.routes import ask, files, health, notes, repository

api_router = APIRouter()
api_router.include_router(repository.router)
api_router.include_router(files.router)
api_router.include_router(ask.router)
api_router.include_router(notes.router)
api_router.include_router(health.router)

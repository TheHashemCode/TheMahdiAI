from fastapi import APIRouter

from app.api.v1.endpoints import admin, notebook

api_router = APIRouter()

api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(notebook.router, prefix="/admin/notebooks", tags=["notebooks"])

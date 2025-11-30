# app/api/__init__.py
from .health import router as health_router
app.include_router(health_router)

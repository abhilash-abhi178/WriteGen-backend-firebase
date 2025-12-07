"""WriteGen Backend - FastAPI Application.

Main entry point for the AI-powered handwriting document generator backend.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from app.api.routes import auth, samples, styles, generation, export, dashboard


from app.core.config import settings
from app.api import routes

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("=== WriteGen Backend Starting ===")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Device: {settings.device}")
    
    # Startup
    yield
    
    # Shutdown
    logger.info("=== WriteGen Backend Shutting Down ===")


# Create FastAPI app
app = FastAPI(
    title="WriteGen Backend API",
    description="AI-powered handwriting document generator",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url=f"/api/{settings.api_version}/openapi.json"
)

# Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "*.writegen.app"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check
@app.get("/api/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.env,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Include routers
app.include_router(
    routes.auth.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Authentication"]
)
app.include_router(
    routes.samples.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Samples"]
)
app.include_router(
    routes.styles.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Styles"]
)
app.include_router(
    routes.generation.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Generation"]
)
app.include_router(
    routes.export.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Export"]
)
app.include_router(
    routes.addons.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Add-ons"]
)
app.include_router(
    dashboard.router, prefix="/api")



# Root redirect
@app.get("/")
async def root():
    """API documentation redirect."""
    return {
        "message": "WriteGen API",
        "docs": "/api/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info" if not settings.debug else "debug"
    )


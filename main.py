"""WriteGen API - FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import connect_to_mongodb, close_mongodb_connection
from app.core.firebase import initialize_firebase
from app.api.routes import samples, styles, generation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    settings = get_settings()
    
    # Initialize Firebase
    try:
        initialize_firebase()
    except Exception as e:
        print(f"Warning: Firebase initialization failed: {e}")
        print("Firebase authentication may not work without proper credentials.")
    
    # Connect to MongoDB
    await connect_to_mongodb()
    
    yield
    
    # Shutdown
    await close_mongodb_connection()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered handwriting replication engine with Firebase Auth, "
                    "stroke extraction, style training, and PDF/SVG generation.",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(samples.router, prefix="/api")
    app.include_router(styles.router, prefix="/api")
    app.include_router(generation.router, prefix="/api")
    
    @app.get("/", tags=["health"])
    async def root():
        """Health check endpoint."""
        return {"status": "healthy", "service": settings.app_name}
    
    @app.get("/health", tags=["health"])
    async def health_check():
        """Detailed health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": "1.0.0",
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

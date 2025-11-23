"""
FastAPI main application entry point.
Initializes the FastAPI app and includes all route routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import db

# Import routers
from location_routes import router as location_router
from emergency_routes import router as emergency_router
from auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize database
    print("Initializing database...")
    db.initialize_tables()
    print("Database initialized successfully")
    
    yield
    
    # Shutdown: Close database connection
    print("Closing database connection...")
    db.disconnect()
    print("Database connection closed")


# Initialize FastAPI application
app = FastAPI(
    title="TheLocalShield API",
    description="Backend API for TheLocalShield application",
    version="2.5.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(location_router, prefix="/location", tags=["location"])
app.include_router(emergency_router, prefix="/emergency", tags=["emergency"])


@app.get("/")
async def root():
    """Root endpoint to check if API is running."""
    return {"message": "TheLocalShield API is running", "version": "2.5.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/test/emergencies")
async def test_emergencies():
    """Test endpoint to check if emergencies table works."""
    from database import get_recent_emergencies
    try:
        emergencies = get_recent_emergencies()
        return {
            "status": "ok",
            "count": len(emergencies),
            "emergencies": emergencies
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


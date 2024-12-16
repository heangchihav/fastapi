"""
FastAPI Express Integration

This is the main entry point for the FastAPI application.
It uses a factory pattern to create and configure the application.
"""

from src.main import app

if __name__ == "__main__":
    import uvicorn
    from src.core.config import get_settings
    
    settings = get_settings()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )
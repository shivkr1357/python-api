from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime

# Import controllers
from app.controllers.pdf_controller import router as pdf_router
from app.controllers.conversion_controller import router as conversion_router
from app.controllers.cleanup_controller import router as cleanup_router

# Create FastAPI app
app = FastAPI(
    title="PDF to PowerPoint Converter API",
    description="A FastAPI application for creating PDF files and converting them to PowerPoint presentations using MVC architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pdf_router)
app.include_router(conversion_router)
app.include_router(cleanup_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PDF to PowerPoint Converter API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "pdf_operations": "/pdf",
            "conversion_operations": "/convert",
            "cleanup_operations": "/cleanup"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "PDF to PowerPoint Converter API"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global exception handler for HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    # Create output directories
    os.makedirs("outputs/pdfs", exist_ok=True)
    os.makedirs("outputs/pptx", exist_ok=True)
    
    # Start cleanup service
    from app.services.cleanup_service import CleanupService
    cleanup_service = CleanupService()
    cleanup_service.start_cleanup_service()
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

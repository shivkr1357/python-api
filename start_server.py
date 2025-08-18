#!/usr/bin/env python3
"""
Simple startup script for the Python API project.
"""

import os
import uvicorn

# Set environment variables
os.environ.setdefault("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ENVIRONMENT", "development")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

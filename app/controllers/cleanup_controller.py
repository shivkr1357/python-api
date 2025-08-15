from fastapi import APIRouter, HTTPException
from app.services.cleanup_service import CleanupService

router = APIRouter(prefix="/cleanup", tags=["File Cleanup"])

# Initialize cleanup service
cleanup_service = CleanupService()

@router.post("/start")
async def start_cleanup_service():
    """Start the automatic cleanup service"""
    try:
        cleanup_service.start_cleanup_service()
        return {
            "success": True,
            "message": f"Cleanup service started. Files will be deleted after {cleanup_service.cleanup_interval_hours} hours.",
            "cleanup_interval_hours": cleanup_service.cleanup_interval_hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting cleanup service: {str(e)}")

@router.post("/stop")
async def stop_cleanup_service():
    """Stop the automatic cleanup service"""
    try:
        cleanup_service.stop_cleanup_service()
        return {
            "success": True,
            "message": "Cleanup service stopped."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping cleanup service: {str(e)}")

@router.get("/status")
async def get_cleanup_status():
    """Get the current status of the cleanup service"""
    try:
        status = cleanup_service.get_cleanup_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cleanup status: {str(e)}")

@router.post("/manual")
async def perform_manual_cleanup():
    """Perform manual cleanup of old files"""
    try:
        result = cleanup_service.manual_cleanup()
        return {
            "success": True,
            "message": f"Manual cleanup completed. Deleted {result['total_deleted']} files.",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing manual cleanup: {str(e)}")

@router.get("/config")
async def get_cleanup_config():
    """Get the current cleanup configuration"""
    try:
        return {
            "success": True,
            "config": {
                "pdf_directory": cleanup_service.pdf_dir,
                "pptx_directory": cleanup_service.pptx_dir,
                "cleanup_interval_hours": cleanup_service.cleanup_interval_hours,
                "service_running": cleanup_service.is_running
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cleanup config: {str(e)}")

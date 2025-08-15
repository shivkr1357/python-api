from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
from typing import List
from app.models.pdf_model import ConversionRequest, ConversionResponse
from app.services.pdf_service import PDFService
from app.services.pptx_service_single import PowerPointServiceSingle

router = APIRouter(prefix="/convert", tags=["PDF to PowerPoint Conversion"])

# Initialize services
pdf_service = PDFService()
pptx_service = PowerPointServiceSingle()

@router.post("/pdf-to-pptx", response_model=ConversionResponse)
async def convert_pdf_to_pptx(conversion_request: ConversionRequest):
    """Convert a PDF file to PowerPoint presentation"""
    try:
        response = pptx_service.convert_pdf_to_pptx(conversion_request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting PDF to PowerPoint: {str(e)}")

@router.get("/download-pptx/{filename}")
async def download_pptx(filename: str):
    """Download a PowerPoint file by filename"""
    try:
        file_path = os.path.join(pptx_service.output_dir, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PowerPoint file not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading PowerPoint: {str(e)}")

@router.get("/list-pptx")
async def list_pptx_files():
    """List all available PowerPoint files"""
    try:
        pptx_files = []
        if os.path.exists(pptx_service.output_dir):
            for filename in os.listdir(pptx_service.output_dir):
                if filename.endswith('.pptx'):
                    file_path = os.path.join(pptx_service.output_dir, filename)
                    file_stats = os.stat(file_path)
                    pptx_files.append({
                        "filename": filename,
                        "size_bytes": file_stats.st_size,
                        "created_at": file_stats.st_ctime,
                        "modified_at": file_stats.st_mtime
                    })
        
        return {
            "success": True,
            "pptx_files": pptx_files,
            "count": len(pptx_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing PowerPoint files: {str(e)}")

@router.delete("/delete-pptx/{filename}")
async def delete_pptx(filename: str):
    """Delete a PowerPoint file"""
    try:
        file_path = os.path.join(pptx_service.output_dir, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PowerPoint file not found")
        
        os.remove(file_path)
        return {
            "success": True,
            "message": f"PowerPoint file {filename} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting PowerPoint file: {str(e)}")

@router.post("/create-sample-pptx")
async def create_sample_pptx():
    """Create a sample PowerPoint presentation for testing"""
    try:
        title = "Sample Presentation"
        content = [
            "Welcome to the Sample Presentation",
            "This is a test slide created by the API.",
            "Key Features",
            "• Fast PDF to PowerPoint conversion",
            "• RESTful API interface",
            "• Professional formatting",
            "• Easy to use",
            "Thank You",
            "This presentation was generated automatically."
        ]
        
        file_path = pptx_service.create_sample_pptx(title, content)
        filename = os.path.basename(file_path)
        
        # Create HTTP URL for download
        if os.environ.get("LAMBDA_EXECUTION"):
            base_url = os.environ.get("API_BASE_URL", "https://your-api-id.execute-api.region.amazonaws.com/prod")
            http_url = f"{base_url}/convert/download-pptx/{filename}"
        else:
            http_url = f"http://localhost:8000/convert/download-pptx/{filename}"
        
        return {
            "success": True,
            "message": f"Sample PowerPoint created: {filename}",
            "pptx_path": http_url,
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sample PowerPoint: {str(e)}")

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
from typing import List
from app.models.pdf_model import PDFContent, PDFResponse, ConversionRequest, ConversionResponse
from app.services.pdf_service import PDFService
from app.services.pptx_service import PowerPointService

router = APIRouter(prefix="/pdf", tags=["PDF Operations"])

# Initialize services
pdf_service = PDFService()
pptx_service = PowerPointService()

@router.post("/create", response_model=PDFResponse)
async def create_pdf(pdf_content: PDFContent):
    """Create a PDF file from provided content"""
    try:
        response = pdf_service.create_pdf(pdf_content)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating PDF: {str(e)}")

@router.get("/download/{filename}")
async def download_pdf(filename: str):
    """Download a PDF file by filename"""
    try:
        file_path = os.path.join(pdf_service.output_dir, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading PDF: {str(e)}")

@router.get("/list")
async def list_pdfs():
    """List all available PDF files"""
    try:
        pdf_files = []
        if os.path.exists(pdf_service.output_dir):
            for filename in os.listdir(pdf_service.output_dir):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(pdf_service.output_dir, filename)
                    file_info = pdf_service.get_pdf_info(file_path)
                    if "error" not in file_info:
                        pdf_files.append(file_info)
        
        return {
            "success": True,
            "pdfs": pdf_files,
            "count": len(pdf_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing PDFs: {str(e)}")

@router.get("/info/{filename}")
async def get_pdf_info(filename: str):
    """Get information about a specific PDF file"""
    try:
        file_path = os.path.join(pdf_service.output_dir, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        info = pdf_service.get_pdf_info(file_path)
        if "error" in info:
            raise HTTPException(status_code=400, detail=info["error"])
        
        return {
            "success": True,
            "info": info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting PDF info: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_pdf(filename: str):
    """Delete a PDF file"""
    try:
        file_path = os.path.join(pdf_service.output_dir, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        os.remove(file_path)
        return {
            "success": True,
            "message": f"PDF file {filename} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting PDF: {str(e)}")

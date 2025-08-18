"""
PDF Unlock API - Simple FastAPI application for unlocking password-protected PDFs.
"""

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime, timedelta
from urllib.parse import unquote
from typing import List

# Create FastAPI application
app = FastAPI(
    title="PDF Unlock API",
    version="1.0.0",
    description="A simple API for unlocking and locking password-protected PDF files",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# Store for temporary PDF files (in production, use Redis or database)
temp_pdfs = {}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PDF Unlock API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "unlock_pdf": "POST /unlock-pdf",
            "unlock_with_password": "POST /unlock-with-password",
            "lock_pdf": "POST /lock-pdf",
            "compress_pdf": "POST /compress-pdf",
            "pdf_to_powerpoint": "POST /pdf-to-powerpoint",
            "powerpoint_to_pdf": "POST /powerpoint-to-pdf",
            "jpg_to_pdf": "POST /jpg-to-pdf",
            "pdf_to_jpg": "POST /pdf-to-jpg",
            "download_pdf": "GET /download-pdf/{file_id}",
            "delete_pdf": "DELETE /download-pdf/{file_id}",
            "debug_files": "GET /debug/files"
        },
        "workflow": {
            "step1": "Upload PDF to /unlock-pdf for automatic unlock attempt",
            "step2": "If automatic unlock fails, use /unlock-with-password with file_id and password",
            "step3": "Download unlocked PDF using the provided download URL"
        },
        "features": {
            "unlock": "Automatically unlock password-protected PDFs",
            "lock": "Add password protection to PDFs",
            "compress": "Reduce PDF file size with compression levels (low, medium, high)",
            "convert": "Convert PDF to PowerPoint, PowerPoint to PDF, JPG to PDF, and PDF to JPG"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "PDF Unlock API"
    }

@app.get("/debug/files")
async def debug_files():
    """Debug endpoint to see stored files."""
    return {
        "stored_files": list(temp_pdfs.keys()),
        "file_count": len(temp_pdfs),
        "uploads_dir": UPLOADS_DIR,
        "uploads_dir_exists": os.path.exists(UPLOADS_DIR)
    }

@app.post("/unlock-pdf")
async def unlock_pdf(
    pdf_file: UploadFile = File(..., description="Password-protected PDF file to unlock")
):
    """
    Automatically unlock a password-protected PDF file and return a download link.
    
    This endpoint attempts to unlock the PDF automatically without requiring a password.
    If automatic unlock fails, the original PDF is returned with a note that manual
    password entry may be required.
    
    - **pdf_file**: The password-protected PDF file to unlock
    
    Returns:
    - **JSON**: Contains download link and file information
    """
    from app.utils.pdf_processor import PDFProcessor
    
    # Validate the uploaded file
    PDFProcessor.validate_pdf_file(pdf_file)
    
    try:
        print(f"DEBUG: Starting automatic unlock for file: {pdf_file.filename}")
        
        # Unlock the PDF automatically
        unlocked_pdf_content, filename = PDFProcessor.unlock_pdf_automatically(pdf_file)
        
        print(f"DEBUG: Successfully unlocked PDF, content size: {len(unlocked_pdf_content)} bytes")
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Save the unlocked PDF to disk
        file_path = os.path.join(UPLOADS_DIR, f"{file_id}.pdf")
        with open(file_path, "wb") as f:
            f.write(unlocked_pdf_content)
        
        print(f"DEBUG: Saved unlocked PDF to: {file_path}")
        
        # Store file info with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        temp_pdfs[file_id] = {
            "filename": filename,
            "file_path": file_path,
            "expires_at": expiration_time,
            "file_size": len(unlocked_pdf_content),
            "unlock_method": "automatic"
        }
        
        # Generate download URL - ensure no encoding issues
        download_url = f"http://localhost:8000/download-pdf/{file_id}"
        
        print(f"DEBUG: Generated file_id: {file_id}")
        print(f"DEBUG: Download URL: {download_url}")
        print(f"DEBUG: Stored in temp_pdfs: {file_id in temp_pdfs}")
        
        return {
            "success": True,
            "message": "PDF unlocked successfully - no password required to open",
            "download_url": download_url,
            "filename": filename,
            "file_size": len(unlocked_pdf_content),
            "expires_at": expiration_time.isoformat(),
            "file_id": file_id,
            "unlock_method": "automatic",
            "passwordRequired": False,
            "note": "The downloaded PDF should open without asking for a password"
        }
        
    except HTTPException as http_error:
        print(f"DEBUG: Automatic unlock failed: {http_error.detail}")
        # If automatic unlock fails, save the original PDF and return it
        # This allows the frontend to then ask for a password and call unlock-with-password
        try:
            # Read the original file content
            pdf_file.file.seek(0)  # Reset file pointer
            original_content = pdf_file.file.read()
            
            # Generate unique ID for the file
            file_id = str(uuid.uuid4())
            
            # Save the original PDF to disk
            file_path = os.path.join(UPLOADS_DIR, f"{file_id}.pdf")
            with open(file_path, "wb") as f:
                f.write(original_content)
            
            # Store file info with expiration (24 hours)
            expiration_time = datetime.now() + timedelta(hours=24)
            temp_pdfs[file_id] = {
                "filename": f"original_{pdf_file.filename}",
                "file_path": file_path,
                "expires_at": expiration_time,
                "file_size": len(original_content),
                "unlock_method": "failed_automatic",
                "original_filename": pdf_file.filename
            }
            
            # Generate download URL - ensure no encoding issues
            download_url = f"http://localhost:8000/download-pdf/{file_id}"
            
            print(f"DEBUG: Generated file_id (fallback): {file_id}")
            print(f"DEBUG: Download URL (fallback): {download_url}")
            print(f"DEBUG: Stored in temp_pdfs (fallback): {file_id in temp_pdfs}")
            
            return {
                "success": False,
                "message": "Automatic unlock failed - password required",
                "download_url": download_url,
                "filename": f"original_{pdf_file.filename}",
                "file_size": len(original_content),
                "expires_at": expiration_time.isoformat(),
                "file_id": file_id,
                "unlock_method": "failed_automatic",
                "original_filename": pdf_file.filename,
                "passwordRequired": True,
                "note": "Automatic unlock failed. Use the unlock-with-password endpoint with this file_id and the correct password.",
                "next_step": "Call /unlock-with-password endpoint with file_id and password"
            }
            
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing PDF: {str(http_error.detail)}. Fallback also failed: {str(fallback_error)}"
            )
    except Exception as e:
        print(f"DEBUG: Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

@app.post("/unlock-with-password")
async def unlock_with_password(
    file_id: str = Form(..., description="File ID from previous unlock attempt"),
    password: str = Form(..., description="Password to unlock the PDF")
):
    """
    Unlock a PDF file using a provided password.
    
    This endpoint is used after the automatic unlock fails. It takes the file_id
    from the previous attempt and a password to unlock the PDF.
    
    - **file_id**: The file ID from the previous unlock attempt
    - **password**: The password to unlock the PDF
    
    Returns:
    - **JSON**: Contains download link and file information
    """
    from app.utils.pdf_processor import PDFProcessor
    
    # Decode URL-encoded file_id if needed
    decoded_file_id = unquote(file_id)
    
    # Try both original and decoded file_id
    actual_file_id = None
    if file_id in temp_pdfs:
        actual_file_id = file_id
    elif decoded_file_id in temp_pdfs:
        actual_file_id = decoded_file_id
    else:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    file_info = temp_pdfs[actual_file_id]
    
    # Check if file has expired
    if datetime.now() > file_info["expires_at"]:
        # Remove expired file
        if os.path.exists(file_info["file_path"]):
            os.remove(file_info["file_path"])
        del temp_pdfs[actual_file_id]
        raise HTTPException(status_code=410, detail="File has expired")
    
    # Check if file exists on disk
    if not os.path.exists(file_info["file_path"]):
        del temp_pdfs[actual_file_id]
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    try:
        print(f"DEBUG: Attempting password unlock for file_id: {actual_file_id}")
        
        # Read the original PDF file
        with open(file_info["file_path"], "rb") as f:
            pdf_content = f.read()
        
        # Create a temporary UploadFile object for the PDF processor
        from fastapi import UploadFile
        import io
        
        temp_file = UploadFile(
            filename=file_info.get("original_filename", "temp.pdf"),
            file=io.BytesIO(pdf_content)
        )
        
        # Unlock the PDF with password
        unlocked_pdf_content, filename = PDFProcessor.unlock_pdf_with_password(temp_file, password)
        
        print(f"DEBUG: Successfully unlocked PDF with password, content size: {len(unlocked_pdf_content)} bytes")
        
        # Generate new unique ID for the unlocked file
        new_file_id = str(uuid.uuid4())
        
        # Save the unlocked PDF to disk
        new_file_path = os.path.join(UPLOADS_DIR, f"{new_file_id}.pdf")
        with open(new_file_path, "wb") as f:
            f.write(unlocked_pdf_content)
        
        print(f"DEBUG: Saved unlocked PDF to: {new_file_path}")
        
        # Store new file info with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        temp_pdfs[new_file_id] = {
            "filename": filename,
            "file_path": new_file_path,
            "expires_at": expiration_time,
            "file_size": len(unlocked_pdf_content),
            "unlock_method": "password"
        }
        
        # Generate download URL
        download_url = f"http://localhost:8000/download-pdf/{new_file_id}"
        
        print(f"DEBUG: Generated new file_id: {new_file_id}")
        print(f"DEBUG: Download URL: {download_url}")
        
        return {
            "success": True,
            "message": "PDF unlocked successfully with password - no password required to open",
            "download_url": download_url,
            "filename": filename,
            "file_size": len(unlocked_pdf_content),
            "expires_at": expiration_time.isoformat(),
            "file_id": new_file_id,
            "unlock_method": "password",
            "passwordRequired": False,
            "note": "The downloaded PDF should open without asking for a password"
        }
        
    except HTTPException as http_error:
        print(f"DEBUG: Password unlock failed: {http_error.detail}")
        raise http_error
    except Exception as e:
        print(f"DEBUG: Unexpected error in password unlock: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error unlocking PDF with password: {str(e)}"
        )

@app.post("/lock-pdf")
async def lock_pdf(
    pdf_file: UploadFile = File(..., description="PDF file to password-protect"),
    password: str = Form(..., description="Password to protect the PDF")
):
    """
    Lock a PDF file with a password and return a download link.
    
    This endpoint accepts a PDF file and a password,
    then returns a temporary link to download the password-protected PDF.
    
    - **pdf_file**: The PDF file to password-protect
    - **password**: The password to protect the PDF
    
    Returns:
    - **JSON**: Contains download link and file information
    """
    from app.utils.pdf_processor import PDFProcessor
    
    # Validate the uploaded file
    PDFProcessor.validate_pdf_file(pdf_file)
    
    try:
        # Lock the PDF
        locked_pdf_content, filename = PDFProcessor.lock_pdf_with_password(
            pdf_file, password
        )
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Save the locked PDF to disk
        file_path = os.path.join(UPLOADS_DIR, f"{file_id}.pdf")
        with open(file_path, "wb") as f:
            f.write(locked_pdf_content)
        
        # Store file info with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        temp_pdfs[file_id] = {
            "filename": filename,
            "file_path": file_path,
            "expires_at": expiration_time,
            "file_size": len(locked_pdf_content)
        }
        
        # Generate download URL
        download_url = f"http://localhost:8000/download-pdf/{file_id}"
        
        return {
            "success": True,
            "message": "PDF locked successfully",
            "download_url": download_url,
            "filename": filename,
            "file_size": len(locked_pdf_content),
            "expires_at": expiration_time.isoformat(),
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

@app.post("/compress-pdf")
async def compress_pdf(
    pdf_file: UploadFile = File(..., description="PDF file to compress"),
    compression_level: str = Form("medium", description="Compression level: low, medium, high")
):
    """
    Compress a PDF file to reduce its size.
    
    This endpoint accepts a PDF file and compresses it to reduce file size
    while maintaining reasonable quality.
    
    - **pdf_file**: The PDF file to compress
    - **compression_level**: Compression level (low, medium, high)
    
    Returns:
    - **JSON**: Contains download link and file information
    """
    from app.utils.pdf_processor import PDFProcessor
    
    # Validate the uploaded file
    PDFProcessor.validate_pdf_file(pdf_file)
    
    # Validate compression level
    valid_levels = ["low", "medium", "high"]
    if compression_level not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid compression level. Must be one of: {', '.join(valid_levels)}"
        )
    
    try:
        print(f"DEBUG: Starting PDF compression for file: {pdf_file.filename} with level: {compression_level}")
        
        # Compress the PDF
        compressed_pdf_content, filename = PDFProcessor.compress_pdf(pdf_file, compression_level)
        
        print(f"DEBUG: Successfully compressed PDF, content size: {len(compressed_pdf_content)} bytes")
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Save the compressed PDF to disk
        file_path = os.path.join(UPLOADS_DIR, f"{file_id}.pdf")
        with open(file_path, "wb") as f:
            f.write(compressed_pdf_content)
        
        print(f"DEBUG: Saved compressed PDF to: {file_path}")
        
        # Store file info with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        temp_pdfs[file_id] = {
            "filename": filename,
            "file_path": file_path,
            "expires_at": expiration_time,
            "file_size": len(compressed_pdf_content),
            "compression_level": compression_level
        }
        
        # Generate download URL
        download_url = f"http://localhost:8000/download-pdf/{file_id}"
        
        print(f"DEBUG: Generated file_id: {file_id}")
        print(f"DEBUG: Download URL: {download_url}")
        
        return {
            "success": True,
            "message": f"PDF compressed successfully with {compression_level} compression",
            "download_url": download_url,
            "filename": filename,
            "file_size": len(compressed_pdf_content),
            "expires_at": expiration_time.isoformat(),
            "file_id": file_id,
            "compression_level": compression_level,
            "note": "The compressed PDF is ready for download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in compression: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error compressing PDF: {str(e)}"
        )

@app.post("/pdf-to-powerpoint")
async def pdf_to_powerpoint(
    pdf_file: UploadFile = File(..., description="PDF file to convert to PowerPoint")
):
    """
    Convert a PDF file to PowerPoint format.
    
    This endpoint accepts a PDF file and converts it to PowerPoint format.
    Each page of the PDF becomes a slide in the PowerPoint presentation.
    
    - **pdf_file**: The PDF file to convert to PowerPoint
    
    Returns:
    - **JSON**: Contains download link and file information
    """
    from app.utils.pdf_processor import PDFProcessor
    
    # Validate the uploaded file
    PDFProcessor.validate_pdf_file(pdf_file)
    
    try:
        print(f"DEBUG: Starting PDF to PowerPoint conversion for file: {pdf_file.filename}")
        
        # Convert PDF to PowerPoint
        powerpoint_content, filename = PDFProcessor.pdf_to_powerpoint(pdf_file)
        
        print(f"DEBUG: Successfully converted PDF to PowerPoint, content size: {len(powerpoint_content)} bytes")
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Save the PowerPoint file to disk
        file_path = os.path.join(UPLOADS_DIR, f"{file_id}.pptx")
        with open(file_path, "wb") as f:
            f.write(powerpoint_content)
        
        print(f"DEBUG: Saved PowerPoint file to: {file_path}")
        
        # Store file info with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        temp_pdfs[file_id] = {
            "filename": filename,
            "file_path": file_path,
            "expires_at": expiration_time,
            "file_size": len(powerpoint_content),
            "conversion_type": "pdf_to_powerpoint"
        }
        
        # Generate download URL
        download_url = f"http://localhost:8000/download-pdf/{file_id}"
        
        print(f"DEBUG: Generated file_id: {file_id}")
        print(f"DEBUG: Download URL: {download_url}")
        
        return {
            "success": True,
            "message": "PDF successfully converted to PowerPoint",
            "download_url": download_url,
            "filename": filename,
            "file_size": len(powerpoint_content),
            "expires_at": expiration_time.isoformat(),
            "file_id": file_id,
            "conversion_type": "pdf_to_powerpoint",
            "note": "The PowerPoint file is ready for download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in PDF to PowerPoint conversion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error converting PDF to PowerPoint: {str(e)}"
        )

@app.post("/powerpoint-to-pdf")
async def powerpoint_to_pdf(
    pptx_file: UploadFile = File(..., description="PowerPoint file to convert to PDF")
):
    """
    Convert a PowerPoint file to PDF format.
    
    This endpoint accepts a PowerPoint file and converts it to PDF format.
    Each slide of the PowerPoint becomes a page in the PDF document.
    
    - **pptx_file**: The PowerPoint file to convert to PDF
    
    Returns:
    - **JSON**: Contains download link and file information
    """
    from app.utils.pdf_processor import PDFProcessor
    
    # Validate the uploaded file
    PDFProcessor.validate_powerpoint_file(pptx_file)
    
    try:
        print(f"DEBUG: Starting PowerPoint to PDF conversion for file: {pptx_file.filename}")
        
        # Convert PowerPoint to PDF
        pdf_content, filename = PDFProcessor.powerpoint_to_pdf(pptx_file)
        
        print(f"DEBUG: Successfully converted PowerPoint to PDF, content size: {len(pdf_content)} bytes")
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Save the PDF file to disk
        file_path = os.path.join(UPLOADS_DIR, f"{file_id}.pdf")
        with open(file_path, "wb") as f:
            f.write(pdf_content)
        
        print(f"DEBUG: Saved PDF file to: {file_path}")
        
        # Store file info with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        temp_pdfs[file_id] = {
            "filename": filename,
            "file_path": file_path,
            "expires_at": expiration_time,
            "file_size": len(pdf_content),
            "conversion_type": "powerpoint_to_pdf"
        }
        
        # Generate download URL
        download_url = f"http://localhost:8000/download-pdf/{file_id}"
        
        print(f"DEBUG: Generated file_id: {file_id}")
        print(f"DEBUG: Download URL: {download_url}")
        
        return {
            "success": True,
            "message": "PowerPoint successfully converted to PDF",
            "download_url": download_url,
            "filename": filename,
            "file_size": len(pdf_content),
            "expires_at": expiration_time.isoformat(),
            "file_id": file_id,
            "conversion_type": "powerpoint_to_pdf",
            "note": "The PDF file is ready for download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in PowerPoint to PDF conversion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error converting PowerPoint to PDF: {str(e)}"
        )

@app.post("/jpg-to-pdf")
async def jpg_to_pdf(
    jpg_files: List[UploadFile] = File(..., description="JPG image files to convert to PDF"),
    page_orientation: str = Form("portrait", description="Page orientation: 'portrait' or 'landscape'"),
    page_size: str = Form("a4", description="Page size: 'a4', 'us_letter', or 'fit'"),
    margin: str = Form("no_margin", description="Margin: 'no_margin', 'small', or 'big'"),
    merge_all: bool = Form(True, description="Merge all images into one PDF file")
):
    """
    Convert JPG images to PDF format with configurable options.
    
    This endpoint accepts multiple JPG image files and converts them to PDF format
    with configurable page orientation, size, margins, and merging options.
    
    - **jpg_files**: List of JPG image files to convert to PDF
    - **page_orientation**: Page orientation ("portrait" or "landscape")
    - **page_size**: Page size ("a4", "us_letter", or "fit")
    - **margin**: Margin size ("no_margin", "small", or "big")
    - **merge_all**: Whether to merge all images into one PDF file
    
    Returns:
    - **JSON**: Contains download link and file information
    """
    from app.utils.pdf_processor import PDFProcessor
    
    # Validate the uploaded files
    for jpg_file in jpg_files:
        PDFProcessor.validate_jpg_file(jpg_file)
    
    try:
        print(f"DEBUG: Starting JPG to PDF conversion for {len(jpg_files)} files")
        print(f"DEBUG: Options - Orientation: {page_orientation}, Size: {page_size}, Margin: {margin}, Merge: {merge_all}")
        
        # Convert JPG to PDF
        pdf_content, filename = PDFProcessor.jpg_to_pdf(
            jpg_files, page_orientation, page_size, margin, merge_all
        )
        
        print(f"DEBUG: Successfully converted JPG to PDF, content size: {len(pdf_content)} bytes")
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Save the PDF file to disk
        file_path = os.path.join(UPLOADS_DIR, f"{file_id}.pdf")
        with open(file_path, "wb") as f:
            f.write(pdf_content)
        
        print(f"DEBUG: Saved PDF file to: {file_path}")
        
        # Store file info with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        temp_pdfs[file_id] = {
            "filename": filename,
            "file_path": file_path,
            "expires_at": expiration_time,
            "file_size": len(pdf_content),
            "conversion_type": "jpg_to_pdf",
            "options": {
                "page_orientation": page_orientation,
                "page_size": page_size,
                "margin": margin,
                "merge_all": merge_all,
                "image_count": len(jpg_files)
            }
        }
        
        # Generate download URL
        download_url = f"http://localhost:8000/download-pdf/{file_id}"
        
        print(f"DEBUG: Generated file_id: {file_id}")
        print(f"DEBUG: Download URL: {download_url}")
        
        return {
            "success": True,
            "message": f"Successfully converted {len(jpg_files)} JPG image(s) to PDF",
            "download_url": download_url,
            "filename": filename,
            "file_size": len(pdf_content),
            "expires_at": expiration_time.isoformat(),
            "file_id": file_id,
            "conversion_type": "jpg_to_pdf",
            "options": {
                "page_orientation": page_orientation,
                "page_size": page_size,
                "margin": margin,
                "merge_all": merge_all,
                "image_count": len(jpg_files)
            },
            "note": "The PDF file is ready for download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in JPG to PDF conversion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error converting JPG to PDF: {str(e)}"
        )

@app.post("/pdf-to-jpg")
async def pdf_to_jpg(
    pdf_file: UploadFile = File(..., description="PDF file to convert to JPG"),
    page_number: int = Form(1, description="Page number to convert (default: 1)")
):
    """
    Convert a PDF page to JPG format.
    
    This endpoint accepts a PDF file and converts a specific page to JPG format.
    The JPG will have high quality and maintain the original page dimensions.
    
    - **pdf_file**: The PDF file to convert to JPG
    - **page_number**: Page number to convert (default: 1)
    
    Returns:
    - **JSON**: Contains download link and file information
    """
    from app.utils.pdf_processor import PDFProcessor
    
    # Validate the uploaded file
    PDFProcessor.validate_pdf_file(pdf_file)
    
    # Validate page number
    if page_number < 1:
        raise HTTPException(
            status_code=400,
            detail="Page number must be greater than 0"
        )
    
    try:
        print(f"DEBUG: Starting PDF to JPG conversion for file: {pdf_file.filename}, page: {page_number}")
        
        # Convert PDF to JPG
        jpg_content, filename = PDFProcessor.pdf_to_jpg(pdf_file, page_number)
        
        print(f"DEBUG: Successfully converted PDF to JPG, content size: {len(jpg_content)} bytes")
        
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Save the JPG file to disk
        file_path = os.path.join(UPLOADS_DIR, f"{file_id}.jpg")
        with open(file_path, "wb") as f:
            f.write(jpg_content)
        
        print(f"DEBUG: Saved JPG file to: {file_path}")
        
        # Store file info with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        temp_pdfs[file_id] = {
            "filename": filename,
            "file_path": file_path,
            "expires_at": expiration_time,
            "file_size": len(jpg_content),
            "conversion_type": "pdf_to_jpg",
            "page_number": page_number
        }
        
        # Generate download URL
        download_url = f"http://localhost:8000/download-pdf/{file_id}"
        
        print(f"DEBUG: Generated file_id: {file_id}")
        print(f"DEBUG: Download URL: {download_url}")
        
        return {
            "success": True,
            "message": f"PDF page {page_number} successfully converted to JPG",
            "download_url": download_url,
            "filename": filename,
            "file_size": len(jpg_content),
            "expires_at": expiration_time.isoformat(),
            "file_id": file_id,
            "conversion_type": "pdf_to_jpg",
            "page_number": page_number,
            "note": "The JPG file is ready for download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in PDF to JPG conversion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error converting PDF to JPG: {str(e)}"
        )

@app.get("/download-pdf/{file_id}")
async def download_pdf(file_id: str):
    """
    Download a PDF file by its ID.
    
    This endpoint allows downloading PDF files using the file ID
    returned from the unlock-pdf or lock-pdf endpoints.
    
    - **file_id**: The unique identifier for the PDF file
    
    Returns:
    - **File**: The PDF file for download
    """
    # Decode URL-encoded file_id if needed
    decoded_file_id = unquote(file_id)
    
    print(f"DEBUG: Original file_id: {file_id}")
    print(f"DEBUG: Decoded file_id: {decoded_file_id}")
    print(f"DEBUG: Available file_ids: {list(temp_pdfs.keys())}")
    print(f"DEBUG: Original in temp_pdfs: {file_id in temp_pdfs}")
    print(f"DEBUG: Decoded in temp_pdfs: {decoded_file_id in temp_pdfs}")
    
    # Try both original and decoded file_id
    actual_file_id = None
    if file_id in temp_pdfs:
        actual_file_id = file_id
    elif decoded_file_id in temp_pdfs:
        actual_file_id = decoded_file_id
    else:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    file_info = temp_pdfs[actual_file_id]
    
    # Check if file has expired
    if datetime.now() > file_info["expires_at"]:
        # Remove expired file
        if os.path.exists(file_info["file_path"]):
            os.remove(file_info["file_path"])
        del temp_pdfs[actual_file_id]
        raise HTTPException(status_code=410, detail="File has expired")
    
    # Check if file exists on disk
    if not os.path.exists(file_info["file_path"]):
        del temp_pdfs[actual_file_id]
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Return the file for download
    return FileResponse(
        path=file_info["file_path"],
        filename=file_info["filename"],
        media_type="application/pdf" if file_info["filename"].endswith('.pdf') else 
                  "image/jpeg" if file_info["filename"].endswith(('.jpg', '.jpeg')) else
                  "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

@app.delete("/download-pdf/{file_id}")
async def delete_pdf(file_id: str):
    """
    Delete a PDF file by its ID.
    
    This endpoint allows manual deletion of PDF files.
    
    - **file_id**: The unique identifier for the PDF file
    
    Returns:
    - **JSON**: Success message
    """
    # Decode URL-encoded file_id if needed
    decoded_file_id = unquote(file_id)
    
    # Try both original and decoded file_id
    actual_file_id = None
    if file_id in temp_pdfs:
        actual_file_id = file_id
    elif decoded_file_id in temp_pdfs:
        actual_file_id = decoded_file_id
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = temp_pdfs[actual_file_id]
    
    # Remove file from disk
    if os.path.exists(file_info["file_path"]):
        os.remove(file_info["file_path"])
    
    # Remove from memory
    del temp_pdfs[actual_file_id]
    
    return {
        "success": True,
        "message": "File deleted successfully"
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

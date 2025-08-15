from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PDFContent(BaseModel):
    """Model for PDF content data"""
    title: str = Field(..., description="Title of the PDF document")
    content: str = Field(..., description="Main content of the PDF")
    author: Optional[str] = Field(None, description="Author of the document")
    subject: Optional[str] = Field(None, description="Subject of the document")
    keywords: Optional[List[str]] = Field(None, description="Keywords for the document")

class PDFResponse(BaseModel):
    """Model for PDF creation response"""
    success: bool
    message: str
    pdf_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class ConversionRequest(BaseModel):
    """Model for PDF to PowerPoint conversion request"""
    pdf_path: str = Field(..., description="Path to the PDF file to convert")
    output_name: Optional[str] = Field(None, description="Name for the output PowerPoint file")
    include_images: bool = Field(True, description="Whether to include images in conversion")

class ConversionResponse(BaseModel):
    """Model for conversion response"""
    success: bool
    message: str
    pptx_path: Optional[str] = None
    converted_at: datetime = Field(default_factory=datetime.now)

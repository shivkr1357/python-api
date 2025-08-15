import os
import re
import uuid
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from app.models.pdf_model import PDFContent, PDFResponse

class PDFService:
    """Service class for PDF operations"""
    
    def __init__(self, output_dir: str = "outputs/pdfs"):
        # Use /tmp in Lambda environment
        if os.environ.get("LAMBDA_EXECUTION"):
            self.output_dir = "/tmp/outputs/pdfs"
        else:
            self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure the output directory exists"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_pdf(self, pdf_content: PDFContent) -> PDFResponse:
        """Create a PDF file from the provided content"""
        try:
            # Generate unique filename with UUID to ensure uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds
            unique_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
            safe_title = re.sub(r'[^\w\s-]', '', pdf_content.title).strip()  # Remove special characters
            safe_title = re.sub(r'[-\s]+', '_', safe_title)  # Replace spaces and dashes with underscores
            
            filename = f"{safe_title}_{timestamp}_{unique_id}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # Center alignment
                textColor=colors.darkblue
            )
            
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                leading=16
            )
            
            # Build PDF content
            story = []
            
            # Add title
            title = Paragraph(pdf_content.title, title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add metadata if provided
            if pdf_content.author:
                author_text = f"<b>Author:</b> {pdf_content.author}"
                story.append(Paragraph(author_text, content_style))
                story.append(Spacer(1, 10))
            
            if pdf_content.subject:
                subject_text = f"<b>Subject:</b> {pdf_content.subject}"
                story.append(Paragraph(subject_text, content_style))
                story.append(Spacer(1, 10))
            
            if pdf_content.keywords:
                keywords_text = f"<b>Keywords:</b> {', '.join(pdf_content.keywords)}"
                story.append(Paragraph(keywords_text, content_style))
                story.append(Spacer(1, 20))
            
            # Add main content
            content_paragraphs = pdf_content.content.split('\n\n')
            for paragraph in content_paragraphs:
                if paragraph.strip():
                    story.append(Paragraph(paragraph.strip(), content_style))
                    story.append(Spacer(1, 10))
            
            # Build PDF
            doc.build(story)
            
            return PDFResponse(
                success=True,
                message=f"PDF created successfully: {filename}",
                pdf_path=filepath
            )
            
        except Exception as e:
            return PDFResponse(
                success=False,
                message=f"Error creating PDF: {str(e)}"
            )
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """Get basic information about a PDF file"""
        try:
            if not os.path.exists(pdf_path):
                return {"error": "PDF file not found"}
            
            file_stats = os.stat(pdf_path)
            return {
                "filename": os.path.basename(pdf_path),
                "size_bytes": file_stats.st_size,
                "created_at": datetime.fromtimestamp(file_stats.st_ctime),
                "modified_at": datetime.fromtimestamp(file_stats.st_mtime)
            }
        except Exception as e:
            return {"error": f"Error reading PDF info: {str(e)}"}

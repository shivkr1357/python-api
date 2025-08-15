#!/usr/bin/env python3
"""
Create a test PDF with images for testing image extraction
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image, ImageDraw
import os

def create_test_images():
    """Create test images"""
    # Create a temporary directory for test images
    temp_dir = "temp_test_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create a simple chart image
    chart_img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(chart_img)
    
    # Draw a simple bar chart
    draw.rectangle([50, 50, 350, 250], outline='black', width=2)
    draw.rectangle([80, 200, 120, 220], fill='blue')
    draw.rectangle([140, 150, 180, 220], fill='green')
    draw.rectangle([200, 100, 240, 220], fill='red')
    draw.rectangle([260, 180, 300, 220], fill='orange')
    
    # Add labels
    draw.text((70, 230), "Q1", fill='black')
    draw.text((150, 230), "Q2", fill='black')
    draw.text((210, 230), "Q3", fill='black')
    draw.text((270, 230), "Q4", fill='black')
    draw.text((10, 130), "Sales", fill='black')
    
    chart_path = os.path.join(temp_dir, "chart.png")
    chart_img.save(chart_path)
    
    # Create a simple diagram
    diagram_img = Image.new('RGB', (350, 250), 'white')
    draw = ImageDraw.Draw(diagram_img)
    
    # Draw a flowchart
    draw.rectangle([50, 50, 150, 100], outline='blue', width=2, fill='lightblue')
    draw.text((75, 70), "Process 1", fill='black')
    
    draw.rectangle([200, 50, 300, 100], outline='green', width=2, fill='lightgreen')
    draw.text((220, 70), "Process 2", fill='black')
    
    draw.rectangle([125, 150, 225, 200], outline='red', width=2, fill='lightcoral')
    draw.text((155, 170), "Result", fill='black')
    
    # Draw arrows
    draw.line([150, 75, 200, 75], fill='black', width=2)
    draw.polygon([(195, 70), (200, 75), (195, 80)], fill='black')
    
    draw.line([175, 100, 175, 150], fill='black', width=2)
    draw.polygon([(170, 145), (175, 150), (180, 145)], fill='black')
    
    diagram_path = os.path.join(temp_dir, "diagram.png")
    diagram_img.save(diagram_path)
    
    return chart_path, diagram_path

def create_pdf_with_images():
    """Create a PDF with text and images"""
    # Create test images
    chart_path, diagram_path = create_test_images()
    
    # Create PDF
    doc = SimpleDocTemplate("outputs/pdfs/test_pdf_with_images.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
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
    
    # Title
    title = Paragraph("Business Report with Images", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Introduction
    intro = Paragraph("This report demonstrates the integration of text and images in PDF documents.", content_style)
    story.append(intro)
    story.append(Spacer(1, 20))
    
    # Section 1
    section1_title = Paragraph("Sales Performance", styles['Heading2'])
    story.append(section1_title)
    story.append(Spacer(1, 10))
    
    section1_text = Paragraph("The following chart shows our quarterly sales performance:", content_style)
    story.append(section1_text)
    story.append(Spacer(1, 10))
    
    # Add chart image
    chart_img = RLImage(chart_path, width=4*inch, height=3*inch)
    story.append(chart_img)
    story.append(Spacer(1, 20))
    
    # Section 2
    section2_title = Paragraph("Process Flow", styles['Heading2'])
    story.append(section2_title)
    story.append(Spacer(1, 10))
    
    section2_text = Paragraph("Our business process follows this workflow:", content_style)
    story.append(section2_text)
    story.append(Spacer(1, 10))
    
    # Add diagram image
    diagram_img = RLImage(diagram_path, width=3.5*inch, height=2.5*inch)
    story.append(diagram_img)
    story.append(Spacer(1, 20))
    
    # Conclusion
    conclusion = Paragraph("These visualizations help illustrate our business performance and processes effectively.", content_style)
    story.append(conclusion)
    
    # Build PDF
    doc.build(story)
    
    # Clean up temporary images
    import shutil
    shutil.rmtree("temp_test_images")
    
    print("✅ Created PDF with images: outputs/pdfs/test_pdf_with_images.pdf")

if __name__ == "__main__":
    create_pdf_with_images()

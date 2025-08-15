#!/usr/bin/env python3
"""
Test script to verify PDF content extraction
"""

import pdfplumber
import PyPDF2
import os

def test_pdf_extraction(pdf_path: str):
    """Test PDF content extraction using different methods"""
    print(f"Testing PDF extraction for: {pdf_path}")
    print("=" * 60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Test 1: pdfplumber
    print("\n📄 Testing pdfplumber extraction:")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"   Total pages: {len(pdf.pages)}")
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    print(f"   Page {page_num}: {len(text)} characters")
                    print(f"   Preview: {text[:200]}...")
                else:
                    print(f"   Page {page_num}: No text extracted")
    except Exception as e:
        print(f"   ❌ pdfplumber error: {e}")
    
    # Test 2: PyPDF2
    print("\n📄 Testing PyPDF2 extraction:")
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"   Total pages: {len(pdf_reader.pages)}")
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    print(f"   Page {page_num}: {len(text)} characters")
                    print(f"   Preview: {text[:200]}...")
                else:
                    print(f"   Page {page_num}: No text extracted")
    except Exception as e:
        print(f"   ❌ PyPDF2 error: {e}")
    
    # Test 3: File info
    print(f"\n📊 File information:")
    file_size = os.path.getsize(pdf_path)
    print(f"   File size: {file_size} bytes ({file_size/1024:.1f} KB)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Test with the latest PDF file
    pdf_path = "outputs/pdfs/Test_PDF_for_Conversion_20250815_135655_740033_26dbc566.pdf"
    test_pdf_extraction(pdf_path)

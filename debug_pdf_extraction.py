#!/usr/bin/env python3
"""
Debug script for PDF extraction
"""

import pdfplumber
import PyPDF2

def debug_pdf_extraction(pdf_path):
    print(f"🔍 Debugging PDF extraction: {pdf_path}")
    print("=" * 60)
    
    # Test pdfplumber
    print("\n📄 pdfplumber extraction:")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                print(f"Page {page_num} raw text:")
                print(repr(text))
                print(f"\nPage {page_num} formatted text:")
                print(text)
                print("-" * 40)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test PyPDF2
    print("\n📄 PyPDF2 extraction:")
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                print(f"Page {page_num} raw text:")
                print(repr(text))
                print(f"\nPage {page_num} formatted text:")
                print(text)
                print("-" * 40)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    pdf_path = "outputs/pdfs/Sample_Text_Document_20250815_140035_347905_e5cf47c3.pdf"
    debug_pdf_extraction(pdf_path)

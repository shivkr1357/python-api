#!/usr/bin/env python3
"""
Test script for improved PDF to PowerPoint conversion
"""

import requests
import json
import time
from datetime import datetime

class PDFConversionTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_pdf_conversion(self, pdf_path: str, output_name: str = None):
        """Test PDF to PowerPoint conversion with detailed feedback"""
        print(f"🔄 Testing PDF to PowerPoint conversion...")
        print(f"   PDF Path: {pdf_path}")
        
        if not output_name:
            output_name = f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conversion_data = {
            "pdf_path": pdf_path,
            "output_name": output_name,
            "include_images": True
        }
        
        try:
            response = self.session.post(f"{self.base_url}/convert/pdf-to-pptx", json=conversion_data)
            response.raise_for_status()
            result = response.json()
            
            if result['success']:
                print(f"✅ PowerPoint created successfully!")
                print(f"   File: {result['pptx_path']}")
                print(f"   Message: {result['message']}")
                return result
            else:
                print(f"❌ Conversion failed: {result.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error during conversion: {e}")
            return None
    
    def test_with_user_pdf(self):
        """Test with the user's specific PDF file"""
        print("🧪 Testing with User's PDF File")
        print("=" * 50)
        
        # Test with the user's PDF
        user_pdf_path = "/Users/pratikranpariya/Downloads/20220929183711.pdf"
        
        print(f"📄 Testing conversion of: {user_pdf_path}")
        
        # First, copy the file to our outputs directory
        import shutil
        import os
        
        try:
            if os.path.exists(user_pdf_path):
                output_pdf_path = "outputs/pdfs/user_document.pdf"
                shutil.copy2(user_pdf_path, output_pdf_path)
                print(f"✅ Copied PDF to: {output_pdf_path}")
                
                # Test conversion
                result = self.test_pdf_conversion(output_pdf_path, "user_document_conversion")
                
                if result:
                    print(f"\n📊 Conversion Summary:")
                    print(f"   - Original PDF: {user_pdf_path}")
                    print(f"   - PowerPoint created: {result['pptx_path']}")
                    print(f"   - Conversion time: {result['converted_at']}")
                    
                    # Check file sizes
                    original_size = os.path.getsize(user_pdf_path)
                    pptx_size = os.path.getsize(result['pptx_path'])
                    print(f"   - Original PDF size: {original_size} bytes ({original_size/1024:.1f} KB)")
                    print(f"   - PowerPoint size: {pptx_size} bytes ({pptx_size/1024:.1f} KB)")
                    
                    return result
                else:
                    print("❌ Conversion failed")
                    return None
            else:
                print(f"❌ PDF file not found: {user_pdf_path}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return None
    
    def test_with_sample_pdf(self):
        """Test with a sample PDF created by the API"""
        print("\n🧪 Testing with Sample PDF")
        print("=" * 50)
        
        # Create a sample PDF first
        pdf_data = {
            "title": "Sample Document for Conversion Test",
            "content": """
            This is a sample document created to test the PDF to PowerPoint conversion.
            
            Key Features:
            • Professional formatting
            • Multiple paragraphs
            • Bullet points
            • Structured content
            
            This document demonstrates the conversion capabilities of our API.
            The content should be properly extracted and formatted in the PowerPoint presentation.
            
            Technical Details:
            • PDF created using ReportLab
            • PowerPoint created using python-pptx
            • Text extraction using pdfplumber and PyPDF2
            • Automatic formatting and layout
            """,
            "author": "API Tester",
            "subject": "Conversion Testing",
            "keywords": ["test", "conversion", "pdf", "powerpoint"]
        }
        
        try:
            # Create PDF
            response = self.session.post(f"{self.base_url}/pdf/create", json=pdf_data)
            response.raise_for_status()
            pdf_result = response.json()
            
            if pdf_result['success']:
                print(f"✅ Sample PDF created: {pdf_result['pdf_path']}")
                
                # Test conversion
                result = self.test_pdf_conversion(pdf_result['pdf_path'], "sample_conversion")
                
                if result:
                    print(f"\n📊 Sample Conversion Summary:")
                    print(f"   - Sample PDF: {pdf_result['pdf_path']}")
                    print(f"   - PowerPoint created: {result['pptx_path']}")
                    
                    return result
                else:
                    print("❌ Sample conversion failed")
                    return None
            else:
                print(f"❌ Failed to create sample PDF: {pdf_result.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error in sample test: {e}")
            return None
    
    def list_all_files(self):
        """List all PDF and PowerPoint files"""
        print("\n📋 File Listing")
        print("=" * 50)
        
        try:
            # List PDFs
            response = self.session.get(f"{self.base_url}/pdf/list")
            response.raise_for_status()
            pdf_result = response.json()
            
            print("📄 PDF Files:")
            if pdf_result['pdfs']:
                for pdf in pdf_result['pdfs']:
                    print(f"   - {pdf['filename']} ({pdf['size_bytes']} bytes)")
            else:
                print("   No PDF files found")
            
            # List PowerPoints
            response = self.session.get(f"{self.base_url}/convert/list-pptx")
            response.raise_for_status()
            pptx_result = response.json()
            
            print("\n📊 PowerPoint Files:")
            if pptx_result['pptx_files']:
                for pptx in pptx_result['pptx_files']:
                    print(f"   - {pptx['filename']} ({pptx['size_bytes']} bytes)")
            else:
                print("   No PowerPoint files found")
                
        except Exception as e:
            print(f"❌ Error listing files: {e}")
    
    def run_comprehensive_test(self):
        """Run comprehensive conversion tests"""
        print("🚀 PDF to PowerPoint Conversion Test Suite")
        print("=" * 60)
        
        # Test 1: User's PDF
        user_result = self.test_with_user_pdf()
        
        # Test 2: Sample PDF
        sample_result = self.test_with_sample_pdf()
        
        # Test 3: List all files
        self.list_all_files()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Test Summary:")
        
        if user_result:
            print("✅ User PDF conversion: SUCCESS")
        else:
            print("❌ User PDF conversion: FAILED")
        
        if sample_result:
            print("✅ Sample PDF conversion: SUCCESS")
        else:
            print("❌ Sample PDF conversion: FAILED")
        
        print("\n💡 Notes:")
        print("   - If your PDF is image-based (scanned), the PowerPoint will contain information about this")
        print("   - For image-based PDFs, you'll need OCR software to extract text first")
        print("   - Text-based PDFs will convert with full content extraction")
        print("   - Check the generated PowerPoint files in the outputs/pptx directory")

def main():
    """Main function to run the conversion tests"""
    print("PDF to PowerPoint Conversion Test")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Wait a moment for user to read
    input("Press Enter to start testing...")
    
    # Create tester and run tests
    tester = PDFConversionTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()

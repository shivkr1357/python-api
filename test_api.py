#!/usr/bin/env python3
"""
Test script for the PDF to PowerPoint Converter API
This script demonstrates how to use the API endpoints
"""

import requests
import json
import time
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self) -> Dict[str, Any]:
        """Test the health check endpoint"""
        print("🔍 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Health check passed: {result['status']}")
            return result
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {"error": str(e)}
    
    def test_create_pdf(self) -> Dict[str, Any]:
        """Test PDF creation"""
        print("\n📄 Testing PDF creation...")
        
        pdf_data = {
            "title": "Sample API Test Document",
            "content": """
            This is a sample document created via the API.
            
            This document demonstrates the PDF creation capabilities of our FastAPI application.
            
            Key Features:
            • Professional formatting
            • Custom styling
            • Metadata support
            • Easy integration
            
            The document includes multiple paragraphs to test the formatting capabilities.
            Each paragraph should be properly spaced and formatted according to the defined styles.
            
            This is the end of our sample content.
            """,
            "author": "API Tester",
            "subject": "API Testing and Demonstration",
            "keywords": ["api", "test", "pdf", "fastapi", "mvc"]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/pdf/create", json=pdf_data)
            response.raise_for_status()
            result = response.json()
            print(f"✅ PDF created successfully: {result['pdf_path']}")
            return result
        except Exception as e:
            print(f"❌ PDF creation failed: {e}")
            return {"error": str(e)}
    
    def test_list_pdfs(self) -> Dict[str, Any]:
        """Test listing PDF files"""
        print("\n📋 Testing PDF listing...")
        try:
            response = self.session.get(f"{self.base_url}/pdf/list")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Found {result['count']} PDF files")
            for pdf in result['pdfs']:
                print(f"   - {pdf['filename']} ({pdf['size_bytes']} bytes)")
            return result
        except Exception as e:
            print(f"❌ PDF listing failed: {e}")
            return {"error": str(e)}
    
    def test_convert_pdf_to_pptx(self, pdf_path: str) -> Dict[str, Any]:
        """Test PDF to PowerPoint conversion"""
        print(f"\n🔄 Testing PDF to PowerPoint conversion...")
        
        conversion_data = {
            "pdf_path": pdf_path,
            "output_name": "converted_test_presentation",
            "include_images": True
        }
        
        try:
            response = self.session.post(f"{self.base_url}/convert/pdf-to-pptx", json=conversion_data)
            response.raise_for_status()
            result = response.json()
            print(f"✅ PowerPoint created successfully: {result['pptx_path']}")
            return result
        except Exception as e:
            print(f"❌ PDF to PowerPoint conversion failed: {e}")
            return {"error": str(e)}
    
    def test_list_pptx(self) -> Dict[str, Any]:
        """Test listing PowerPoint files"""
        print("\n📊 Testing PowerPoint listing...")
        try:
            response = self.session.get(f"{self.base_url}/convert/list-pptx")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Found {result['count']} PowerPoint files")
            for pptx in result['pptx_files']:
                print(f"   - {pptx['filename']} ({pptx['size_bytes']} bytes)")
            return result
        except Exception as e:
            print(f"❌ PowerPoint listing failed: {e}")
            return {"error": str(e)}
    
    def test_create_sample_pptx(self) -> Dict[str, Any]:
        """Test creating a sample PowerPoint"""
        print("\n🎯 Testing sample PowerPoint creation...")
        try:
            response = self.session.post(f"{self.base_url}/convert/create-sample-pptx")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Sample PowerPoint created: {result['filename']}")
            return result
        except Exception as e:
            print(f"❌ Sample PowerPoint creation failed: {e}")
            return {"error": str(e)}
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting API Tests")
        print("=" * 50)
        
        # Test health check
        health_result = self.test_health_check()
        if "error" in health_result:
            print("❌ API is not running. Please start the server first.")
            return
        
        # Test PDF creation
        pdf_result = self.test_create_pdf()
        if "error" in pdf_result:
            print("❌ Cannot proceed without PDF creation")
            return
        
        # Test PDF listing
        self.test_list_pdfs()
        
        # Test PDF to PowerPoint conversion
        pptx_result = self.test_convert_pdf_to_pptx(pdf_result['pdf_path'])
        
        # Test PowerPoint listing
        self.test_list_pptx()
        
        # Test sample PowerPoint creation
        self.test_create_sample_pptx()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        print(f"📄 PDF created: {pdf_result.get('pdf_path', 'N/A')}")
        if "pptx_path" in pptx_result:
            print(f"📊 PowerPoint created: {pptx_result['pptx_path']}")

def main():
    """Main function to run the API tests"""
    print("PDF to PowerPoint Converter API - Test Script")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Wait a moment for user to read
    input("Press Enter to start testing...")
    
    # Create tester and run tests
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

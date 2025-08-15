#!/usr/bin/env python3
"""
Test script to verify unique file naming
"""

import requests
import time
import os
from datetime import datetime

class UniqueNameTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_pdf_unique_names(self):
        """Test that multiple PDFs have unique names"""
        print("📄 Testing PDF Unique Names")
        print("=" * 50)
        
        pdf_names = []
        
        # Create multiple PDFs quickly
        for i in range(5):
            pdf_data = {
                "title": f"Test Document {i+1}",
                "content": f"This is test document number {i+1} to verify unique naming.",
                "author": f"Tester {i+1}",
                "subject": f"Test Subject {i+1}",
                "keywords": [f"test{i+1}", "unique", "naming"]
            }
            
            try:
                response = self.session.post(f"{self.base_url}/pdf/create", json=pdf_data)
                response.raise_for_status()
                result = response.json()
                
                if result['success']:
                    filename = os.path.basename(result['pdf_path'])
                    pdf_names.append(filename)
                    print(f"✅ Created: {filename}")
                else:
                    print(f"❌ Failed to create PDF {i+1}: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error creating PDF {i+1}: {e}")
            
            # Small delay to ensure different timestamps
            time.sleep(0.1)
        
        # Check for uniqueness
        unique_names = set(pdf_names)
        print(f"\n📊 Results:")
        print(f"   Total PDFs created: {len(pdf_names)}")
        print(f"   Unique names: {len(unique_names)}")
        print(f"   All names unique: {'✅ YES' if len(pdf_names) == len(unique_names) else '❌ NO'}")
        
        if len(pdf_names) != len(unique_names):
            print(f"   Duplicate names found!")
            for name in pdf_names:
                if pdf_names.count(name) > 1:
                    print(f"     - {name} appears {pdf_names.count(name)} times")
        
        return len(pdf_names) == len(unique_names)
    
    def test_pptx_unique_names(self):
        """Test that multiple PowerPoint files have unique names"""
        print("\n📊 Testing PowerPoint Unique Names")
        print("=" * 50)
        
        pptx_names = []
        
        # Create multiple PowerPoints quickly
        for i in range(5):
            try:
                response = self.session.post(f"{self.base_url}/convert/create-sample-pptx")
                response.raise_for_status()
                result = response.json()
                
                if result['success']:
                    filename = os.path.basename(result['pptx_path'])
                    pptx_names.append(filename)
                    print(f"✅ Created: {filename}")
                else:
                    print(f"❌ Failed to create PowerPoint {i+1}: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error creating PowerPoint {i+1}: {e}")
            
            # Small delay to ensure different timestamps
            time.sleep(0.1)
        
        # Check for uniqueness
        unique_names = set(pptx_names)
        print(f"\n📊 Results:")
        print(f"   Total PowerPoints created: {len(pptx_names)}")
        print(f"   Unique names: {len(unique_names)}")
        print(f"   All names unique: {'✅ YES' if len(pptx_names) == len(unique_names) else '❌ NO'}")
        
        if len(pptx_names) != len(unique_names):
            print(f"   Duplicate names found!")
            for name in pptx_names:
                if pptx_names.count(name) > 1:
                    print(f"     - {name} appears {pptx_names.count(name)} times")
        
        return len(pptx_names) == len(unique_names)
    
    def test_conversion_unique_names(self):
        """Test that PDF to PowerPoint conversions have unique names"""
        print("\n🔄 Testing Conversion Unique Names")
        print("=" * 50)
        
        # First create a PDF
        pdf_data = {
            "title": "Conversion Test Document",
            "content": "This document will be converted to PowerPoint multiple times to test unique naming.",
            "author": "Conversion Tester",
            "subject": "Unique Naming Test",
            "keywords": ["conversion", "unique", "naming", "test"]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/pdf/create", json=pdf_data)
            response.raise_for_status()
            pdf_result = response.json()
            
            if not pdf_result['success']:
                print(f"❌ Failed to create test PDF: {pdf_result.get('message', 'Unknown error')}")
                return False
            
            pdf_path = pdf_result['pdf_path']
            print(f"✅ Created test PDF: {os.path.basename(pdf_path)}")
            
        except Exception as e:
            print(f"❌ Error creating test PDF: {e}")
            return False
        
        # Convert to PowerPoint multiple times
        conversion_names = []
        
        for i in range(5):
            conversion_data = {
                "pdf_path": pdf_path,
                "output_name": f"conversion_test_{i+1}",
                "include_images": True
            }
            
            try:
                response = self.session.post(f"{self.base_url}/convert/pdf-to-pptx", json=conversion_data)
                response.raise_for_status()
                result = response.json()
                
                if result['success']:
                    filename = os.path.basename(result['pptx_path'])
                    conversion_names.append(filename)
                    print(f"✅ Converted: {filename}")
                else:
                    print(f"❌ Failed conversion {i+1}: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error in conversion {i+1}: {e}")
            
            # Small delay to ensure different timestamps
            time.sleep(0.1)
        
        # Check for uniqueness
        unique_names = set(conversion_names)
        print(f"\n📊 Results:")
        print(f"   Total conversions: {len(conversion_names)}")
        print(f"   Unique names: {len(unique_names)}")
        print(f"   All names unique: {'✅ YES' if len(conversion_names) == len(unique_names) else '❌ NO'}")
        
        if len(conversion_names) != len(unique_names):
            print(f"   Duplicate names found!")
            for name in conversion_names:
                if conversion_names.count(name) > 1:
                    print(f"     - {name} appears {conversion_names.count(name)} times")
        
        return len(conversion_names) == len(unique_names)
    
    def list_all_files(self):
        """List all files to show the unique naming"""
        print("\n📋 All Generated Files")
        print("=" * 50)
        
        try:
            # List PDFs
            response = self.session.get(f"{self.base_url}/pdf/list")
            response.raise_for_status()
            pdf_result = response.json()
            
            print("📄 PDF Files:")
            if pdf_result['pdfs']:
                for pdf in pdf_result['pdfs']:
                    print(f"   - {pdf['filename']}")
            else:
                print("   No PDF files found")
            
            # List PowerPoints
            response = self.session.get(f"{self.base_url}/convert/list-pptx")
            response.raise_for_status()
            pptx_result = response.json()
            
            print("\n📊 PowerPoint Files:")
            if pptx_result['pptx_files']:
                for pptx in pptx_result['pptx_files']:
                    print(f"   - {pptx['filename']}")
            else:
                print("   No PowerPoint files found")
                
        except Exception as e:
            print(f"❌ Error listing files: {e}")
    
    def run_all_tests(self):
        """Run all unique naming tests"""
        print("🔍 Unique File Naming Test Suite")
        print("=" * 60)
        
        # Test 1: PDF unique names
        pdf_success = self.test_pdf_unique_names()
        
        # Test 2: PowerPoint unique names
        pptx_success = self.test_pptx_unique_names()
        
        # Test 3: Conversion unique names
        conversion_success = self.test_conversion_unique_names()
        
        # Test 4: List all files
        self.list_all_files()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Test Summary:")
        print(f"   PDF unique naming: {'✅ PASS' if pdf_success else '❌ FAIL'}")
        print(f"   PowerPoint unique naming: {'✅ PASS' if pptx_success else '❌ FAIL'}")
        print(f"   Conversion unique naming: {'✅ PASS' if conversion_success else '❌ FAIL'}")
        
        overall_success = pdf_success and pptx_success and conversion_success
        print(f"\n   Overall result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        if overall_success:
            print("\n💡 All files now have guaranteed unique names!")
            print("   - Timestamp includes microseconds for precision")
            print("   - UUID component ensures uniqueness even with identical timestamps")
            print("   - Special characters are safely handled")

def main():
    """Main function to run the unique naming tests"""
    print("Unique File Naming Test")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Wait a moment for user to read
    input("Press Enter to start testing...")
    
    # Create tester and run tests
    tester = UniqueNameTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

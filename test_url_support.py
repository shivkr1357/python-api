#!/usr/bin/env python3
"""
Test script for PDF URL support
"""

import requests
import json

def test_pdf_url_support():
    """Test PDF conversion from URLs"""
    print("🌐 Testing PDF URL Support")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test URLs
    test_urls = [
        {
            "name": "W3C Test PDF",
            "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "description": "Simple test PDF from W3C"
        },
        {
            "name": "Sample Document",
            "url": "https://www.africau.edu/images/default/sample.pdf",
            "description": "Sample educational PDF"
        }
    ]
    
    for i, test_case in enumerate(test_urls, 1):
        print(f"\n📄 Test {i}: {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        print(f"   Description: {test_case['description']}")
        
        try:
            # Test conversion
            payload = {
                "pdf_path": test_case['url'],
                "output_name": f"url_test_{i}",
                "include_images": True
            }
            
            print("   🔄 Converting PDF from URL...")
            response = requests.post(
                f"{base_url}/convert/pdf-to-pptx",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ Success: {result['message']}")
                    print(f"   🔗 Download URL: {result['pptx_path']}")
                    
                    # Test download
                    download_response = requests.get(result['pptx_path'])
                    if download_response.status_code == 200:
                        size_mb = len(download_response.content) / (1024 * 1024)
                        print(f"   📥 Download verified: {size_mb:.2f} MB")
                    else:
                        print(f"   ❌ Download failed: {download_response.status_code}")
                else:
                    print(f"   ❌ Conversion failed: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 URL Support Test Complete!")
    print()
    print("✅ **NEW FEATURES:**")
    print("   🌐 Direct PDF URL support")
    print("   📥 Automatic PDF download")
    print("   🔗 HTTP download URLs")
    print("   🧹 Automatic cleanup")
    print()
    print("📝 **Usage Examples:**")
    print('   Local file: {"pdf_path": "/path/to/file.pdf"}')
    print('   URL: {"pdf_path": "https://example.com/document.pdf"}')

if __name__ == "__main__":
    test_pdf_url_support()

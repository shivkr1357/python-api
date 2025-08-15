#!/usr/bin/env python3
"""
Test script for the cleanup service functionality
"""

import requests
import time
import json
from datetime import datetime

class CleanupTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_cleanup_status(self):
        """Test getting cleanup service status"""
        print("🔍 Testing cleanup service status...")
        try:
            response = self.session.get(f"{self.base_url}/cleanup/status")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Cleanup status retrieved successfully")
            print(f"   Service running: {result['status']['service_running']}")
            print(f"   Cleanup interval: {result['status']['cleanup_interval_hours']} hours")
            print(f"   Files to be deleted: {result['status']['files_to_be_deleted']['total']}")
            print(f"   Total files: {result['status']['total_files']['total']}")
            return result
        except Exception as e:
            print(f"❌ Error getting cleanup status: {e}")
            return None
    
    def test_cleanup_config(self):
        """Test getting cleanup configuration"""
        print("\n⚙️ Testing cleanup configuration...")
        try:
            response = self.session.get(f"{self.base_url}/cleanup/config")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Cleanup config retrieved successfully")
            print(f"   PDF directory: {result['config']['pdf_directory']}")
            print(f"   PPTX directory: {result['config']['pptx_directory']}")
            print(f"   Cleanup interval: {result['config']['cleanup_interval_hours']} hours")
            print(f"   Service running: {result['config']['service_running']}")
            return result
        except Exception as e:
            print(f"❌ Error getting cleanup config: {e}")
            return None
    
    def test_start_cleanup_service(self):
        """Test starting the cleanup service"""
        print("\n🚀 Testing cleanup service start...")
        try:
            response = self.session.post(f"{self.base_url}/cleanup/start")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Cleanup service started successfully")
            print(f"   Message: {result['message']}")
            return result
        except Exception as e:
            print(f"❌ Error starting cleanup service: {e}")
            return None
    
    def test_stop_cleanup_service(self):
        """Test stopping the cleanup service"""
        print("\n🛑 Testing cleanup service stop...")
        try:
            response = self.session.post(f"{self.base_url}/cleanup/stop")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Cleanup service stopped successfully")
            print(f"   Message: {result['message']}")
            return result
        except Exception as e:
            print(f"❌ Error stopping cleanup service: {e}")
            return None
    
    def test_manual_cleanup(self):
        """Test manual cleanup"""
        print("\n🧹 Testing manual cleanup...")
        try:
            response = self.session.post(f"{self.base_url}/cleanup/manual")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Manual cleanup completed successfully")
            print(f"   Message: {result['message']}")
            print(f"   Files deleted: {result['result']['total_deleted']}")
            if result['result']['deleted_files']:
                print("   Deleted files:")
                for file_info in result['result']['deleted_files']:
                    print(f"     - {file_info['type']}: {file_info['filename']} ({file_info['size_bytes']} bytes)")
            return result
        except Exception as e:
            print(f"❌ Error performing manual cleanup: {e}")
            return None
    
    def create_test_files(self):
        """Create some test files to demonstrate cleanup"""
        print("\n📄 Creating test files for cleanup demonstration...")
        
        # Create a test PDF
        pdf_data = {
            "title": "Test File for Cleanup",
            "content": "This is a test file that will be cleaned up after 2 hours.",
            "author": "Cleanup Tester",
            "subject": "Cleanup Test",
            "keywords": ["test", "cleanup", "demo"]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/pdf/create", json=pdf_data)
            response.raise_for_status()
            pdf_result = response.json()
            print(f"✅ Test PDF created: {pdf_result['pdf_path']}")
            
            # Create a test PowerPoint
            response = self.session.post(f"{self.base_url}/convert/create-sample-pptx")
            response.raise_for_status()
            pptx_result = response.json()
            print(f"✅ Test PowerPoint created: {pptx_result['filename']}")
            
            return True
        except Exception as e:
            print(f"❌ Error creating test files: {e}")
            return False
    
    def run_all_tests(self):
        """Run all cleanup tests"""
        print("🧪 Cleanup Service Test Suite")
        print("=" * 50)
        
        # Test 1: Get cleanup status
        self.test_cleanup_status()
        
        # Test 2: Get cleanup config
        self.test_cleanup_config()
        
        # Test 3: Create test files
        self.create_test_files()
        
        # Test 4: Get status again to see new files
        print("\n📊 Checking status after creating test files...")
        self.test_cleanup_status()
        
        # Test 5: Test manual cleanup (will only delete files older than 2 hours)
        print("\n⚠️ Note: Manual cleanup will only delete files older than 2 hours.")
        print("   Since we just created the files, they won't be deleted yet.")
        self.test_manual_cleanup()
        
        # Test 6: Test service control
        print("\n🔄 Testing service control...")
        self.test_stop_cleanup_service()
        time.sleep(1)
        self.test_start_cleanup_service()
        
        print("\n" + "=" * 50)
        print("🎉 Cleanup service tests completed!")
        print("\n💡 Tips:")
        print("   - Files are automatically deleted after 2 hours")
        print("   - You can manually trigger cleanup anytime")
        print("   - Check /cleanup/status to see what files will be deleted")
        print("   - The service runs in the background automatically")

def main():
    """Main function to run cleanup tests"""
    print("Cleanup Service Test Script")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Wait a moment for user to read
    input("Press Enter to start testing...")
    
    # Create tester and run tests
    tester = CleanupTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

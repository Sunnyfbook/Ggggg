#!/usr/bin/env python3
"""
Test script for CamGrabber Admin API
Run this script to test all admin API endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:2626"  # Change this to your server URL
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class AdminAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def print_test(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        print()
    
    def test_health_check(self):
        """Test basic health check"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                self.print_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.print_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_admin_login(self):
        """Test admin login"""
        try:
            response = self.session.post(f"{self.base_url}/api/admin/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                user = data.get("user", {})
                self.print_test("Admin Login", True, f"Logged in as: {user.get('username')}")
                return True
            else:
                self.print_test("Admin Login", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.print_test("Admin Login", False, f"Error: {str(e)}")
            return False
    
    def test_get_stats(self):
        """Test getting admin stats"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = self.session.get(f"{self.base_url}/api/admin/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Get Stats", True, f"Views: {data.get('totalViews', 0)}, Downloads: {data.get('totalDownloads', 0)}")
                return True
            else:
                self.print_test("Get Stats", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Get Stats", False, f"Error: {str(e)}")
            return False
    
    def test_update_stats(self):
        """Test updating stats"""
        try:
            response = self.session.post(f"{self.base_url}/api/admin/stats", json={
                "action": "view",
                "fileId": "test_file_123",
                "title": "Test Video"
            })
            
            if response.status_code == 200:
                self.print_test("Update Stats", True, "Stats updated successfully")
                return True
            else:
                self.print_test("Update Stats", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Update Stats", False, f"Error: {str(e)}")
            return False
    
    def test_banner_ads(self):
        """Test banner ads management"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Test saving banner ads
            banner_data = {
                "top": "<script>console.log('Top Banner Ad');</script>",
                "middle": "<script>console.log('Middle Banner Ad');</script>",
                "bottom": "<script>console.log('Bottom Banner Ad');</script>",
                "sidebar": "<script>console.log('Sidebar Banner Ad');</script>"
            }
            
            response = self.session.post(f"{self.base_url}/api/admin/ads/banner", 
                                       json=banner_data, headers=headers)
            
            if response.status_code == 200:
                self.print_test("Save Banner Ads", True, "Banner ads saved successfully")
                return True
            else:
                self.print_test("Save Banner Ads", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Save Banner Ads", False, f"Error: {str(e)}")
            return False
    
    def test_vast_ads(self):
        """Test VAST ads management"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Test saving VAST ads
            vast_data = {
                "preRoll": "https://example.com/vast/preroll.xml",
                "midRoll": "https://example.com/vast/midroll.xml",
                "postRoll": "https://example.com/vast/postroll.xml"
            }
            
            response = self.session.post(f"{self.base_url}/api/admin/ads/vast", 
                                       json=vast_data, headers=headers)
            
            if response.status_code == 200:
                self.print_test("Save VAST Ads", True, "VAST ads saved successfully")
                return True
            else:
                self.print_test("Save VAST Ads", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Save VAST Ads", False, f"Error: {str(e)}")
            return False
    
    def test_get_ads(self):
        """Test getting ads configuration"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = self.session.get(f"{self.base_url}/api/admin/ads", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Get Ads Config", True, "Ads configuration retrieved")
                return True
            else:
                self.print_test("Get Ads Config", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Get Ads Config", False, f"Error: {str(e)}")
            return False
    
    def test_reactions(self):
        """Test reactions management"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Test saving reactions
            reactions_data = {
                "enabled": True,
                "like": True,
                "dislike": True,
                "share": False
            }
            
            response = self.session.post(f"{self.base_url}/api/admin/reactions", 
                                       json=reactions_data, headers=headers)
            
            if response.status_code == 200:
                self.print_test("Save Reactions", True, "Reactions saved successfully")
                return True
            else:
                self.print_test("Save Reactions", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Save Reactions", False, f"Error: {str(e)}")
            return False
    
    def test_api_settings(self):
        """Test API settings management"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Test saving API settings
            api_data = {
                "apiBaseUrl": "https://api.example.com",
                "apiKey": "test_api_key_123",
                "serverPort": 8080,
                "environment": "development"
            }
            
            response = self.session.post(f"{self.base_url}/api/admin/api", 
                                       json=api_data, headers=headers)
            
            if response.status_code == 200:
                self.print_test("Save API Settings", True, "API settings saved successfully")
                return True
            else:
                self.print_test("Save API Settings", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Save API Settings", False, f"Error: {str(e)}")
            return False
    
    def test_server_settings(self):
        """Test server settings management"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Test saving server settings
            server_data = {
                "serverName": "CamGrabber Test Server",
                "maxFileSize": 100,
                "rateLimit": 60
            }
            
            response = self.session.post(f"{self.base_url}/api/admin/server", 
                                       json=server_data, headers=headers)
            
            if response.status_code == 200:
                self.print_test("Save Server Settings", True, "Server settings saved successfully")
                return True
            else:
                self.print_test("Save Server Settings", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Save Server Settings", False, f"Error: {str(e)}")
            return False
    
    def test_metadata(self):
        """Test metadata management"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Test saving metadata
            metadata_data = {
                "siteTitle": "CamGrabber Test",
                "siteDescription": "Test video streaming platform",
                "siteKeywords": "test, video, streaming",
                "siteAuthor": "Test Team"
            }
            
            response = self.session.post(f"{self.base_url}/api/admin/metadata", 
                                       json=metadata_data, headers=headers)
            
            if response.status_code == 200:
                self.print_test("Save Metadata", True, "Metadata saved successfully")
                return True
            else:
                self.print_test("Save Metadata", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Save Metadata", False, f"Error: {str(e)}")
            return False
    
    def test_credentials(self):
        """Test credentials management"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            # Test updating credentials
            credentials_data = {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{self.base_url}/api/admin/credentials", 
                                       json=credentials_data, headers=headers)
            
            if response.status_code == 200:
                self.print_test("Update Credentials", True, "Credentials updated successfully")
                return True
            else:
                self.print_test("Update Credentials", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Update Credentials", False, f"Error: {str(e)}")
            return False
    
    def test_activity_logs(self):
        """Test activity logs"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = self.session.get(f"{self.base_url}/api/admin/activity", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Get Activity Logs", True, f"Retrieved {len(data)} activity logs")
                return True
            else:
                self.print_test("Get Activity Logs", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Get Activity Logs", False, f"Error: {str(e)}")
            return False
    
    def test_admin_logout(self):
        """Test admin logout"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = self.session.post(f"{self.base_url}/api/admin/logout", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Admin Logout", True, "Logged out successfully")
                return True
            else:
                self.print_test("Admin Logout", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Admin Logout", False, f"Error: {str(e)}")
            return False
    
    def test_admin_panel_access(self):
        """Test admin panel HTML access"""
        try:
            response = self.session.get(f"{self.base_url}/admin")
            
            if response.status_code == 200 and "html" in response.headers.get("content-type", ""):
                self.print_test("Admin Panel Access", True, "Admin panel HTML served successfully")
                return True
            else:
                self.print_test("Admin Panel Access", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Admin Panel Access", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting CamGrabber Admin API Tests")
        print("=" * 50)
        print(f"Base URL: {self.base_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print()
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Admin Login", self.test_admin_login),
            ("Get Stats", self.test_get_stats),
            ("Update Stats", self.test_update_stats),
            ("Save Banner Ads", self.test_banner_ads),
            ("Save VAST Ads", self.test_vast_ads),
            ("Get Ads Config", self.test_get_ads),
            ("Save Reactions", self.test_reactions),
            ("Save API Settings", self.test_api_settings),
            ("Save Server Settings", self.test_server_settings),
            ("Save Metadata", self.test_metadata),
            ("Update Credentials", self.test_credentials),
            ("Get Activity Logs", self.test_activity_logs),
            ("Admin Logout", self.test_admin_logout),
            ("Admin Panel Access", self.test_admin_panel_access),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.print_test(test_name, False, f"Unexpected error: {str(e)}")
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Admin API is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
        
        print("=" * 50)

def main():
    """Main function"""
    print("CamGrabber Admin API Test Suite")
    print("Make sure your server is running before starting tests.")
    print()
    
    # Get server URL from user
    server_url = input(f"Enter server URL (default: {BASE_URL}): ").strip()
    if not server_url:
        server_url = BASE_URL
    
    # Create tester and run tests
    tester = AdminAPITester(server_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 
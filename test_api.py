#!/usr/bin/env python3
"""
Simple test script to verify API endpoints work correctly
Run this after deploying your bot to test the API endpoints
"""

import requests
import json

# Update this with your actual bot URL
BOT_URL = "https://your-bot-url.onrender.com"

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BOT_URL}/api/health")
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Version: {data.get('version')}")
            print(f"Uptime: {data.get('uptime')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")

def test_file_info_endpoint():
    """Test the file info endpoint with a sample file ID"""
    # Replace with an actual file ID from your bot
    file_id = "123456"  # Example file ID
    
    try:
        response = requests.get(f"{BOT_URL}/api/file/{file_id}")
        print(f"File Info: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"File Name: {data.get('file_name')}")
            print(f"File Size: {data.get('file_size')}")
            print(f"File Type: {data.get('file_type')}")
            print(f"Stream URL: {data.get('stream_url')}")
            print(f"Download URL: {data.get('download_url')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"File info test failed: {e}")

def test_process_url_endpoint():
    """Test the process URL endpoint"""
    test_url = "https://example.com/video.mp4"
    
    try:
        response = requests.post(
            f"{BOT_URL}/api/process",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        print(f"Process URL: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Process URL test failed: {e}")

def test_cors_headers():
    """Test CORS headers are present"""
    try:
        response = requests.get(f"{BOT_URL}/api/health")
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        print("CORS Headers Check:")
        for header in cors_headers:
            value = response.headers.get(header)
            print(f"{header}: {value}")
            
    except Exception as e:
        print(f"CORS test failed: {e}")

if __name__ == "__main__":
    print("Testing API Endpoints...")
    print("=" * 50)
    
    test_health_endpoint()
    print("-" * 30)
    
    test_cors_headers()
    print("-" * 30)
    
    test_process_url_endpoint()
    print("-" * 30)
    
    test_file_info_endpoint()
    print("-" * 30)
    
    print("API Testing Complete!") 
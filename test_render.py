import requests
import json
import time

def test_render_deployment(base_url):
    """Test the Render deployment of Quran Grader API"""
    
    print(f"Testing Render deployment at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed!")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Model: {health_data.get('model_status')}")
            print(f"   Config: {health_data.get('configuration', {})}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=30)
        if response.status_code == 200:
            root_data = response.json()
            print(f"✅ Root endpoint passed!")
            print(f"   Message: {root_data.get('message')}")
            print(f"   Version: {root_data.get('version')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: API Documentation
    print("\n3. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=30)
        if response.status_code == 200:
            print(f"✅ API docs available at: {base_url}/docs")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")
    
    # Test 4: OpenAPI schema
    print("\n4. Testing OpenAPI schema...")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=30)
        if response.status_code == 200:
            print(f"✅ OpenAPI schema available")
        else:
            print(f"❌ OpenAPI schema failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OpenAPI schema error: {e}")
    
    # Test 5: CORS headers
    print("\n5. Testing CORS headers...")
    try:
        response = requests.options(f"{base_url}/grade_recitation/", timeout=30)
        headers = response.headers
        if 'access-control-allow-origin' in headers:
            print(f"✅ CORS headers present")
            print(f"   Allow-Origin: {headers.get('access-control-allow-origin')}")
        else:
            print(f"❌ CORS headers missing")
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Render deployment test completed!")
    print(f"📖 API Documentation: {base_url}/docs")
    print(f"🔍 Health Check: {base_url}/health")
    
    return True

if __name__ == "__main__":
    # Replace with your actual Render URL
    RENDER_URL = "https://your-service-name.onrender.com"
    
    print("Quran Grader API - Render Deployment Test")
    print("Replace 'your-service-name' with your actual Render service name")
    print()
    
    # Prompt for URL if using default
    if "your-service-name" in RENDER_URL:
        custom_url = input("Enter your Render URL (or press Enter to use example): ").strip()
        if custom_url:
            RENDER_URL = custom_url
    
    test_render_deployment(RENDER_URL)

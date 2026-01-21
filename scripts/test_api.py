"""Script to test the API endpoints (local and ngrok)."""

import requests
import sys
import json


def test_endpoint(url, endpoint_name):
    """Test an API endpoint."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {endpoint_name}: SUCCESS")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ {endpoint_name}: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint_name}: FAILED (Connection Error - Is the server running?)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {endpoint_name}: FAILED (Timeout)")
        return False
    except Exception as e:
        print(f"❌ {endpoint_name}: FAILED ({str(e)})")
        return False


def test_diff_endpoint(base_url):
    """Test the diff endpoint."""
    url = f"{base_url}/api/diff"
    test_data = {
        "source_content": "key1=value1\nkey2=value2",
        "target_content": "key1=value1\nkey2=value3",
        "normalize": True
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Diff Endpoint: SUCCESS")
            result = response.json()
            print(f"   Changes detected: {len(result.get('changes', []))}")
            print(f"   Summary: {json.dumps(result.get('summary', {}), indent=2)}")
            return True
        else:
            print(f"❌ Diff Endpoint: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Diff Endpoint: FAILED ({str(e)})")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("API Connection Test")
    print("=" * 60)
    
    # Get ngrok URL from user if provided
    if len(sys.argv) > 1:
        ngrok_url = sys.argv[1].rstrip('/')
    else:
        ngrok_url = None
        print("\n💡 Tip: Pass ngrok URL as argument: python test_api.py <ngrok-url>")
    
    local_url = "http://localhost:8000"
    
    print("\n📡 Testing Local API (http://localhost:8000)")
    print("-" * 60)
    
    local_health = test_endpoint(f"{local_url}/api/health", "Health Check (Local)")
    local_root = test_endpoint(f"{local_url}/", "Root Endpoint (Local)")
    
    if local_health and local_root:
        print("\n✅ Local API is working!")
        test_diff_endpoint(local_url)
    else:
        print("\n❌ Local API is not responding. Make sure the server is running:")
        print("   poetry run python scripts/run_api.py")
    
    if ngrok_url:
        print(f"\n🌐 Testing ngrok URL ({ngrok_url})")
        print("-" * 60)
        
        ngrok_health = test_endpoint(f"{ngrok_url}/api/health", "Health Check (ngrok)")
        ngrok_root = test_endpoint(f"{ngrok_url}/", "Root Endpoint (ngrok)")
        
        if ngrok_health and ngrok_root:
            print("\n✅ ngrok tunnel is working!")
            test_diff_endpoint(ngrok_url)
        else:
            print("\n❌ ngrok tunnel is not working. Check:")
            print("   1. Is ngrok running? (ngrok http 8000)")
            print("   2. Is the API server running?")
            print("   3. Is the ngrok URL correct?")
    else:
        print("\n💡 To test ngrok, run:")
        print("   python scripts/test_api.py https://your-ngrok-url.ngrok-free.app")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

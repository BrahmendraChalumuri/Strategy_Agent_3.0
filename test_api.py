import requests
import json

# Test the API endpoints
base_url = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_customers():
    """Test customers endpoint"""
    print("\n🔍 Testing customers endpoint...")
    try:
        response = requests.get(f"{base_url}/customers")
        print(f"✅ Customers: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Customers endpoint failed: {e}")
        return False

def test_generate_recommendations():
    """Test generate recommendations endpoint"""
    print("\n🔍 Testing generate recommendations endpoint...")
    try:
        payload = {"customer_id": "C001"}
        response = requests.post(
            f"{base_url}/generate-recommendations",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Generate recommendations: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Customer: {data.get('CustomerInfo', {}).get('CustomerName')}")
            print(f"Summary: {data.get('Summary', {})}")
            print(f"Files generated: {data.get('files_generated', {})}")
        else:
            print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Generate recommendations failed: {e}")
        return False

def test_get_json():
    """Test get JSON recommendations endpoint"""
    print("\n🔍 Testing get JSON recommendations endpoint...")
    try:
        response = requests.get(f"{base_url}/recommendations/C001/json")
        print(f"✅ Get JSON: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Summary: {data.get('Summary', {})}")
        else:
            print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Get JSON failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Strategy Agent 3.0 API")
    print("=" * 50)
    
    # Test all endpoints
    health_ok = test_health()
    customers_ok = test_customers()
    
    if health_ok and customers_ok:
        generate_ok = test_generate_recommendations()
        if generate_ok:
            test_get_json()
    
    print("\n" + "=" * 50)
    print("🏁 API testing completed!")

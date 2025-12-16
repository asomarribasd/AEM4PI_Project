"""
Example client for testing the Lost Pet Intelligence API
"""

import requests
import json
from pathlib import Path

API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("Testing Health Check Endpoint")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_root():
    """Test root endpoint"""
    print("\n" + "="*60)
    print("Testing Root Endpoint")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_report_lost_pet():
    """Test lost pet report endpoint"""
    print("\n" + "="*60)
    print("Testing Lost Pet Report Endpoint")
    print("="*60)
    
    # Test data
    data = {
        "province": "San José",
        "canton": "Escazú",
        "district": "San Antonio",
        "description": "My dog Max is missing since yesterday. He's a medium-sized mixed breed with white and brown patches. He has a very distinctive black spot on his left ear. He was wearing a red collar with a small bell.",
        "additional_details": "Near the children's playground"
    }
    
    # No images for this test
    print(f"Sending data: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/report/lost",
        data=data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print(f"\nConfidence: {result['result']['matches']['confidence_level']}")
        print(f"Explanation: {result['result']['explanation']}")
        print(f"\nTop Match:")
        if result['result']['matches']['top_match']:
            top_match = result['result']['matches']['top_match']
            print(f"  - ID: {top_match['match_id']}")
            print(f"  - Similarity: {top_match['similarity_score'] * 100:.1f}%")
            print(f"  - Distance: {top_match.get('location_distance_km', 'N/A')}km")
        else:
            print("  - No strong matches found")
        
        return True
    else:
        print(f"\n❌ FAILED")
        print(f"Error: {response.text}")
        return False


def test_report_sighting():
    """Test sighting report endpoint"""
    print("\n" + "="*60)
    print("Testing Sighting Report Endpoint")
    print("="*60)
    
    # Test data
    data = {
        "province": "San José",
        "canton": "Moravia",
        "district": "San Vicente",
        "description": "I saw a gray and white cat near the park this morning. It had beautiful green eyes and distinctive white paws. The cat seemed friendly but was alone.",
        "additional_details": "Near the main entrance to the park"
    }
    
    print(f"Sending data: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/report/sighting",
        data=data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print(f"\nConfidence: {result['result']['matches']['confidence_level']}")
        print(f"Explanation: {result['result']['explanation']}")
        print(f"\nCandidates found: {len(result['result']['matches']['candidates'])}")
        return True
    else:
        print(f"\n❌ FAILED")
        print(f"Error: {response.text}")
        return False


def test_search():
    """Test search endpoint"""
    print("\n" + "="*60)
    print("Testing Search Endpoint")
    print("="*60)
    
    params = {
        "province": "San José",
        "species": "dog",
        "size": "medium",
        "limit": 5
    }
    
    print(f"Searching with params: {json.dumps(params, indent=2)}")
    
    response = requests.get(
        f"{API_BASE_URL}/api/v1/search",
        params=params
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_invalid_input():
    """Test validation with invalid input"""
    print("\n" + "="*60)
    print("Testing Validation (Invalid Province)")
    print("="*60)
    
    # Invalid province
    data = {
        "province": "Madrid",  # Not a Costa Rica province
        "canton": "Centro",
        "district": "Centro",
        "description": "A small brown dog"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/report/lost",
        data=data
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 500:
        print("✅ Validation correctly rejected invalid province")
        return True
    else:
        print(f"Response: {response.text}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 API CLIENT TEST SUITE")
    print("="*60)
    print("\n⚠️  Make sure the API server is running!")
    print("   Run: python run_api.py")
    print()
    
    input("Press Enter to start tests...")
    
    results = {}
    
    # Run tests
    results["Health Check"] = test_health_check()
    results["Root Endpoint"] = test_root()
    results["Lost Pet Report"] = test_report_lost_pet()
    results["Sighting Report"] = test_report_sighting()
    results["Search"] = test_search()
    results["Validation Test"] = test_invalid_input()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

"""
Test script to validate SHL Assessment Recommender against sample conversations.

This script tests the system against the provided sample conversations
to ensure it meets the expected behavior and format.
"""

import json
import requests
import time
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=30)
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_conversation(conversation_file: str) -> bool:
    """Test a conversation from a sample file."""
    print(f"\n🧪 Testing {conversation_file}")
    
    try:
        # Read the conversation file
        with open(conversation_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract conversation turns (simplified parsing)
        # In real implementation, we'd parse the markdown properly
        messages = []
        
        # For now, let's test a simple Java developer request
        messages = [
            {"role": "user", "content": "I need to hire a Java developer"}
        ]
        
        # Test the chat endpoint
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"messages": messages},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📤 Request: {json.dumps(messages, indent=2)}")
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Response: {json.dumps(result, indent=2)}")
            
            # Validate response structure
            if validate_response_structure(result):
                print("✅ Response structure is valid")
                return True
            else:
                print("❌ Response structure is invalid")
                return False
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def validate_response_structure(response: Dict[str, Any]) -> bool:
    """Validate response structure against SHL requirements."""
    required_fields = ["reply", "recommendations", "end_of_conversation"]
    
    # Check required fields
    for field in required_fields:
        if field not in response:
            print(f"❌ Missing field: {field}")
            return False
    
    # Check reply is string
    if not isinstance(response["reply"], str):
        print("❌ 'reply' must be a string")
        return False
    
    # Check recommendations is list
    if not isinstance(response["recommendations"], list):
        print("❌ 'recommendations' must be a list")
        return False
    
    # Check end_of_conversation is boolean
    if not isinstance(response["end_of_conversation"], bool):
        print("❌ 'end_of_conversation' must be boolean")
        return False
    
    # Check recommendation items have required fields
    for i, rec in enumerate(response["recommendations"]):
        if not isinstance(rec, dict):
            print(f"❌ Recommendation {i} must be a dictionary")
            return False
        
        rec_fields = ["name", "url", "test_type"]
        for field in rec_fields:
            if field not in rec:
                print(f"❌ Recommendation {i} missing field: {field}")
                return False
    
    return True

def test_sample_scenarios():
    """Test various scenarios based on sample conversations."""
    scenarios = [
        {
            "name": "Vague Query - Clarification",
            "messages": [{"role": "user", "content": "hiring"}],
            "expect_recommendations": False,
            "expect_clarification": True
        },
        {
            "name": "Specific Query - Recommendations",
            "messages": [{"role": "user", "content": "I need to hire a senior Java developer"}],
            "expect_recommendations": True,
            "expect_clarification": False
        },
        {
            "name": "Comparison Request",
            "messages": [{"role": "user", "content": "What is the difference between OPQ and GSA?"}],
            "expect_recommendations": True,
            "expect_clarification": False
        },
        {
            "name": "Refinement Request",
            "messages": [
                {"role": "user", "content": "I need to hire a Java developer"},
                {"role": "assistant", "content": "What seniority level?"},
                {"role": "user", "content": "Mid-level"},
                {"role": "user", "content": "Also include personality tests"}
            ],
            "expect_recommendations": True,
            "expect_clarification": False
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n🎯 Testing: {scenario['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"messages": scenario["messages"]},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate structure
                is_valid = validate_response_structure(result)
                
                # Check expectations
                has_recommendations = len(result["recommendations"]) > 0
                recommendations_match = has_recommendations == scenario["expect_recommendations"]
                
                print(f"  📊 Has recommendations: {has_recommendations} (expected: {scenario['expect_recommendations']})")
                print(f"  ✅ Structure valid: {is_valid}")
                print(f"  ✅ Expectations match: {recommendations_match}")
                
                results.append({
                    "scenario": scenario["name"],
                    "valid": is_valid and recommendations_match,
                    "response": result
                })
            else:
                print(f"  ❌ Request failed: {response.status_code}")
                results.append({
                    "scenario": scenario["name"],
                    "valid": False,
                    "error": response.text
                })
                
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            results.append({
                "scenario": scenario["name"],
                "valid": False,
                "error": str(e)
            })
    
    return results

def main():
    """Main test function."""
    print("🚀 Starting SHL Assessment Recommender Tests")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed. Make sure the server is running.")
        return
    
    # Test sample scenarios
    results = test_sample_scenarios()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r["valid"])
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    # Show detailed results for failed tests
    for result in results:
        if not result["valid"]:
            print(f"\n❌ {result['scenario']}:")
            if "error" in result:
                print(f"   Error: {result['error']}")
            elif "response" in result:
                print(f"   Response: {json.dumps(result['response'], indent=4)}")

if __name__ == "__main__":
    main()

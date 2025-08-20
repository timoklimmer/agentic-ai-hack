"""
Sample test script to demonstrate the Azure Function usage.
This script shows how to test the function endpoints locally.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:7071/api"
TEST_CLAIMS = [
    {
        "claim_details": "Vehicle collision on highway resulting in $15,000 damage to front end. Driver reported hitting a deer at 60 mph. No injuries reported.",
        "claim_id": "CL002"
    },
    {
        "claim_details": "Rear-end collision at traffic light. Estimated $8,500 in damage to rear bumper and trunk. Minor whiplash injury reported.",
        "claim_id": "CL001"
    },
    {
        "claim_details": "Comprehensive claim for hail damage. Multiple dents across hood, roof, and trunk. Estimated repair cost $12,000."
    }
]

def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing health check endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            result = response.json()
            print(f"   Service: {result.get('service', 'Unknown')}")
            print(f"   Status: {result.get('status', 'Unknown')}")
            print(f"   Version: {result.get('version', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {str(e)}")
        return False
    
    return True

def test_cosmos_connection():
    """Test the Cosmos DB connection endpoint."""
    print("\n🗄️ Testing Cosmos DB connection...")
    
    try:
        response = requests.get(f"{BASE_URL}/test-cosmos")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Cosmos DB test completed!")
            print(f"   Result: {result.get('cosmos_test_result', 'No result')}")
        else:
            print(f"⚠️ Cosmos DB test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cosmos DB test error: {str(e)}")

def test_claim_processing():
    """Test the claim processing endpoint with sample claims."""
    print("\n🔍 Testing claim processing endpoint...")
    
    for i, claim in enumerate(TEST_CLAIMS, 1):
        print(f"\n📋 Testing claim {i}...")
        print(f"   Details: {claim['claim_details'][:50]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/claim",
                json=claim,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Claim processing successful!")
                
                if result.get('status') == 'success':
                    analyses = result.get('agent_analyses', [])
                    print(f"   📊 Received {len(analyses)} agent analyses")
                    
                    for analysis in analyses:
                        agent_name = analysis.get('agent_name', 'Unknown')
                        analysis_text = analysis.get('analysis', '')
                        
                        # Extract key information from analysis
                        if 'CLAIM STATUS:' in analysis_text:
                            status_line = [line for line in analysis_text.split('\n') if 'CLAIM STATUS:' in line]
                            if status_line:
                                print(f"   🔍 {agent_name}: {status_line[0].strip()}")
                        elif 'RISK LEVEL:' in analysis_text:
                            risk_line = [line for line in analysis_text.split('\n') if 'RISK LEVEL:' in line]
                            if risk_line:
                                print(f"   ⚠️ {agent_name}: {risk_line[0].strip()}")
                        elif 'COVERAGE:' in analysis_text:
                            coverage_line = [line for line in analysis_text.split('\n') if 'COVERAGE:' in line]
                            if coverage_line:
                                print(f"   📋 {agent_name}: {coverage_line[0].strip()}")
                        else:
                            print(f"   🤖 {agent_name}: Analysis completed")
                else:
                    print(f"❌ Claim processing failed: {result.get('error_message', 'Unknown error')}")
                    
            else:
                print(f"❌ HTTP Error {response.status_code}")
                try:
                    error_result = response.json()
                    print(f"   Error: {error_result.get('error_message', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {str(e)}")
        
        # Add delay between requests
        if i < len(TEST_CLAIMS):
            print("   ⏳ Waiting before next test...")
            time.sleep(2)

def test_get_method():
    """Test the GET method for claim processing."""
    print("\n🌐 Testing GET method for claim processing...")
    
    test_claim = TEST_CLAIMS[0]
    params = {
        'claim_details': test_claim['claim_details'],
        'claim_id': test_claim.get('claim_id', '')
    }
    
    try:
        response = requests.get(f"{BASE_URL}/claim", params=params)
        
        if response.status_code == 200:
            print("✅ GET method test successful!")
            result = response.json()
            if result.get('status') == 'success':
                print(f"   📊 Received {len(result.get('agent_analyses', []))} agent analyses")
            else:
                print(f"   ❌ Processing failed: {result.get('error_message', 'Unknown error')}")
        else:
            print(f"❌ GET method test failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ GET method test error: {str(e)}")

def main():
    """Run all tests."""
    print("🧪 Azure Function Test Suite")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Health check failed. Make sure the function is running with 'func start'")
        return
    
    # Test Cosmos DB connection
    test_cosmos_connection()
    
    # Test claim processing (POST method)
    test_claim_processing()
    
    # Test GET method
    test_get_method()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n💡 Tips:")
    print("   - Make sure your local.settings.json is configured correctly")
    print("   - Check that your Azure services are accessible")
    print("   - Monitor the function logs for detailed information")

if __name__ == "__main__":
    main()

"""
Test file for the Azure Function orchestrator.
"""

import asyncio
import json
from orchestrator.semantic_orchestrator import InsuranceClaimOrchestrator

async def test_orchestrator():
    """Test the orchestrator functionality."""
    
    print("🧪 Testing Insurance Claim Orchestrator...")
    
    try:
        # Create test claim details
        test_claim_details = "Vehicle collision on highway resulting in $15,000 damage to front end. Driver reported hitting a deer at 60 mph. No injuries reported."
        test_claim_id = "CL002"
        
        # Test with orchestrator
        async with InsuranceClaimOrchestrator() as orchestrator:
            print("📋 Processing test claim...")
            result = await orchestrator.process_claim(test_claim_details, test_claim_id)
            
            print("✅ Test completed!")
            print("\n📊 Results:")
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())

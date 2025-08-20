"""
Semantic Kernel Orchestrator for Insurance Claim Processing
This module provides the core orchestration logic extracted from the notebook.
"""

import asyncio
import os
import logging
from typing import Dict, Any, Optional
from datetime import timedelta
from azure.identity.aio import DefaultAzureCredential, ClientSecretCredential
from semantic_kernel.agents import (
    AzureAIAgent, 
    ConcurrentOrchestration
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.agents.open_ai.run_polling_options import RunPollingOptions

from .tools import CosmosDBPlugin

logger = logging.getLogger(__name__)

class InsuranceClaimOrchestrator:
    """
    Main orchestrator class for insurance claim processing using Semantic Kernel agents.
    """
    
    def __init__(self):
        self.agents = {}
        self.client = None
        self.runtime = None
        
    async def initialize(self):
        """Initialize the orchestrator with specialized agents."""
        try:
            logger.info("🔧 Initializing specialized insurance agents...")
            self.agents, self.client = await self._create_specialized_agents()
            self.runtime = InProcessRuntime()
            self.runtime.start()
            logger.info("✅ Orchestrator initialized successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {str(e)}")
            raise

    async def _create_specialized_agents(self):
        """Create our specialized insurance processing agents using Semantic Kernel."""
        
        logger.info("🔧 Creating specialized insurance agents...")
        
        # Create Cosmos DB plugin instances for different agents
        cosmos_plugin_claims = CosmosDBPlugin()
        cosmos_plugin_risk = CosmosDBPlugin()
        
        # Get environment variables
        endpoint = os.environ.get("AI_FOUNDRY_PROJECT_ENDPOINT")
        model_deployment = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
        
        # Get authentication details
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        
        if not endpoint:
            raise ValueError("AI_FOUNDRY_PROJECT_ENDPOINT environment variable is required")
        
        agents = {}
        
        # Use service principal credentials if available, otherwise fall back to default
        if client_id and client_secret and tenant_id:
            logger.info("🔐 Using service principal authentication...")
            creds = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            logger.info("🔐 Using default Azure credentials...")
            creds = DefaultAzureCredential()
        
        async with creds:
            client = AzureAIAgent.create_client(credential=creds, endpoint=endpoint)
            
            # Create Claim Reviewer Agent with Cosmos DB access
            logger.info("🔍 Creating Claim Reviewer Agent...")
            claim_reviewer_definition = await client.agents.create_agent(
                model=model_deployment,
                name="ClaimReviewer",
                description="Expert Insurance Claim Reviewer Agent specialized in analyzing and validating insurance claims",
                instructions="""You are an expert Insurance Claim Reviewer Agent specialized in analyzing and validating insurance claims. Your primary responsibilities include:

**Core Functions:**
- Review claim documentation and assess completeness
- Analyze damage assessments and cost estimates
- Validate claim details against policy requirements
- Identify inconsistencies or missing information
- Provide detailed assessments with specific recommendations

**Analysis Guidelines:**
1. Use the Cosmos DB plugin to retrieve claim data by claim_id
2. Examine all claim details including dates, amounts, and descriptions
3. Assess the reasonableness of damage estimates
4. Check for proper documentation and evidence
5. Identify any red flags or unusual patterns

**Response Format:**
- Start with CLAIM STATUS: VALID/QUESTIONABLE/INVALID
- Provide detailed analysis of claim components
- List any missing documentation or concerns
- Give specific recommendations for next steps
- Be thorough but concise in your assessment

Use the available Cosmos DB functions to retrieve and analyze claim data."""
            )
            
            claim_reviewer_agent = AzureAIAgent(
                client=client,
                definition=claim_reviewer_definition,
                plugins=[cosmos_plugin_claims],
                polling_options=RunPollingOptions(default_polling_interval=timedelta(milliseconds=3000))
            )
            
            # Create Risk Analyzer Agent with Cosmos DB access
            logger.info("⚠️ Creating Risk Analyzer Agent...")
            risk_analyzer_definition = await client.agents.create_agent(
                model=model_deployment,
                name="RiskAnalyzer",
                description="Expert Insurance Risk Analysis Agent specialized in detecting fraud patterns and assessing claim authenticity",
                instructions="""You are an expert Insurance Risk Analysis Agent specialized in detecting fraud patterns and assessing claim authenticity. Your primary responsibilities include:

**Core Functions:**
- Evaluate risk factors and fraud indicators
- Detect suspicious patterns in claim data
- Assess claim authenticity and credibility
- Analyze historical claim patterns
- Provide risk scores and recommendations

**Risk Assessment Guidelines:**
1. Use the Cosmos DB plugin to retrieve and analyze claim data
2. Look for unusual patterns, timing, or amounts
3. Check for consistency in claim details
4. Identify potential fraud indicators
5. Assess overall risk profile of the claim

**Fraud Indicators to Watch For:**
- Unusual timing of claims
- Inconsistent damage descriptions
- Suspicious amount patterns
- Multiple recent claims
- Geographic or temporal clustering

**Response Format:**
- Start with RISK LEVEL: LOW/MEDIUM/HIGH
- Provide detailed risk analysis
- List specific fraud indicators found (if any)
- Give risk score (1-10 scale)
- Recommend investigation actions if needed

Use the available Cosmos DB functions to thoroughly analyze claim data for risk assessment."""
            )
            
            risk_analyzer_agent = AzureAIAgent(
                client=client,
                definition=risk_analyzer_definition,
                plugins=[cosmos_plugin_risk],
                polling_options=RunPollingOptions(default_polling_interval=timedelta(milliseconds=3000))
            )
            
            # Create Policy Checker Agent (without Cosmos DB as it uses Azure AI Search)
            logger.info("📋 Creating Policy Checker Agent...")
            policy_checker_definition = await client.agents.create_agent(
                model=model_deployment,
                name="PolicyChecker",
                description="Expert Insurance Policy Analysis Agent specialized in validating policy coverage and claim eligibility",
                instructions="""You are an expert Insurance Policy Analysis Agent specialized in validating policy coverage and claim eligibility. Your primary responsibilities include:

**Core Functions:**
- Analyze insurance policy terms and conditions
- Validate claim coverage under policy provisions
- Interpret policy limits, deductibles, and exclusions
- Determine eligibility for specific claim types
- Provide clear coverage determinations

**Policy Types You Handle:**
- Commercial Auto Policies
- Comprehensive Auto Policies  
- High Value Vehicle Policies
- Liability Only Policies
- Motorcycle Policies

**Analysis Guidelines:**
1. Review policy documents for relevant coverage
2. Check claim details against policy terms
3. Identify applicable limits, deductibles, and exclusions
4. Assess coverage eligibility
5. Provide clear determination with policy references

**Response Format:**
- Start with COVERAGE: COVERED/NOT COVERED/PARTIAL COVERAGE
- Reference specific policy sections
- Explain coverage limits and deductibles
- List any exclusions that apply
- Provide clear reasoning for determination

Provide professional, accurate, and thorough policy analysis."""
            )
            
            policy_checker_agent = AzureAIAgent(
                client=client,
                definition=policy_checker_definition,
                polling_options=RunPollingOptions(default_polling_interval=timedelta(milliseconds=3000))
            )
            
            agents = {
                'claim_reviewer': claim_reviewer_agent,
                'risk_analyzer': risk_analyzer_agent,
                'policy_checker': policy_checker_agent
            }
            
            logger.info("✅ All specialized agents created successfully!")
            return agents, client

    async def process_claim(self, claim_id: str) -> Dict[str, Any]:
        """
        Orchestrate multiple agents to process an insurance claim concurrently using only the claim ID.
        
        Args:
            claim_id: The claim ID for database lookup and analysis
            
        Returns:
            Dict containing the analysis results from all agents
        """
        
        if not self.agents or not self.client or not self.runtime:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        logger.info(f"🚀 Starting Concurrent Insurance Claim Processing Orchestration")
        logger.info(f"🔍 Processing Claim ID: {claim_id}")
        
        try:
            # Create concurrent orchestration with all three agents
            orchestration = ConcurrentOrchestration(
                members=[self.agents['claim_reviewer'], self.agents['risk_analyzer'], self.agents['policy_checker']]
            )
            
            logger.info(f"🎯 Processing insurance claim with all agents working simultaneously")
            
            # Create task that instructs agents to retrieve claim details first
            task = f"""Analyze the insurance claim with ID: {claim_id}

INSTRUCTIONS FOR ALL AGENTS:
1. First, use the get_document_by_claim_id() function to retrieve the complete claim details for claim ID: {claim_id}
2. Then analyze the retrieved claim data from your specialized perspective

AGENT-SPECIFIC INSTRUCTIONS:

Claim Reviewer Agent: 
- Retrieve claim details using get_document_by_claim_id("{claim_id}")
- Review all claim documentation and assess completeness
- Validate damage estimates and repair costs
- Check for proper evidence and documentation
- Provide VALID/QUESTIONABLE/INVALID determination

Risk Analyzer Agent:
- Retrieve claim data using get_document_by_claim_id("{claim_id}")
- Analyze for fraud indicators and suspicious patterns
- Assess claim authenticity and credibility
- Check for unusual timing, amounts, or circumstances
- Provide LOW/MEDIUM/HIGH risk assessment

Policy Checker Agent:
- Retrieve claim details using get_document_by_claim_id("{claim_id}") if needed for context
- Analyze policy coverage for this type of claim
- Determine if claim is covered under policy terms
- Identify relevant exclusions, limits, or deductibles
- Provide COVERED/NOT COVERED/PARTIAL COVERAGE determination
- Reference specific policy sections

Each agent should provide comprehensive analysis from your area of expertise based on the retrieved claim data."""
            
            logger.info(f"📋 Task assigned to all agents:")
            logger.info(f"   • Claim Reviewer: Retrieve and validate claim documentation")
            logger.info(f"   • Risk Analyzer: Retrieve and assess fraud risk")
            logger.info(f"   • Policy Checker: Determine coverage eligibility")
            
            # Invoke concurrent orchestration
            orchestration_result = await orchestration.invoke(
                task=task,
                runtime=self.runtime
            )
            
            # Get results from all agents
            results = await orchestration_result.get(timeout=300)  # 5 minute timeout
            
            logger.info(f"🎉 All agents completed their analysis!")
            
            # Format results for API response
            formatted_results = {}
            agent_analyses = []
            
            for i, result in enumerate(results, 1):
                agent_name = result.name if hasattr(result, 'name') else f"Agent {i}"
                content = str(result.content)
                
                agent_analyses.append({
                    "agent_name": agent_name,
                    "analysis": content
                })
                
                logger.info(f"🤖 {agent_name} Analysis completed")
            
            # Create comprehensive analysis report
            comprehensive_analysis = f"""# 🏢 Insurance Claim Analysis Report

## 📋 Claim Information
**Claim ID:** {claim_id}

## 🔍 Multi-Agent Concurrent Analysis Results

{chr(10).join([f"### {result['agent_name']} Assessment:{chr(10)}{chr(10)}{result['analysis']}{chr(10)}" for result in agent_analyses])}

## 📊 Summary and Recommendations

Based on the comprehensive concurrent analysis from our specialized AI agents:

1. **Claim Validity**: Assessed by our Claim Reviewer for documentation completeness and accuracy
2. **Risk Profile**: Evaluated by our Risk Analyzer for fraud indicators and authenticity
3. **Policy Coverage**: Determined by our Policy Checker for coverage eligibility and terms

**Next Steps**: This multi-agent analysis provides a thorough foundation for claim processing decisions. Review all agent assessments and follow their specific recommendations.

---
*Generated through concurrent multi-agent orchestration using Azure AI Agent Service and Semantic Kernel*
*Analysis completed simultaneously by specialized insurance processing agents*
*Claim data automatically retrieved from Cosmos DB using Claim ID: {claim_id}*
"""
            
            formatted_results = {
                "status": "success",
                "claim_id": claim_id,
                "agent_analyses": agent_analyses,
                "comprehensive_analysis": comprehensive_analysis,
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            logger.info("✅ Concurrent Insurance Claim Orchestration Complete!")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error during orchestration: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "claim_id": claim_id
            }

    async def cleanup(self):
        """Clean up orchestrator resources."""
        try:
            if self.runtime:
                await self.runtime.stop_when_idle()
                logger.info("🧹 Orchestration cleanup complete.")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

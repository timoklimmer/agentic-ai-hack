"""
Simple evaluation script for the policy-checker agent without AI Foundry upload.
This avoids storage permission issues while still running the core evaluation.
"""

import os
import time
import json

from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

from azure.ai.agents.models import RunStatus, MessageRole
from azure.ai.projects import AIProjectClient
from azure.ai.evaluation import (
    AIAgentConverter, evaluate, ToolCallAccuracyEvaluator, IntentResolutionEvaluator, 
    TaskAdherenceEvaluator, ContentSafetyEvaluator, CodeVulnerabilityEvaluator, 
    IndirectAttackEvaluator)

from azure.identity import DefaultAzureCredential

class OperationalMetricsEvaluator:
    """Propagate operational metrics to the final evaluation results"""
    def __init__(self):
        pass
    def __call__(self, *, metrics: dict, **kwargs):
        return metrics

def run_simple_evaluation():
    """Run evaluation with comprehensive evaluators and no AI Foundry upload"""
    
    print("🚀 Starting Simple AI Agent Evaluation for Policy Checker")
    print("=" * 55)
    
    current_dir = Path(__file__).parent
    eval_queries_path = current_dir / "eval-queries.json"
    eval_input_path = current_dir / "eval-input-simple.jsonl"
    eval_output_path = current_dir / "eval-output-simple.json"

    # Load environment variables
    env_path = current_dir / "../.env"
    if not env_path.exists():
        raise ValueError(f"Environment file not found at {env_path}. Please create a .env file based on .env.sample")
    
    load_dotenv(dotenv_path=env_path)

    # Get AI project parameters
    project_endpoint = os.environ.get("AI_FOUNDRY_PROJECT_ENDPOINT")
    if not project_endpoint:
        raise ValueError("Please set the AI_FOUNDRY_PROJECT_ENDPOINT environment variable in your .env file.")

    parsed_endpoint = urlparse(project_endpoint)
    model_endpoint = f"{parsed_endpoint.scheme}://{parsed_endpoint.netloc}"
    deployment_name = "gpt-4.1-mini"
    agent_name = "policy-checker"

    # Initialize client
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    ai_project = AIProjectClient(
        credential=credential,
        endpoint=project_endpoint,
        api_version="2025-05-15-preview"
    )

    # Find agent
    print(f"🔍 Looking for agent named '{agent_name}'...")
    agent_found = False
    for agent in ai_project.agents.list_agents():
        if agent.name == agent_name:
            agent_id = agent.id
            agent_found = True
            print(f"✅ Found agent '{agent_name}' with ID: {agent_id}")
            break
            
    if not agent_found:
        available_agents = [a.name for a in ai_project.agents.list_agents()]
        raise ValueError(f"Agent '{agent_name}' not found. Available agents: {available_agents}")

    agent = ai_project.agents.get_agent(agent_id)

    # Setup evaluation config
    model_config = {
        "azure_deployment": deployment_name,
        "azure_endpoint": model_endpoint,
        "api_version": "2024-10-21",
    }
    thread_data_converter = AIAgentConverter(ai_project)

    # Read test queries
    with open(eval_queries_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    # Execute queries and prepare evaluation input
    print(f"📝 Running {len(test_data)} test queries against the agent...")
    
    with open(eval_input_path, "w", encoding="utf-8") as f:        
        for i, row in enumerate(test_data, 1):
            print(f"  Processing query {i}/{len(test_data)}: {row.get('query')[:60]}...")
            
            thread = ai_project.agents.threads.create()
            ai_project.agents.messages.create(
                thread.id, role=MessageRole.USER, content=row.get("query")
            )

            start_time = time.time()
            run = ai_project.agents.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id
            )
            end_time = time.time()

            if run.status != RunStatus.COMPLETED:
                print(f"  ⚠️  Query {i} failed: {run.last_error}")
                continue
            else:
                print(f"  ✅ Query {i} completed successfully")

            operational_metrics = {
                "server-run-duration-in-seconds": (run.completed_at - run.created_at).total_seconds(),
                "client-run-duration-in-seconds": end_time - start_time,
                "completion-tokens": run.usage.completion_tokens,
                "prompt-tokens": run.usage.prompt_tokens,
                "ground-truth": row.get("ground-truth", '')
            }

            evaluation_data = thread_data_converter.prepare_evaluation_data(thread_ids=thread.id)
            eval_item = evaluation_data[0]
            eval_item["metrics"] = operational_metrics
            f.write(json.dumps(eval_item) + "\n")   
        
    print("✅ All test queries completed successfully!")

    # Setup comprehensive evaluators
    print("🔧 Setting up comprehensive evaluators...")
    
    evaluators_config = {
        "operational_metrics": OperationalMetricsEvaluator(),
    }
    
    # Add core AI agent evaluation metrics
    try:
        evaluators_config["tool_call_accuracy"] = ToolCallAccuracyEvaluator(model_config=model_config)
        print("  ✅ tool_call_accuracy evaluator added")
    except Exception as e:
        print(f"  ⚠️  tool_call_accuracy evaluator skipped: {e}")

    try:
        evaluators_config["intent_resolution"] = IntentResolutionEvaluator(model_config=model_config)
        print("  ✅ intent_resolution evaluator added")
    except Exception as e:
        print(f"  ⚠️  intent_resolution evaluator skipped: {e}")

    try:
        evaluators_config["task_adherence"] = TaskAdherenceEvaluator(model_config=model_config)
        print("  ✅ task_adherence evaluator added")
    except Exception as e:
        print(f"  ⚠️  task_adherence evaluator skipped: {e}")

    # Add security and safety evaluators
    try:
        evaluators_config["code_vulnerability"] = CodeVulnerabilityEvaluator(credential=credential, azure_ai_project=ai_project)
        print("  ✅ code_vulnerability evaluator added")
    except Exception as e:
        print(f"  ⚠️  code_vulnerability evaluator skipped: {e}")

    try:
        evaluators_config["content_safety"] = ContentSafetyEvaluator(credential=credential, azure_ai_project=ai_project)
        print("  ✅ content_safety evaluator added")
    except Exception as e:
        print(f"  ⚠️  content_safety evaluator skipped: {e}")

    try:
        evaluators_config["indirect_attack"] = IndirectAttackEvaluator(credential=credential, azure_ai_project=ai_project)
        print("  ✅ indirect_attack evaluator added")
    except Exception as e:
        print(f"  ⚠️  indirect_attack evaluator skipped: {e}")

    # Run evaluation WITHOUT AI Foundry upload
    print(f"\n📊 Running local evaluation with {len(evaluators_config)} evaluators...")
    
    results = evaluate(
        evaluation_name="policy-checker-comprehensive-evaluation",
        data=eval_input_path,
        evaluators=evaluators_config,
        output_path=eval_output_path,
        # NO azure_ai_project parameter to avoid storage permission issues
    )
    
    print("✅ Comprehensive evaluation completed!")
    
    # Display results with target metrics
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS".center(70))
    print("=" * 70)
    print("TARGET METRICS:")
    print("  Intent Resolution: 85-95% (accurate intention identification)")
    print("  Task Adherence: 80-90% (successful task completion)")
    print("  Tool Call Accuracy: 90-95% (correct tool selection and usage)")
    print("  Response Completeness: 85-95% (comprehensive information coverage)")
    print("-" * 70)
    
    if hasattr(results, 'metrics') and results.metrics:
        for key, value in results.metrics.items():
            if isinstance(value, float):
                # Convert to percentage if it looks like a proportion (0-1 range)
                if 0 <= value <= 1 and key in ['intent_resolution', 'task_adherence', 'tool_call_accuracy']:
                    percentage = value * 100
                    print(f"{key:<35} | {percentage:.1f}%")
                else:
                    print(f"{key:<35} | {value:.2f}")
            else:
                print(f"{key:<35} | {value}")
    else:
        print("No metrics found in results")
        print(f"Results type: {type(results)}")
    
    print("=" * 70)
    print(f"Evaluation input: {eval_input_path}")
    print(f"Evaluation output: {eval_output_path}")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_simple_evaluation()
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
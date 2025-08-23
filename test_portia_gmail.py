from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    Portia,
    StorageClass,
    LLMProvider,
)
from portia.cli import CLIExecutionHooks
import os

load_dotenv()

def test_gmail_behavior():
    openai_key = os.getenv("OPENAI_API_KEY")
    portia_key = os.getenv("PORTIA_API_KEY")
    
    if not openai_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return
    
    if not portia_key:
        print("❌ Error: PORTIA_API_KEY not found in .env file")
        return
    
    print("🤖 Testing Portia Gmail Behavior")
    print("=" * 40)
    
    config = Config.from_default(
        storage_class=StorageClass.CLOUD,
        llm_provider=LLMProvider.OPENAI,
        openai_api_key=openai_key,
        portia_api_key=portia_key
    )
    
    portia = Portia(
        config=config,
        tools=DefaultToolRegistry(config),
        execution_hooks=CLIExecutionHooks(),
    )
    
    test_tasks = [
        {
            "name": "Complex Email Task",
            "task": """
            Send a professional email to suryanshg2050@gmail.com with:
            - Subject: Project Update
            - Body: Here is the latest update on our project progress
            - Make it professional and friendly
            """
        }
    ]
    
    for i, test_task in enumerate(test_tasks, 1):
        print(f"\n🧪 Test {i}: {test_task['name']}")
        print(f"📝 Task: {test_task['task']}")
        print("⏳ Executing...")
        
        try:
            plan_run = portia.run(test_task['task'], end_user="test_user")
            
            print("✅ Task completed!")
            print(f"📋 Result: {plan_run.outputs.final_output}")
            
            if "authentication" in str(plan_run.outputs).lower() or "login" in str(plan_run.outputs).lower():
                print("🔐 Authentication was required")
            else:
                print("✅ No authentication needed (already authenticated)")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_gmail_behavior()
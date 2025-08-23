from portia import (
    Config,
    DefaultToolRegistry,
    Portia,
    StorageClass,
    LLMProvider,
)
from portia.cli import CLIExecutionHooks
import os

class PortiaClient:
    def __init__(self, openai_api_key: str, user_id: str):
        self.openai_api_key = openai_api_key
        self.user_id = user_id
    
    def create_portia_instance(self):
        """Create a Portia instance with user's configuration"""
        config = Config.from_default(
            storage_class=StorageClass.CLOUD,
            llm_provider=LLMProvider.OPENAI,
            openai_api_key=self.openai_api_key,
            portia_api_key=os.getenv("PORTIA_API_KEY")
        )
        
        return Portia(
            config=config,
            tools=DefaultToolRegistry(config),
            execution_hooks=CLIExecutionHooks(),
        )
    
    async def run_task(self, task: str):
        """Run a Portia task"""
        try:
            portia = self.create_portia_instance()
            plan_run = portia.run(task, end_user=self.user_id)
            
            return {
                "success": True,
                "result": plan_run.outputs.final_output,
                "user_id": self.user_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "user_id": self.user_id
            }
    
    async def plan_task(self, task: str):
        """Plan a task without executing"""
        try:
            portia = self.create_portia_instance()
            plan = portia.plan(task)
            
            return {
                "success": True,
                "result": plan.pretty_print(),
                "user_id": self.user_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "user_id": self.user_id
            }
    
    @staticmethod
    async def test_openai_key(openai_api_key: str) -> bool:
        """Test if OpenAI API key is valid"""
        try:
            config = Config.from_default(
                storage_class=StorageClass.MEMORY,
                llm_provider=LLMProvider.OPENAI,
                openai_api_key=openai_api_key
            )
            
            portia = Portia(
                config=config,
                tools=DefaultToolRegistry(config),
                execution_hooks=CLIExecutionHooks(),
            )
            
            # Try a simple task to test the key
            plan_run = portia.run("Say hello")
            return True
        except Exception:
            return False
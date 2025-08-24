from portia import (
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification,
    PlanRunState,
    Portia,
    PortiaToolRegistry,
    default_config,
)
import os

class PortiaClient:
    def __init__(self, openai_api_key: str, user_id: str):
        self.openai_api_key = openai_api_key
        self.user_id = user_id
        os.environ["OPENAI_API_KEY"] = openai_api_key
        if os.getenv("PORTIA_API_KEY"):
            os.environ["PORTIA_API_KEY"] = os.getenv("PORTIA_API_KEY")
    
    def create_portia_instance(self):
        return Portia(tools=PortiaToolRegistry(default_config()))
    
    async def run_task(self, task: str):
        try:
            portia = self.create_portia_instance()
            
            plan = portia.plan(task)
            plan_run = portia.run_plan(plan, end_user=self.user_id)
            
            while plan_run.state == PlanRunState.NEED_CLARIFICATION:
                for clarification in plan_run.get_outstanding_clarifications():
                    if isinstance(clarification, ActionClarification):
                        return {
                            "success": False,
                            "error": "OAuth authentication required",
                            "result": f"OAuth required: {clarification.user_guidance}",
                            "needs_oauth": True,
                            "oauth_url": str(clarification.action_url),
                            "user_id": self.user_id
                        }
                    
                    elif isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
                        return {
                            "success": False,
                            "error": "User input required",
                            "result": f"Input needed: {clarification.user_guidance}",
                            "needs_input": True,
                            "user_id": self.user_id
                        }
                
                break
            
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
    
    def _run_task_sync(self, task: str):
        try:
            portia = self.create_portia_instance()
            plan = portia.plan(task)
            plan_run = portia.run_plan(plan, end_user=self.user_id)
            
            while plan_run.state == PlanRunState.NEED_CLARIFICATION:
                for clarification in plan_run.get_outstanding_clarifications():
                    if isinstance(clarification, ActionClarification):
                        return {
                            "success": False,
                            "error": "OAuth authentication required",
                            "result": f"OAuth required: {clarification.user_guidance}",
                            "needs_oauth": True,
                            "oauth_url": str(clarification.action_url),
                            "user_id": self.user_id
                        }
                break
            
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
        try:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            portia = Portia(tools=PortiaToolRegistry(default_config()))
            plan = portia.plan("Say hello")
            plan_run = portia.run_plan(plan)
            return True
        except Exception:
            return False
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
        config = Config.from_default(
            storage_class=StorageClass.CLOUD,
            llm_provider=LLMProvider.OPENAI,
            openai_api_key=self.openai_api_key,
            portia_api_key=os.getenv("PORTIA_API_KEY"),
        )

        return Portia(
            config=config,
            tools=DefaultToolRegistry(config),
            execution_hooks=CLIExecutionHooks(),
        )

    async def run_task(self, task: str):
        import asyncio
        import re
        import threading
        import time
        import sys
        import io
        from contextlib import redirect_stdout, redirect_stderr

        oauth_url_found = threading.Event()
        oauth_url = None
        captured_output = io.StringIO()

        def run_portia_with_capture():
            nonlocal oauth_url, oauth_url_found, captured_output

            try:
                with redirect_stdout(captured_output), redirect_stderr(captured_output):
                    portia = self.create_portia_instance()
                    plan_run = portia.run(task, end_user=self.user_id)

                    return {
                        "success": True,
                        "result": plan_run.outputs.final_output,
                        "user_id": self.user_id,
                    }
            except Exception as e:
                return {"success": False, "error": str(e), "user_id": self.user_id}

        task_result = [None]

        def run_and_store():
            task_result[0] = run_portia_with_capture()

        portia_thread = threading.Thread(target=run_and_store, daemon=True)
        portia_thread.start()

        start_time = time.time()
        while time.time() - start_time < 60:
            output_content = captured_output.getvalue()

            if output_content and not oauth_url_found.is_set():
                url_match = re.search(
                    r"https://accounts\.google\.com/o/oauth2/v2/auth[^\s\)]+",
                    output_content,
                )
                if url_match:
                    oauth_url = url_match.group(0)
                    oauth_url_found.set()

                    return {
                        "success": False,
                        "error": "OAuth authentication required",
                        "result": f"OAuth required for google: Click the link below to authenticate. {oauth_url}",
                        "needs_oauth": True,
                        "oauth_url": oauth_url,
                        "user_id": self.user_id,
                    }

            if not portia_thread.is_alive():
                if task_result[0]:
                    return task_result[0]
                break

            await asyncio.sleep(0.2)

        if task_result[0]:
            return task_result[0]

        return {
            "success": False,
            "error": "Task timed out",
            "result": f"Captured output: {captured_output.getvalue()[:500]}...",
            "user_id": self.user_id,
        }

    def _run_task_sync(self, task: str):
        portia = self.create_portia_instance()
        plan_run = portia.run(task, end_user=self.user_id)

        return {
            "success": True,
            "result": plan_run.outputs.final_output,
            "user_id": self.user_id,
        }

    async def plan_task(self, task: str):
        try:
            portia = self.create_portia_instance()
            plan = portia.plan(task)

            return {
                "success": True,
                "result": plan.pretty_print(),
                "user_id": self.user_id,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "user_id": self.user_id}

    @staticmethod
    async def test_openai_key(openai_api_key: str) -> bool:
        try:
            config = Config.from_default(
                storage_class=StorageClass.MEMORY,
                llm_provider=LLMProvider.OPENAI,
                openai_api_key=openai_api_key,
            )

            portia = Portia(
                config=config,
                tools=DefaultToolRegistry(config),
                execution_hooks=CLIExecutionHooks(),
            )

            plan_run = portia.run("Say hello")
            return True
        except Exception:
            return False

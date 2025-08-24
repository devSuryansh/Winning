from models.gmail_models import (
    SendEmailRequest,
    SendEmailResponse,
    AutomatedEmailRequest,
)
from services.portia_client import PortiaClient


class GmailService:
    def __init__(self, openai_api_key: str, user_id: str):
        self.client = PortiaClient(openai_api_key, user_id)

    async def send_email(self, request: SendEmailRequest) -> SendEmailResponse:
        try:
            task = f"""
            Send an email to {request.to} with subject '{request.subject}' and body: {request.body}
            Make it professional and friendly.
            """

            result = await self.client.run_task(task)

            result_text = str(result.get("result", ""))
            needs_auth = (
                "oauth" in result_text.lower()
                or "authentication" in result_text.lower()
                or "clarification" in result_text.lower()
            )

            oauth_url = None
            if needs_auth:
                import re

                url_patterns = [
                    r"https://accounts\.google\.com/o/oauth2/v2/auth[^\s\)]+",
                    r"https://accounts\.google\.com[^\s\)]+",
                ]

                for pattern in url_patterns:
                    url_match = re.search(pattern, result_text)
                    if url_match:
                        oauth_url = url_match.group(0)
                        break

                if not oauth_url and result.get("error"):
                    error_text = str(result.get("error", ""))
                    for pattern in url_patterns:
                        url_match = re.search(pattern, error_text)
                        if url_match:
                            oauth_url = url_match.group(0)
                            break

            return SendEmailResponse(
                success=result["success"],
                result=result.get("result"),
                error=result.get("error"),
                user_id=self.client.user_id,
                needs_authentication=needs_auth,
                oauth_url=oauth_url,
            )

        except Exception as e:
            return SendEmailResponse(
                success=False, error=str(e), user_id=self.client.user_id
            )

    async def send_automated_email(
        self, request: AutomatedEmailRequest
    ) -> SendEmailResponse:
        try:
            task = f"""
            Send an email to {request.to} with subject '{request.subject}'.
            Generate appropriate professional email content based on the subject line.
            Make the email body relevant to the subject, professional, and engaging.
            """

            result = await self.client.run_task(task)

            result_text = str(result.get("result", ""))
            needs_auth = (
                result.get("needs_oauth", False)
                or "oauth" in result_text.lower()
                or "authentication" in result_text.lower()
                or "clarification" in result_text.lower()
            )

            oauth_url = result.get("oauth_url")
            if not oauth_url and needs_auth:
                import re

                url_patterns = [
                    r"https://accounts\.google\.com/o/oauth2/v2/auth[^\s\)]+",
                    r"https://accounts\.google\.com[^\s\)]+",
                ]

                for pattern in url_patterns:
                    url_match = re.search(pattern, result_text)
                    if url_match:
                        oauth_url = url_match.group(0)
                        break

                if not oauth_url and result.get("error"):
                    error_text = str(result.get("error", ""))
                    for pattern in url_patterns:
                        url_match = re.search(pattern, error_text)
                        if url_match:
                            oauth_url = url_match.group(0)
                            break

            return SendEmailResponse(
                success=result["success"],
                result=str(result.get("result", "")),
                error=str(result.get("error", "")) if result.get("error") else None,
                user_id=self.client.user_id,
                needs_authentication=needs_auth,
                oauth_url=oauth_url,
            )

        except Exception as e:
            return SendEmailResponse(
                success=False, error=str(e), user_id=self.client.user_id
            )

    async def send_automated_email_simple(
        self, to: str, subject: str
    ) -> SendEmailResponse:
        request = AutomatedEmailRequest(to=to, subject=subject)
        return await self.send_automated_email(request)

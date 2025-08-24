from models.gmail_models import SendEmailRequest, SendEmailResponse, AutomatedEmailRequest
from services.portia_client import PortiaClient

class GmailService:
    def __init__(self, openai_api_key: str, user_id: str):
        self.client = PortiaClient(openai_api_key, user_id)
    
    
    async def send_automated_email(self, request: AutomatedEmailRequest) -> SendEmailResponse:
        try:
            task = f"""
            Send an email to {request.to} with subject '{request.subject}'.
            Generate appropriate professional email content based on the subject line.
            Make the email body relevant to the subject, professional, and engaging.
            """
            
            result = await self.client.run_task(task)
            
            return SendEmailResponse(
                success=result["success"],
                result=str(result.get("result", "")),
                error=str(result.get("error", "")) if result.get("error") else None,
                user_id=self.client.user_id,
                needs_authentication=result.get("needs_oauth", False),
                oauth_url=result.get("oauth_url")
            )

        except Exception as e:
            return SendEmailResponse(
                success=False,
                error=str(e),
                user_id=self.client.user_id
            )
    
    async def send_automated_email_simple(self, to: str, subject: str) -> SendEmailResponse:
        request = AutomatedEmailRequest(to=to, subject=subject)
        return await self.send_automated_email(request)
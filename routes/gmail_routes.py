from fastapi import APIRouter, Depends
from models.gmail_models import (
    SendEmailRequest,
    SendEmailResponse,
    AutomatedEmailRequest,
)
from services.gmail_service import GmailService
from routes.auth_routes import get_current_user

router = APIRouter()


@router.post("/send-email", response_model=SendEmailResponse)
async def send_email(
    request: AutomatedEmailRequest, token_data: dict = Depends(get_current_user)
):
    service = GmailService(token_data["openai_api_key"], token_data["user_id"])
    return await service.send_automated_email(request)

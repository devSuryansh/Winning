from pydantic import BaseModel, EmailStr
from typing import Optional


class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


class AutomatedEmailRequest(BaseModel):
    to: EmailStr
    subject: str


class SendEmailResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    user_id: str
    service: str = "gmail"
    action: str = "send_email"
    needs_authentication: bool = False
    oauth_url: Optional[str] = None

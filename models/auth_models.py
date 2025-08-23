from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    openai_api_key: str
    user_id: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class TaskRequest(BaseModel):
    task: str

class TaskResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    user_id: str
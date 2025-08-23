from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from models.auth_models import LoginRequest, LoginResponse
from services.portia_client import PortiaClient

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 

class AuthService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            openai_api_key: str = payload.get("openai_api_key")
            user_id: str = payload.get("user_id")
            
            if openai_api_key is None or user_id is None:
                return None
            
            return {"openai_api_key": openai_api_key, "user_id": user_id}
        except JWTError:
            return None
    
    @staticmethod
    async def login(request: LoginRequest) -> LoginResponse:
        """Login with OpenAI API key and get JWT token"""
        is_valid = await PortiaClient.test_openai_key(request.openai_api_key)
        
        if not is_valid:
            raise ValueError("Invalid OpenAI API key")
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={
                "openai_api_key": request.openai_api_key,
                "user_id": request.user_id
            },
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=request.user_id
        )
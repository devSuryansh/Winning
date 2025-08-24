from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from models.auth_models import LoginRequest, LoginResponse
from services.portia_client import PortiaClient
import uuid
import aiohttp

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
        is_valid = await AuthService.test_openai_key_fast(request.openai_api_key)

        if not is_valid:
            raise ValueError("Invalid OpenAI API key")

        user_id = str(uuid.uuid4())

        access_token = AuthService.create_access_token(
            data={"openai_api_key": request.openai_api_key, "user_id": user_id}
        )

        return LoginResponse(
            access_token=access_token, token_type="bearer", user_id=user_id
        )

    @staticmethod
    async def test_openai_key_fast(openai_api_key: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json",
                }

                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 5,
                }

                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=5,
                ) as response:
                    return response.status == 200

        except Exception:
            return False

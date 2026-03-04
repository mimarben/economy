import jwt
import os
from datetime import datetime, timedelta

SECRET = os.getenv("JWT_SECRET")


def create_token(user_id: int):

    payload = {
        "sub": user_id,
        "exp": datetime.now(datetime.timezone.utc) + timedelta(hours=2)
    }

    return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token: str):

    return jwt.decode(token, SECRET, algorithms=["HS256"])

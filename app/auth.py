import jwt
from datetime import datetime, timedelta, timezone  # Changed from UTC
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from app.settings import get_settings
from typing import Optional

settings = get_settings()
async def verify_jwt_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.security.jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")




def generate_long_lived_jwt(outlet_id: Optional[int] = None, multiuser_id: Optional[int]= None, data: Optional[dict] = None, expires_in_days: int = 3650) -> str:
    now     = datetime.now(timezone.utc)
    payload = {
        "sub": "system-access",
        "scope": "internal-api",
        "iat": now,
        "exp": now + timedelta(days=expires_in_days),
        "outlet_id": outlet_id,
        "multiuser_id": multiuser_id
        }
    token = jwt.encode(payload, settings.security.jwt_secret, algorithm="HS256")
    return token
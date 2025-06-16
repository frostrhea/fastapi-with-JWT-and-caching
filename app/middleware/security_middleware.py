from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.auth.redis import is_token_blacklisted, add_to_blacklist
from app.auth.jwt import decode_token
import jwt

async def get_current_user(token: str) -> str:
    # Check if the token is blacklisted
    if await is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been blacklisted.\nUnauthorized: Please log in")

    try:
        # Decode the access token
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Token is invalid or expired.\nUnauthorized: Please log in",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def check_token_blacklist(request: Request, call_next):
    token = request.cookies.get("access_token")
    if token and is_token_blacklisted(token):
        return JSONResponse(status_code=403, content={"detail": "Token is blacklisted"})
    response = await call_next(request)
    return response
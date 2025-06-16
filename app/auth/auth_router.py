from fastapi import APIRouter, Depends, Response, HTTPException, Request, Cookie
from app.models.user import UserLogin, Token
from app.auth.jwt import create_token, decode_token
from app.database.users import get_user
from app.auth.security import verify_password
from datetime import timedelta
from app.auth.redis import is_token_blacklisted, add_to_blacklist
import jwt
import time

from app.core.config import settings

router = APIRouter(prefix="/auth")

# Custom dependency to extract JWT token from the Authorization header
def get_jwt_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token_type, token = auth_header.split(" ")
    if token_type.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid token format")
    return token

# Login endpoint
# This endpoint generates both access and refresh tokens upon successful login
@router.post("/token", response_model=Token)
def login(user: UserLogin, response: Response):
    db_user = get_user(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_token({"sub": user.username}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token({"sub": user.username}, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    # Store refresh token in HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # set to True in production
        samesite="Strict"  # or "Lax" depending on app's flow
    )
    return Token(access_token=access_token)


# Refresh token endpoint
# This endpoint generates a new access token using the refresh token
@router.post("/refresh", response_model=Token)
async def refresh_token(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    # Check if the refresh token is blacklisted
    if await is_token_blacklisted(refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token has been invalidated")

    try:
        # Decode the refresh token to get payload
        payload = decode_token(refresh_token)
        username = payload.get("sub")
        exp = payload.get("exp")
        
        if username is None or exp is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Blacklist the old tokens
    await add_to_blacklist(refresh_token, timedelta(seconds=exp - int(time.time())))  # Expiration relative to current time

    # Create new tokens
    access_token = create_token({"sub": username}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    new_refresh = create_token({"sub": username}, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    # Set the new refresh token in the cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,     # only over HTTPS in production
        samesite="Strict"  # or "Lax", depending on frontend behavior
    )

    return Token(access_token=access_token)


# Logout endpoint
# This endpoint invalidates both the access and refresh tokens
# NOTE: for client/frontend side, remove the access token from local storage to fully log out the user
@router.post("/logout")
async def logout(request: Request, response: Response, access_token: str = Depends(get_jwt_token)):
    # Get the refresh token from the cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token is missing")

    # Decode the refresh token to get the expiration time
    try:
        payload = decode_token(refresh_token)
        exp = payload.get("exp")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if exp:
        # Calculate the remaining expiration time
        expiration_time = timedelta(seconds=exp - int(time.time()))  # Time remaining for the token

        # Store both the refresh token and access token in Redis (blacklist them)
        await add_to_blacklist(refresh_token, expiration_time)
        await add_to_blacklist(access_token, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    # Remove the refresh token cookie
    response.delete_cookie("refresh_token")

    return {"message": "Logged out successfully"}

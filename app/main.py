from typing import Union

from fastapi import FastAPI
from app.middleware.security_middleware import check_token_blacklist
from app.auth.auth_router import router as auth_router
from app.secure.endpoints import router as secure_router

app = FastAPI()

# Add the middleware globally
@app.middleware("http")
async def blacklist_middleware(request, call_next):
    return await check_token_blacklist(request, call_next)

app.include_router(auth_router)
app.include_router(secure_router)

@app.get("/")
def read_root():
    return {"Hello World": "A Sample FastAPI application with JWT authentication and Redis caching"}


from fastapi import APIRouter, Depends
from app.middleware.security_middleware import get_current_user
from app.cache.cache_decorator import cached
# 
router = APIRouter(prefix="/secure")

@router.get("/data")
def read_secure_data(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}. You have access to secure data."}

# FOR CACHE TESTING
# Simulate a computationally heavy task (e.g., Fibonacci calculation)
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@router.get("/heavy-task")
@cached(ttl=60)  # Cache the result for 60 seconds
async def heavy_task(n: int, current_user: str = Depends(get_current_user)):
    result = fibonacci(n)  # Simulate a heavy computation
    return {"message": f"Hello, {current_user}. The result of Fibonacci({n}) is {result}."}
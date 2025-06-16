# FastAPI JWT Authentication & Redis Caching Example

This project demonstrates a FastAPI application with JWT authentication (access & refresh tokens), Redis-based token blacklisting, and Redis caching for heavy computations.

---

## Features

- **JWT Authentication**: Secure login, token refresh, and logout using access and refresh tokens.
- **Token Blacklisting**: Redis is used to blacklist tokens on logout or refresh, preventing reuse.
- **Protected Endpoints**: Access to certain endpoints requires a valid, non-blacklisted JWT.
- **Caching**: Heavy computations can be cached in Redis for performance.
- **Environment-based Configuration**: Uses `.env` for secrets and settings.
- **Test Coverage**: Example test for the refresh token flow.

---

## Requirements

- Python 3.10+
- Redis server (local or Docker)

---

## Setup

1. **Clone the repository**  
   ```bash
   git clone <repo-url>
   cd fastapi_setup
2. **Create and activate a virtual environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
4. **Configure environment variables:**
    Edit or review .env for secrets and Redis settings.
    - Example `.env` file:
    ```env
    SECRET_KEY=your-super-secret-key   # Secret key for JWT signing
    ALGORITHM=HS256                    # JWT algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES=15     # Access token expiry (minutes)
    REFRESH_TOKEN_EXPIRE_DAYS=7        # Refresh token expiry (days)
    ENABLE_CACHE=true                  # Enable Redis caching (true/false)
    REDIS_HOST=localhost               # Redis server hostname
    REDIS_PORT=6379                    # Redis server port
    REDIS_DB=0                         # Redis database index
5. **Start Redis**
    Linux:
    ```bash
    sudo systemctl start redis
6. **Run the application**
    ```bash
    uvicorn app.main:app --reload

---

## Usage

### Authentication Endpoints

- **POST `/auth/token`**  
  Login with JSON body:  
  ```json
  { "username": "test", "password": "admin123" }
  ```
  Returns:  
  ```json
  { "access_token": "<jwt>" }
  ```
  Sets: `refresh_token` as HTTP-only cookie.

- **POST `/auth/refresh`**  
  Use the `refresh_token` cookie to get a new access token.  
  Returns:  
  ```json
  { "access_token": "<new_jwt>" }
  ```
  Sets: new `refresh_token` cookie.

- **POST `/auth/logout`**  
  Blacklists both access and refresh tokens, removes the `refresh_token` cookie.

### Protected Endpoints

- **GET `/secure/data`**  
  Requires a valid (non-blacklisted) access token in the `Authorization` header:  
  ```
  Authorization: Bearer <access_token>
  ```

- **GET `/secure/heavy-task?n=20`**  
  Requires authentication. Returns a cached result for the Fibonacci calculation.

---
#### Note: You can also access the interactive documentation by accessing the /docs or redoc endpoints!

---

## Project Structure

```
app/
  ├── auth/         # Authentication logic (JWT, Redis blacklist)
  ├── cache/        # Caching config and decorators
  ├── core/         # App settings/config
  ├── database/     # User database (example)
  ├── middleware/   # Security middleware
  ├── models/       # Pydantic models
  ├── secure/       # Protected endpoints
  └── main.py       # FastAPI app entrypoint
```

---

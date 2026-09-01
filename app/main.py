import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from app.auth import User, authenticate, create_token, current_user, require_reviewer
from app.config import Settings, get_settings
from app.llm import MockLLMProvider
from app.logging_config import configure_logging, security_event
from app.models import ChatRequest, ChatResponse, LoginRequest, TokenResponse, UserResponse
from app.rate_limit import limiter
from app.service import chat

configure_logging()
logger = logging.getLogger("application")
provider = MockLLMProvider()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    logger.info("application_started", extra={"reason": settings.environment})
    yield


app = FastAPI(
    title="Secure LLM Application",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:64]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers.update(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; base-uri 'none'; frame-ancestors 'none'",
            "Cache-Control": "no-store",
            "X-Request-ID": request_id,
        }
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, _: RequestValidationError):
    security_event("invalid_input", request_id=request.state.request_id, reason="schema_validation")
    return JSONResponse(
        status_code=422,
        content={"detail": "Request validation failed", "request_id": request.state.request_id},
    )


@app.exception_handler(Exception)
async def unexpected_error(request: Request, error: Exception):
    logger.exception("unhandled_error", extra={"request_id": request.state.request_id})
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": request.state.request_id},
    )


def client_key(request: Request) -> str:
    # Do not trust X-Forwarded-For unless a configured trusted proxy validates it.
    return request.client.host if request.client else "unknown"


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/app.js", include_in_schema=False)
async def javascript():
    return FileResponse(
        Path(__file__).parent / "static" / "app.js", media_type="application/javascript"
    )


@app.get("/static.css", include_in_schema=False)
async def stylesheet():
    return FileResponse(Path(__file__).parent / "static" / "static.css", media_type="text/css")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, settings: Settings = Depends(get_settings)):
    limiter.check(
        f"login:{client_key(request)}",
        settings.rate_limit_requests,
        settings.rate_limit_window_seconds,
    )
    user = authenticate(body.username, body.password)
    if user is None:
        security_event(
            "authentication_failure", username=body.username, client_ip=client_key(request)
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    security_event("authentication_success", username=user.username, client_ip=client_key(request))
    return TokenResponse(
        access_token=create_token(user, settings), expires_in=settings.token_ttl_seconds
    )


@app.get("/api/me", response_model=UserResponse)
async def me(user: User = Depends(current_user)):
    return UserResponse(username=user.username, role=user.role)


@app.get("/api/reviewer", response_model=dict[str, str])
async def reviewer_area(user: User = Depends(require_reviewer)):
    return {"message": f"Reviewer access granted to {user.username}"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    body: ChatRequest,
    request: Request,
    user: User = Depends(current_user),
    settings: Settings = Depends(get_settings),
):
    limiter.check(
        f"chat:{user.username}", settings.rate_limit_requests, settings.rate_limit_window_seconds
    )
    if len(body.message) > settings.max_prompt_chars:
        security_event("invalid_input", username=user.username, reason="prompt_too_long")
        raise HTTPException(status_code=422, detail="Message exceeds configured maximum")
    try:
        output = await chat(body.message, provider, request.state.request_id)
    except Exception:
        security_event("llm_error", request_id=request.state.request_id)
        raise HTTPException(status_code=502, detail="Model service unavailable") from None
    return ChatResponse(response=output, request_id=request.state.request_id)

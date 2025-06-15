from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.v1.router import api_router as api_router_v1
from app.core.config import config
from app.core.exceptions import ExceptionBase
from app.middleware.logging import default_logger
from app.middleware.rate_limit import init_limiter, rate_limit_middleware
from app.middleware.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    default_logger.info("Application starting up...")
    await init_limiter()  # Initialize rate limiter

    try:
        yield
    finally:
        # Shutdown
        default_logger.info("Application shutting down...")
        # TODO: close the necessary connections


app = FastAPI(
    title=config.APP_NAME.format(name="Chat Assistant"),
    version=config.APP_VERSION,
    openapi_url=f"{config.APP_STR}/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "docExpansion": "none",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    },
    lifespan=lifespan,
)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Add rate limit middleware
app.middleware("http")(rate_limit_middleware)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ExceptionBase)
def http_exception_handler(request, exc: ExceptionBase):
    default_logger.error(
        "API Error occurred",
        error_code=exc.code,
        error_message=exc.message,
        error_description=exc.description,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "description": exc.description,
        },
    )


@app.middleware("http")
async def log_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "unknown")
    start_time = datetime.now(timezone.utc)

    # Log incoming request
    body = await request.body()

    # Check if the request is multipart/form-data
    content_type = request.headers.get("content-type", "")
    is_multipart = "multipart/form-data" in content_type

    # For multipart requests, don't try to decode the body
    body_str = "{}"
    if not is_multipart and body:
        try:
            body_str = body.decode()
        except UnicodeDecodeError:
            body_str = "<binary content>"

    default_logger.info(
        "Incoming request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params),
        headers=dict(request.headers),
        body=body_str,
        content_type=content_type,
    )

    try:
        response = await call_next(request)

        # Log response
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        default_logger.info(
            "Request completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time,
        )

        return response
    except Exception as e:
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        default_logger.error(
            "Request failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            error=str(e),
            process_time=process_time,
        )
        raise


# Include API router
app.include_router(api_router_v1, prefix=config.APP_STR)
app.include_router(health_router, prefix=config.APP_STR)

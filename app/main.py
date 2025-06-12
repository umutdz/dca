from contextlib import asynccontextmanager

from elasticapm.contrib.starlette import ElasticAPM
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from app.api.health import router as health_router
from app.api.v1.router import api_router as api_router_v1
from app.core.config import config
from app.core.exceptions import ExceptionBase
from app.core.tracing import app_apm
from app.middleware.rate_limit import init_limiter, rate_limit_middleware
from app.middleware.request_id import RequestIDMiddleware
from app.tasks.tasks import cp_log_to_elk


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    print("Starting up...")
    await init_limiter()  # Initialize rate limiter

    try:
        yield
    finally:
        # Shutdown
        print("Shutting down...")

        # close the necessary connections


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
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "description": exc.description,
        },
    )


if config.APP_ENV != "LOCAL":
    from app.core.logging import Logger

    logger = Logger(apm_method=app_apm)

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        body = await request.body() if request.method == "POST" else "{}"
        response = await call_next(request)
        log_data = await logger.get_incoming_log_data(request, body, response)
        if log_data:
            cp_log_to_elk.delay(log_data)
        return response

    app.add_middleware(ElasticAPM, client=app_apm)


# Include API router
app.include_router(api_router_v1, prefix=config.APP_STR)
app.include_router(health_router, prefix=config.APP_STR)

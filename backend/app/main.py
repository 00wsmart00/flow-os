from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import ApplicationError
from app.db.database import close_database
from app.schemas.errors import ErrorDetail, ErrorResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    close_database()


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    @application.exception_handler(ApplicationError)
    async def handle_application_error(_: Request, exc: ApplicationError) -> JSONResponse:
        payload = ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details)
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(part) for part in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        payload = ErrorResponse(
            error=ErrorDetail(
                code="request_validation_error",
                message="Request validation failed",
                details=details,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=payload.model_dump(),
        )

    application.include_router(api_router, prefix=settings.api_prefix)
    return application


app = create_app()

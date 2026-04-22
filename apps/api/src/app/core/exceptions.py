from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def app_exception_handler(_: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "request_id": "local-dev",
            "data": None,
        },
    )


async def http_exception_handler(_: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": f"HTTP_{exc.status_code}",
            "message": detail,
            "request_id": "local-dev",
            "data": None,
        },
    )


async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": str(exc),
            "request_id": "local-dev",
            "data": None,
        },
    )

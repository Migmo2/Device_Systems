"""Middleware de trazabilidad y metricas basicas por request."""

import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response

from app.core.config import settings


async def request_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    started_at = time.perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    response = await call_next(request)
    response.headers["X-App-Name"] = settings.app_name
    response.headers["X-API-Version"] = settings.api_version
    response.headers["X-Process-Time"] = f"{time.perf_counter() - started_at:.6f}"
    response.headers["X-Request-ID"] = request_id
    return response

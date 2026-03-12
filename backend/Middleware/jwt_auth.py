from fastapi import Request, status
from fastapi.responses import JSONResponse

from backend.Core.db import SessionLocal
from backend.Service.auth import get_user_by_subject, verify_token

PROTECTED_PATH_PREFIXES = ("/user", "/resume")


def _requires_auth(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in PROTECTED_PATH_PREFIXES)


async def jwt_auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS" or not _requires_auth(request.url.path):
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing bearer token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.removeprefix("Bearer ").strip()
    token_data = verify_token(token)
    if token_data is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with SessionLocal() as session:
        user = await get_user_by_subject(token_data.sub, session)

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Inactive user"},
        )

    request.state.current_user = user
    request.state.jwt_subject = token_data.sub
    return await call_next(request)

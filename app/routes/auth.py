from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import auth_schemas
from app.auth_config import AuthSettings, get_auth_settings
from app.database import get_db
from app.errors import ServiceError
from app.services import auth
from app.services.auth_security import auth_rate_limiter, hash_opaque_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def apply_rate_limit(
    request: Request,
    action: str,
    settings: AuthSettings,
    identity: str = "",
) -> None:
    private_identity = hash_opaque_token(
        f"{client_ip(request)}:{identity.casefold()}",
        settings.token_hash_secret,
    )
    auth_rate_limiter.check(
        f"{action}:{private_identity}",
        settings.rate_limit_per_minute,
    )


def get_current_context(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Session = Depends(get_db),
    settings: AuthSettings = Depends(get_auth_settings),
) -> auth.AuthenticatedContext:
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise ServiceError(401, "INVALID_ACCESS_TOKEN", "Bearer access token is required")
    token = credentials.credentials.strip()
    if not token:
        raise ServiceError(401, "INVALID_ACCESS_TOKEN", "Bearer access token is required")
    return auth.authenticate_access_token(db, token, settings)


@router.post(
    "/register",
    response_model=auth_schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: auth_schemas.RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    settings: AuthSettings = Depends(get_auth_settings),
):
    apply_rate_limit(request, "register", settings, str(data.email))
    return auth.register_user(db, data, settings)


@router.post("/verify-email", response_model=auth_schemas.MessageResponse)
def verify_email(
    data: auth_schemas.TokenRequest,
    request: Request,
    db: Session = Depends(get_db),
    settings: AuthSettings = Depends(get_auth_settings),
):
    apply_rate_limit(request, "verify-email", settings)
    auth.verify_email(db, data.token, settings)
    return {"message": "Email verified successfully"}


@router.post("/login", response_model=auth_schemas.TokenPairResponse)
def login(
    data: auth_schemas.LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    settings: AuthSettings = Depends(get_auth_settings),
):
    apply_rate_limit(request, "login", settings, str(data.email))
    return auth.login(
        db,
        data,
        settings,
        client_ip(request),
        request.headers.get("user-agent"),
    )


@router.post("/refresh", response_model=auth_schemas.TokenPairResponse)
def refresh(
    data: auth_schemas.RefreshRequest,
    request: Request,
    db: Session = Depends(get_db),
    settings: AuthSettings = Depends(get_auth_settings),
):
    apply_rate_limit(request, "refresh", settings)
    return auth.refresh_tokens(db, data.refresh_token, settings)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: Session = Depends(get_db),
    context: auth.AuthenticatedContext = Depends(get_current_context),
) -> Response:
    auth.logout(db, context)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/forgot-password",
    response_model=auth_schemas.DevelopmentLinkResponse,
)
def forgot_password(
    data: auth_schemas.ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    settings: AuthSettings = Depends(get_auth_settings),
):
    apply_rate_limit(request, "forgot-password", settings, str(data.email))
    return auth.forgot_password(db, data.email, settings)


@router.post("/reset-password", response_model=auth_schemas.MessageResponse)
def reset_password(
    data: auth_schemas.ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    settings: AuthSettings = Depends(get_auth_settings),
):
    apply_rate_limit(request, "reset-password", settings)
    auth.reset_password(db, data, settings)
    return {"message": "Password reset successfully; all sessions were revoked"}


@router.post("/change-password", response_model=auth_schemas.MessageResponse)
def change_password(
    data: auth_schemas.ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    context: auth.AuthenticatedContext = Depends(get_current_context),
    settings: AuthSettings = Depends(get_auth_settings),
):
    apply_rate_limit(
        request,
        "change-password",
        settings,
        str(context.user.user_id),
    )
    auth.change_password(db, context, data)
    return {"message": "Password changed successfully; all sessions were revoked"}


@router.get("/me", response_model=auth_schemas.CurrentUserResponse)
def current_user(
    context: auth.AuthenticatedContext = Depends(get_current_context),
):
    return context.user


@router.get("/sessions", response_model=list[auth_schemas.SessionResponse])
def sessions(
    db: Session = Depends(get_db),
    context: auth.AuthenticatedContext = Depends(get_current_context),
):
    return auth.list_sessions(db, context)


@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_sessions(
    db: Session = Depends(get_db),
    context: auth.AuthenticatedContext = Depends(get_current_context),
) -> Response:
    auth.revoke_all_sessions(db, context.user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    context: auth.AuthenticatedContext = Depends(get_current_context),
) -> Response:
    auth.revoke_one_session(db, context, session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

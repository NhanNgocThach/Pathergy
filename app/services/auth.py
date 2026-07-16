import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import NoReturn

from sqlalchemy import case, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import auth_schemas, models
from app.auth_config import AuthSettings
from app.auth_identifiers import (
    mask_phone_number,
    normalize_email,
    normalize_login_identifier,
)
from app.errors import ServiceError
from app.services.auth_security import (
    constant_time_hash_matches,
    create_access_token,
    decode_access_token,
    hash_opaque_token,
    hash_password,
    needs_password_rehash,
    new_opaque_token,
    token_id_from_opaque_token,
    validate_password_strength,
    verify_password,
)

DUMMY_PASSWORD_HASH = hash_password("NotAReal1!Password")
SESSION_ACTIVITY_WRITE_INTERVAL = timedelta(minutes=5)


@dataclass
class AuthenticatedContext:
    user: models.UserAccount
    session: models.AuthSession


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def register_user(
    db: Session,
    data: auth_schemas.RegisterRequest,
    settings: AuthSettings,
) -> auth_schemas.RegisterResponse:
    validate_password_strength(data.password, data.confirm_password)
    email = normalize_email(data.email)
    if db.scalar(select(models.UserAccount).where(models.UserAccount.email == email)):
        raise ServiceError(
            409,
            "EMAIL_ALREADY_REGISTERED",
            "An account with this email is already registered",
        )

    patient = models.Patient(**data.profile.model_dump())
    db.add(patient)
    db.flush()

    user = models.UserAccount(
        email=email,
        display_name=data.display_name,
        patient_id=patient.id,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    try:
        db.flush()
        token_id, raw_token = new_opaque_token()
        db.add(
            models.EmailVerificationToken(
                token_id=token_id,
                user_id=user.user_id,
                token_hash=hash_opaque_token(raw_token, settings.token_hash_secret),
                expires_at=utc_now()
                + timedelta(hours=settings.verification_token_hours),
            )
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        message = str(error.orig).lower()
        if "email" in message:
            raise ServiceError(
                409,
                "EMAIL_ALREADY_REGISTERED",
                "An account with this email is already registered",
            ) from error
        raise ServiceError(
            409,
            "REGISTRATION_CONFLICT",
            "Registration could not be completed because the data conflicts",
        ) from error

    verification_url = None
    if settings.development_mode:
        verification_url = (
            f"{settings.development_base_url}/auth/verify-email?token={raw_token}"
        )
    return auth_schemas.RegisterResponse(
        user_id=user.user_id,
        email=user.email,
        patient_id=user.patient_id,
        verification_url=verification_url,
    )


def verify_email(
    db: Session,
    raw_token: str,
    settings: AuthSettings,
) -> None:
    token_id = token_id_from_opaque_token(raw_token)
    supplied_hash = hash_opaque_token(raw_token, settings.token_hash_secret)
    token = db.get(models.EmailVerificationToken, token_id) if token_id else None
    if token is None or not constant_time_hash_matches(
        token.token_hash,
        supplied_hash,
    ):
        raise ServiceError(
            400,
            "INVALID_VERIFICATION_TOKEN",
            "Email verification token is invalid",
        )
    if token.used_at is not None:
        raise ServiceError(
            400,
            "INVALID_VERIFICATION_TOKEN",
            "Email verification token has already been used",
        )
    if as_utc(token.expires_at) <= utc_now():
        raise ServiceError(
            400,
            "VERIFICATION_TOKEN_EXPIRED",
            "Email verification token has expired",
        )

    user_id = token.user_id
    user = db.get(models.UserAccount, user_id)
    if user is None:
        raise ServiceError(400, "INVALID_VERIFICATION_TOKEN", "User no longer exists")
    now = utc_now()
    consumed = db.execute(
        update(models.EmailVerificationToken)
        .where(
            models.EmailVerificationToken.token_id == token_id,
            models.EmailVerificationToken.token_hash == supplied_hash,
            models.EmailVerificationToken.used_at.is_(None),
            models.EmailVerificationToken.expires_at > now,
        )
        .values(used_at=now)
        .execution_options(synchronize_session=False)
    )
    if consumed.rowcount != 1:
        db.rollback()
        raise ServiceError(
            400,
            "INVALID_VERIFICATION_TOKEN",
            "Email verification token has already been used",
        )
    user.email_verified_at = now
    db.commit()


def record_failed_login(
    db: Session,
    user: models.UserAccount,
    settings: AuthSettings,
) -> None:
    now = utc_now()
    locked_until = now + timedelta(minutes=settings.lockout_minutes)
    db.execute(
        update(models.UserAccount)
        .where(models.UserAccount.user_id == user.user_id)
        .values(
            failed_login_attempts=models.UserAccount.failed_login_attempts + 1,
            locked_until=case(
                (
                    models.UserAccount.failed_login_attempts + 1
                    >= settings.max_failed_logins,
                    locked_until,
                ),
                else_=models.UserAccount.locked_until,
            ),
        )
        .execution_options(synchronize_session=False)
    )
    db.commit()
    db.refresh(user)


def login(
    db: Session,
    data: auth_schemas.LoginRequest,
    settings: AuthSettings,
    ip_address: str | None,
    user_agent: str | None,
) -> auth_schemas.TokenPairResponse:
    identifier_kind, identifier = normalize_login_identifier(data.login_identifier)
    identifier_column = (
        models.UserAccount.email
        if identifier_kind == "email"
        else models.UserAccount.phone_number
    )
    user = db.scalar(select(models.UserAccount).where(identifier_column == identifier))
    if user is None:
        verify_password(DUMMY_PASSWORD_HASH, data.password)
        raise ServiceError(
            401,
            "INVALID_CREDENTIALS",
            "Email, phone number, or password is incorrect",
        )

    now = utc_now()
    if user.locked_until is not None and as_utc(user.locked_until) > now:
        raise ServiceError(423, "ACCOUNT_LOCKED", "Account is temporarily locked")
    if user.locked_until is not None:
        user.locked_until = None
        user.failed_login_attempts = 0

    if not verify_password(user.password_hash, data.password):
        record_failed_login(db, user, settings)
        if user.locked_until is not None:
            raise ServiceError(423, "ACCOUNT_LOCKED", "Account is temporarily locked")
        raise ServiceError(
            401,
            "INVALID_CREDENTIALS",
            "Email, phone number, or password is incorrect",
        )
    if not user.is_active:
        raise ServiceError(
            401,
            "INVALID_CREDENTIALS",
            "Email, phone number, or password is incorrect",
        )
    if identifier_kind == "email" and user.email_verified_at is None:
        raise ServiceError(403, "EMAIL_NOT_VERIFIED", "Email address is not verified")
    if identifier_kind == "phone" and user.phone_verified_at is None:
        raise ServiceError(
            403,
            "PHONE_NOT_VERIFIED",
            "Phone number is not verified",
        )

    if needs_password_rehash(user.password_hash):
        user.password_hash = hash_password(data.password)
    user.failed_login_attempts = 0
    user.locked_until = None

    session_id = str(uuid.uuid4())
    refresh_token = f"{session_id}.{secrets.token_urlsafe(32)}"
    session = models.AuthSession(
        session_id=session_id,
        user_id=user.user_id,
        refresh_token_hash=hash_opaque_token(
            refresh_token,
            settings.token_hash_secret,
        ),
        device_name=data.device_name,
        device_type=data.device_type,
        ip_address=ip_address,
        user_agent=user_agent[:500] if user_agent else None,
        expires_at=now + timedelta(days=settings.refresh_token_days),
    )
    db.add(session)
    db.commit()
    return token_pair(user.user_id, session_id, refresh_token, settings)


def token_pair(
    user_id: int,
    session_id: str,
    refresh_token: str,
    settings: AuthSettings,
) -> auth_schemas.TokenPairResponse:
    return auth_schemas.TokenPairResponse(
        access_token=create_access_token(user_id, session_id, settings),
        refresh_token=refresh_token,
        access_token_expires_in=settings.access_token_minutes * 60,
        refresh_token_expires_in=settings.refresh_token_days * 24 * 60 * 60,
    )


def refresh_tokens(
    db: Session,
    raw_token: str,
    settings: AuthSettings,
) -> auth_schemas.TokenPairResponse:
    session_id = token_id_from_opaque_token(raw_token)
    session = db.get(models.AuthSession, session_id) if session_id else None
    if session is None:
        raise ServiceError(401, "INVALID_REFRESH_TOKEN", "Refresh token is invalid")

    token_hash = hash_opaque_token(raw_token, settings.token_hash_secret)
    if not constant_time_hash_matches(session.refresh_token_hash, token_hash):
        raise_refresh_token_error(db, session.session_id, token_hash)
    if session.revoked_at is not None:
        raise ServiceError(401, "REFRESH_TOKEN_REVOKED", "Refresh token is revoked")
    now = utc_now()
    if as_utc(session.expires_at) <= now:
        session.revoked_at = now
        db.commit()
        raise ServiceError(401, "REFRESH_TOKEN_EXPIRED", "Refresh token has expired")

    new_refresh_token = f"{session.session_id}.{secrets.token_urlsafe(32)}"
    new_token_hash = hash_opaque_token(
        new_refresh_token,
        settings.token_hash_secret,
    )
    user_id = session.user_id
    current_session_id = session.session_id
    rotation = db.execute(
        update(models.AuthSession)
        .where(
            models.AuthSession.session_id == current_session_id,
            models.AuthSession.refresh_token_hash == token_hash,
            models.AuthSession.revoked_at.is_(None),
            models.AuthSession.expires_at > now,
        )
        .values(refresh_token_hash=new_token_hash, last_used_at=now)
        .execution_options(synchronize_session=False)
    )
    if rotation.rowcount != 1:
        db.rollback()
        raise_refresh_token_error(db, current_session_id, token_hash)
    db.add(
        models.UsedRefreshToken(
            session_id=current_session_id,
            token_hash=token_hash,
        )
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise_refresh_token_error(db, current_session_id, token_hash)
    return token_pair(user_id, current_session_id, new_refresh_token, settings)


def raise_refresh_token_error(
    db: Session,
    session_id: str,
    token_hash: str,
) -> NoReturn:
    """Classify a failed rotation and revoke the session when reuse is proven."""
    db.expire_all()
    session = db.get(models.AuthSession, session_id)
    if session is None:
        raise ServiceError(401, "INVALID_REFRESH_TOKEN", "Refresh token is invalid")

    replayed = db.scalar(
        select(models.UsedRefreshToken).where(
            models.UsedRefreshToken.session_id == session_id,
            models.UsedRefreshToken.token_hash == token_hash,
        )
    )
    if replayed is not None:
        revoke_session(session)
        db.commit()
        raise ServiceError(
            401,
            "REFRESH_TOKEN_REVOKED",
            "Refresh token replay was detected and the session was revoked",
        )
    if not constant_time_hash_matches(session.refresh_token_hash, token_hash):
        raise ServiceError(401, "INVALID_REFRESH_TOKEN", "Refresh token is invalid")
    if session.revoked_at is not None:
        raise ServiceError(401, "REFRESH_TOKEN_REVOKED", "Refresh token is revoked")
    if as_utc(session.expires_at) <= utc_now():
        session.revoked_at = utc_now()
        db.commit()
        raise ServiceError(401, "REFRESH_TOKEN_EXPIRED", "Refresh token has expired")
    raise ServiceError(401, "INVALID_REFRESH_TOKEN", "Refresh token is invalid")


def authenticate_access_token(
    db: Session,
    raw_token: str,
    settings: AuthSettings,
) -> AuthenticatedContext:
    payload = decode_access_token(raw_token, settings)
    try:
        user_id = int(str(payload["sub"]))
        session_id = str(payload["sid"])
    except (KeyError, TypeError, ValueError) as error:
        raise ServiceError(401, "INVALID_ACCESS_TOKEN", "Access token is invalid") from error

    session = db.get(models.AuthSession, session_id)
    user = db.get(models.UserAccount, user_id)
    invalid = (
        session is None
        or user is None
        or session.user_id != user_id
        or session.revoked_at is not None
        or as_utc(session.expires_at) <= utc_now()
        or not user.is_active
        or (
            user.email_verified_at is None
            and user.phone_verified_at is None
        )
    )
    if invalid:
        raise ServiceError(401, "INVALID_ACCESS_TOKEN", "Access token is invalid")
    now = utc_now()
    if as_utc(session.last_used_at) <= now - SESSION_ACTIVITY_WRITE_INTERVAL:
        session.last_used_at = now
        db.commit()
    return AuthenticatedContext(user=user, session=session)


def revoke_session(session: models.AuthSession) -> None:
    if session.revoked_at is None:
        session.revoked_at = utc_now()


def logout(db: Session, context: AuthenticatedContext) -> None:
    revoke_session(context.session)
    db.commit()


def list_sessions(
    db: Session,
    context: AuthenticatedContext,
) -> list[auth_schemas.SessionResponse]:
    now = utc_now()
    sessions = list(
        db.scalars(
            select(models.AuthSession)
            .where(
                models.AuthSession.user_id == context.user.user_id,
                models.AuthSession.revoked_at.is_(None),
                models.AuthSession.expires_at > now,
            )
            .order_by(models.AuthSession.created_at.desc())
        )
    )
    return [
        auth_schemas.SessionResponse(
            session_id=session.session_id,
            device_name=session.device_name,
            device_type=session.device_type,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            created_at=session.created_at,
            last_used_at=session.last_used_at,
            expires_at=session.expires_at,
            is_current=session.session_id == context.session.session_id,
        )
        for session in sessions
    ]


def revoke_one_session(
    db: Session,
    context: AuthenticatedContext,
    session_id: str,
) -> None:
    session = db.get(models.AuthSession, session_id)
    if session is None or session.user_id != context.user.user_id:
        raise ServiceError(404, "SESSION_NOT_FOUND", "Session not found")
    revoke_session(session)
    db.commit()


def mark_all_sessions_revoked(db: Session, user_id: int) -> None:
    db.execute(
        update(models.AuthSession)
        .where(
            models.AuthSession.user_id == user_id,
            models.AuthSession.revoked_at.is_(None),
        )
        .values(revoked_at=utc_now())
        .execution_options(synchronize_session="fetch")
    )


def revoke_all_sessions(db: Session, user_id: int) -> None:
    mark_all_sessions_revoked(db, user_id)
    db.commit()


def forgot_password(
    db: Session,
    email: object,
    settings: AuthSettings,
) -> auth_schemas.DevelopmentLinkResponse:
    user = db.scalar(
        select(models.UserAccount).where(
            models.UserAccount.email == normalize_email(email)
        )
    )
    message = "If the account exists, password reset instructions are available."
    if user is None or user.password_hash is None:
        return auth_schemas.DevelopmentLinkResponse(message=message)

    now = utc_now()
    existing_tokens = db.scalars(
        select(models.PasswordResetToken).where(
            models.PasswordResetToken.user_id == user.user_id,
            models.PasswordResetToken.used_at.is_(None),
        )
    )
    for existing in existing_tokens:
        existing.used_at = now

    token_id, raw_token = new_opaque_token()
    db.add(
        models.PasswordResetToken(
            token_id=token_id,
            user_id=user.user_id,
            token_hash=hash_opaque_token(raw_token, settings.token_hash_secret),
            expires_at=now + timedelta(hours=settings.reset_token_hours),
        )
    )
    db.commit()
    development_url = None
    if settings.development_mode:
        development_url = (
            f"{settings.development_base_url}/auth/reset-password?token={raw_token}"
        )
    return auth_schemas.DevelopmentLinkResponse(
        message=message,
        development_url=development_url,
    )


def reset_password(
    db: Session,
    data: auth_schemas.ResetPasswordRequest,
    settings: AuthSettings,
) -> None:
    validate_password_strength(data.new_password, data.confirm_password)
    token_id = token_id_from_opaque_token(data.token)
    supplied_hash = hash_opaque_token(data.token, settings.token_hash_secret)
    token = db.get(models.PasswordResetToken, token_id) if token_id else None
    if token is None or not constant_time_hash_matches(
        token.token_hash,
        supplied_hash,
    ):
        raise ServiceError(400, "INVALID_RESET_TOKEN", "Password reset token is invalid")
    if token.used_at is not None:
        raise ServiceError(400, "INVALID_RESET_TOKEN", "Password reset token was already used")
    if as_utc(token.expires_at) <= utc_now():
        raise ServiceError(400, "RESET_TOKEN_EXPIRED", "Password reset token has expired")

    user_id = token.user_id
    user = db.get(models.UserAccount, user_id)
    if user is None:
        raise ServiceError(400, "INVALID_RESET_TOKEN", "User no longer exists")
    now = utc_now()
    consumed = db.execute(
        update(models.PasswordResetToken)
        .where(
            models.PasswordResetToken.token_id == token_id,
            models.PasswordResetToken.token_hash == supplied_hash,
            models.PasswordResetToken.used_at.is_(None),
            models.PasswordResetToken.expires_at > now,
        )
        .values(used_at=now)
        .execution_options(synchronize_session=False)
    )
    if consumed.rowcount != 1:
        db.rollback()
        raise ServiceError(
            400,
            "INVALID_RESET_TOKEN",
            "Password reset token was already used",
        )
    user.password_hash = hash_password(data.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    mark_all_sessions_revoked(db, user.user_id)
    db.commit()


def change_password(
    db: Session,
    context: AuthenticatedContext,
    data: auth_schemas.ChangePasswordRequest,
) -> None:
    validate_password_strength(data.new_password, data.confirm_password)
    if not verify_password(context.user.password_hash, data.current_password):
        raise ServiceError(401, "INVALID_CREDENTIALS", "Current password is incorrect")
    context.user.password_hash = hash_password(data.new_password)
    mark_all_sessions_revoked(db, context.user.user_id)
    db.commit()


def current_user_response(
    user: models.UserAccount,
) -> auth_schemas.CurrentUserResponse:
    return auth_schemas.CurrentUserResponse(
        user_id=user.user_id,
        email=user.email,
        phone_number_masked=mask_phone_number(user.phone_number),
        display_name=user.display_name,
        patient_id=user.patient_id,
        email_verified_at=user.email_verified_at,
        phone_verified_at=user.phone_verified_at,
        is_active=user.is_active,
    )

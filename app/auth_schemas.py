from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.auth_identifiers import normalize_login_identifier

from app.schemas import PatientCreate


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)
    profile: PatientCreate

    @field_validator("display_name", mode="before")
    @classmethod
    def strip_display_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class RegisterResponse(BaseModel):
    user_id: int
    email: EmailStr
    patient_id: int
    verification_required: bool = True
    verification_url: str | None = None


class TokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1, max_length=500)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identifier: str | None = Field(default=None, min_length=1, max_length=254)
    email: EmailStr | None = None
    password: str = Field(min_length=1, max_length=128)
    device_name: str | None = Field(default=None, max_length=100)
    device_type: str | None = Field(default=None, max_length=50)

    @field_validator("identifier", mode="before")
    @classmethod
    def strip_identifier(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_one_identifier(self) -> "LoginRequest":
        if (self.identifier is None) == (self.email is None):
            raise ValueError("Provide exactly one email address or phone number")
        normalize_login_identifier(self.login_identifier)
        return self

    @property
    def login_identifier(self) -> str:
        return self.identifier if self.identifier is not None else str(self.email)


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=1, max_length=500)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int = 900
    refresh_token_expires_in: int = 2_592_000


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr


class DevelopmentLinkResponse(BaseModel):
    message: str
    development_url: str | None = None


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1, max_length=500)
    new_password: str = Field(min_length=1, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)


class MessageResponse(BaseModel):
    message: str


class CurrentUserResponse(BaseModel):
    user_id: int
    email: EmailStr | None
    phone_number_masked: str | None
    display_name: str
    patient_id: int
    email_verified_at: datetime | None
    phone_verified_at: datetime | None
    is_active: bool


class SessionResponse(BaseModel):
    session_id: str
    device_name: str | None
    device_type: str | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    is_current: bool

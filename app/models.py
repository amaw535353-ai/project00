from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def reject_control_characters(cls, value: str) -> str:
        if any(ord(char) < 32 and char not in "\n\t" for char in value):
            raise ValueError("control characters are not allowed")
        if not value.strip():
            raise ValueError("message cannot be blank")
        return value


class ChatResponse(BaseModel):
    response: str
    request_id: str


class UserResponse(BaseModel):
    username: str
    role: str

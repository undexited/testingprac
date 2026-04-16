from pydantic import BaseModel, Field
from typing import Optional


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=120)


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    id: int
    email: str
    display_name: str


class ConversationOut(BaseModel):
    id: int
    title: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    provider: str
    model: str
    latency_ms: int


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    mode: str = Field(default="fast")
    provider: Optional[str] = None
    conversation_id: Optional[int] = None


class ChatOut(BaseModel):
    conversation_id: int
    assistant_message: MessageOut

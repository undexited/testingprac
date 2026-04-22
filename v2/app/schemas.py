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
    is_admin: bool


class MembershipOut(BaseModel):
    organization_id: int
    organization_name: str
    role: str


class WorkspaceOut(BaseModel):
    id: int
    organization_id: int
    name: str


class ConversationOut(BaseModel):
    id: int
    title: str
    workspace_id: int


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
    workspace_id: Optional[int] = None
    agent_id: Optional[str] = None


class ChatOut(BaseModel):
    conversation_id: int
    assistant_message: MessageOut


class LoginEventOut(BaseModel):
    id: int
    email: str
    action: str
    status: str
    ip_address: str
    user_agent: str
    created_at: str


class AgentOut(BaseModel):
    id: str
    name: str
    description: str

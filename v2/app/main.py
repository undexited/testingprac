from pathlib import Path
from typing import Any
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import create_token, get_current_user, get_db, hash_password, verify_password
from .config import get_settings
from .db import Base, engine, ensure_sqlite_compatibility
from .gateway import generate_response
from .models import Conversation, LoginEvent, Membership, Message, Organization, User, Workspace
from .schemas import (
    AgentOut,
    ChatIn,
    ChatOut,
    ConversationOut,
    LoginEventOut,
    LoginIn,
    MeOut,
    MembershipOut,
    MessageOut,
    RegisterIn,
    TokenOut,
    WorkspaceOut,
)


settings = get_settings()
Base.metadata.create_all(bind=engine)
ensure_sqlite_compatibility()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AGENTS: dict[str, dict[str, str]] = {
    "general": {
        "name": "General",
        "description": "Everyday assistant for normal prompting/chat.",
        "system": "You are a helpful general assistant. Be concise and practical.",
    },
    "coder": {
        "name": "Coder",
        "description": "Code-focused assistant for architecture, debugging and implementation.",
        "system": "You are an elite coding assistant. Provide concrete code-first answers and explain tradeoffs.",
    },
    "analyst": {
        "name": "Analyst",
        "description": "Deep reasoning assistant for decision support and planning.",
        "system": "You are a strategic analyst. Surface assumptions, risks, and recommended decisions.",
    },
}

web_dir = Path(__file__).resolve().parent.parent / "web"
app.mount("/assets", StaticFiles(directory=str(web_dir)), name="assets")


def _record_login_event(db: Session, user: User, action: str, status: str, req: Request) -> None:
    event = LoginEvent(
        user_id=user.id,
        email=user.email,
        action=action,
        status=status,
        ip_address=req.client.host if req.client else "",
        user_agent=req.headers.get("user-agent", "")[:512],
    )
    db.add(event)


def _user_workspaces(db: Session, user_id: int) -> list[Workspace]:
    memberships = db.scalars(select(Membership).where(Membership.user_id == user_id)).all()
    org_ids = [m.organization_id for m in memberships]
    if not org_ids:
        return []
    return db.scalars(select(Workspace).where(Workspace.organization_id.in_(org_ids))).all()


def _ensure_workspace_access(db: Session, user: User, workspace_id: int) -> Workspace:
    ws = db.get(Workspace, workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id, Membership.organization_id == ws.organization_id
        )
    )
    if not membership:
        raise HTTPException(status_code=403, detail="No workspace access")
    return ws


@app.get("/")
def root():
    return FileResponse(str(web_dir / "index.html"))


@app.get("/api/agents", response_model=list[AgentOut])
def list_agents():
    return [AgentOut(id=k, name=v["name"], description=v["description"]) for k, v in AGENTS.items()]


@app.post("/api/auth/register", response_model=TokenOut)
def register(payload: RegisterIn, req: Request, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    first_user = db.scalar(select(User).limit(1)) is None
    user = User(
        email=email,
        display_name=payload.display_name.strip(),
        password_hash=hash_password(payload.password),
        is_admin=first_user,
    )
    db.add(user)
    db.flush()

    org = Organization(name=f"{user.display_name} Workspace {uuid4().hex[:8]}", plan="starter")
    db.add(org)
    db.flush()

    ws = Workspace(organization_id=org.id, name="Default Workspace")
    db.add(ws)
    db.flush()

    membership = Membership(user_id=user.id, organization_id=org.id, role="owner")
    db.add(membership)

    _record_login_event(db, user, action="register", status="success", req=req)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_token(user.id))


@app.post("/api/auth/login", response_model=TokenOut)
def login(payload: LoginIn, req: Request, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(payload.password, user.password_hash):
        # Best effort login event for unknown user isn't persisted.
        raise HTTPException(status_code=401, detail="Invalid credentials")
    _record_login_event(db, user, action="login", status="success", req=req)
    db.commit()
    return TokenOut(access_token=create_token(user.id))


@app.get("/api/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)):
    return MeOut(id=user.id, email=user.email, display_name=user.display_name, is_admin=user.is_admin)


@app.get("/api/memberships", response_model=list[MembershipOut])
def memberships(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Membership).where(Membership.user_id == user.id)).all()
    results: list[MembershipOut] = []
    for row in rows:
        org = db.get(Organization, row.organization_id)
        results.append(
            MembershipOut(
                organization_id=row.organization_id,
                organization_name=org.name if org else "Unknown Organization",
                role=row.role,
            )
        )
    return results


@app.get("/api/workspaces", response_model=list[WorkspaceOut])
def workspaces(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = _user_workspaces(db, user.id)
    return [WorkspaceOut(id=w.id, organization_id=w.organization_id, name=w.name) for w in rows]


@app.get("/api/admin/login-events", response_model=list[LoginEventOut])
def admin_login_events(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    rows = db.scalars(select(LoginEvent).order_by(LoginEvent.id.desc()).limit(200)).all()
    return [
        LoginEventOut(
            id=row.id,
            email=row.email,
            action=row.action,
            status=row.status,
            ip_address=row.ip_address,
            user_agent=row.user_agent,
            created_at=row.created_at.isoformat() if row.created_at else "",
        )
        for row in rows
    ]


@app.get("/api/conversations", response_model=list[ConversationOut])
def conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workspaces = _user_workspaces(db, user.id)
    workspace_ids = [w.id for w in workspaces]
    if not workspace_ids:
        return []
    rows = db.scalars(
        select(Conversation).where(Conversation.workspace_id.in_(workspace_ids)).order_by(Conversation.id.desc())
    ).all()
    return [ConversationOut(id=row.id, title=row.title, workspace_id=row.workspace_id) for row in rows]


@app.get("/api/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def conversation_messages(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.get(Conversation, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    _ensure_workspace_access(db, user, convo.workspace_id)
    rows = db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.asc())).all()
    return [
        MessageOut(
            id=r.id,
            role=r.role,
            content=r.content,
            provider=r.provider,
            model=r.model,
            latency_ms=r.latency_ms,
        )
        for r in rows
    ]


@app.post("/api/chat/send", response_model=ChatOut)
def chat_send(payload: ChatIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mode = payload.mode.lower()
    if mode not in {"fast", "think"}:
        raise HTTPException(status_code=400, detail="mode must be fast or think")

    workspaces = _user_workspaces(db, user.id)
    if not workspaces:
        raise HTTPException(status_code=400, detail="No workspace available for user")

    target_workspace = workspaces[0]
    if payload.workspace_id:
        target_workspace = _ensure_workspace_access(db, user, payload.workspace_id)

    convo: Conversation | None = None
    if payload.conversation_id:
        convo = db.get(Conversation, payload.conversation_id)
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
        _ensure_workspace_access(db, user, convo.workspace_id)
    else:
        title = payload.message.strip()[:60]
        convo = Conversation(
            workspace_id=target_workspace.id,
            user_id=user.id,
            title=title if title else "New Conversation",
        )
        db.add(convo)
        db.flush()

    chosen_agent = payload.agent_id or "general"
    if chosen_agent not in AGENTS:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {chosen_agent}")
    system_prompt = AGENTS[chosen_agent]["system"]

    user_msg = Message(
        conversation_id=convo.id,
        role="user",
        content=payload.message,
        provider=payload.provider or settings.default_provider,
        model=chosen_agent,
        latency_ms=0,
    )
    db.add(user_msg)
    db.flush()

    output, model, used_provider, latency_ms = generate_response(
        prompt=payload.message,
        mode=mode,
        provider_override=payload.provider,
        system_prompt=system_prompt,
    )

    assistant_msg = Message(
        conversation_id=convo.id,
        role="assistant",
        content=output,
        provider=used_provider,
        model=model,
        latency_ms=latency_ms,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return ChatOut(
        conversation_id=convo.id,
        assistant_message=MessageOut(
            id=assistant_msg.id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            provider=assistant_msg.provider,
            model=assistant_msg.model,
            latency_ms=assistant_msg.latency_ms,
        ),
    )

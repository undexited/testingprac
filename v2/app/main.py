from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import create_token, get_current_user, get_db, hash_password, verify_password
from .config import get_settings
from .db import Base, engine
from .gateway import generate_response
from .models import Conversation, Message, User
from .schemas import ChatIn, ChatOut, ConversationOut, LoginIn, MeOut, MessageOut, RegisterIn, TokenOut


settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

web_dir = Path(__file__).resolve().parent.parent / "web"
app.mount("/assets", StaticFiles(directory=str(web_dir)), name="assets")


@app.get("/")
def root():
    return FileResponse(str(web_dir / "index.html"))


@app.post("/api/auth/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        display_name=payload.display_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_token(user.id))


@app.post("/api/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_token(user.id))


@app.get("/api/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)):
    return MeOut(id=user.id, email=user.email, display_name=user.display_name)


@app.get("/api/conversations", response_model=list[ConversationOut])
def conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.id.desc())
    ).all()
    return [ConversationOut(id=row.id, title=row.title) for row in rows]


@app.get("/api/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def conversation_messages(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.get(Conversation, conversation_id)
    if not convo or convo.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    rows = db.scalars(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.asc())
    ).all()
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

    convo: Conversation | None = None
    if payload.conversation_id:
        convo = db.get(Conversation, payload.conversation_id)
        if not convo or convo.user_id != user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        title = payload.message.strip()[:60]
        convo = Conversation(user_id=user.id, title=title if title else "New Conversation")
        db.add(convo)
        db.flush()

    user_msg = Message(
        conversation_id=convo.id,
        role="user",
        content=payload.message,
        provider=payload.provider or settings.default_provider,
        model="",
        latency_ms=0,
    )
    db.add(user_msg)
    db.flush()

    output, model, latency_ms = generate_response(
        prompt=payload.message,
        mode=mode,
        provider_override=payload.provider,
    )
    assistant_msg = Message(
        conversation_id=convo.id,
        role="assistant",
        content=output,
        provider=payload.provider or settings.default_provider,
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

import os
from pathlib import Path

from fastapi.testclient import TestClient


def main() -> None:
    db_path = Path(__file__).resolve().parent / "smoke_test.db"
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"

    from app.main import app

    client = TestClient(app)

    register = client.post(
        "/api/auth/register",
        json={"email": "smoke@example.com", "password": "password123", "display_name": "Smoke"},
    )
    assert register.status_code == 200, register.text
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/me", headers=headers)
    assert me.status_code == 200, me.text
    assert me.json()["is_admin"] is True

    events = client.get("/api/admin/login-events", headers=headers)
    assert events.status_code == 200, events.text

    agents = client.get("/api/agents")
    assert agents.status_code == 200, agents.text
    assert any(a["id"] == "coder" for a in agents.json())

    workspaces = client.get("/api/workspaces", headers=headers)
    assert workspaces.status_code == 200, workspaces.text
    workspace_id = workspaces.json()[0]["id"]

    chat = client.post(
        "/api/chat/send",
        headers=headers,
        json={
            "message": "Give me a short architecture checklist.",
            "mode": "think",
            "provider": "builtin",
            "workspace_id": workspace_id,
            "agent_id": "analyst",
        },
    )
    assert chat.status_code == 200, chat.text
    assert "assistant_message" in chat.json()

    print("SMOKE TEST OK")

    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass


if __name__ == "__main__":
    main()

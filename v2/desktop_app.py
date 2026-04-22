import json
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from urllib import request, error


API_BASE = os.getenv("V2_API_BASE", "http://127.0.0.1:8090")
ROOT_DIR = os.path.dirname(__file__)


class AppState:
    token = ""
    conversation_id = None
    workspace_id = None
    mode = "fast"
    provider = ""
    agent_id = "general"


def http_json(path: str, method: str = "GET", body: dict | None = None, token: str = "") -> dict:
    url = f"{API_BASE}{path}"
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            detail = json.loads(raw).get("detail", raw)
        except Exception:
            detail = raw or str(exc)
        raise RuntimeError(detail)
    except Exception as exc:
        raise RuntimeError(str(exc))


def ensure_backend():
    try:
        http_json("/")
        return
    except Exception:
        pass

    python_exe = os.path.join("C:\\Users\\helme\\OneDrive\\Documents\\codexplay", ".venv-openwebui", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    env = os.environ.copy()
    local_app_data = env.get("LOCALAPPDATA", "")
    if local_app_data:
        db_dir = os.path.join(local_app_data, "testingprac-ai-v2")
        os.makedirs(db_dir, exist_ok=True)
        env["DATABASE_URL"] = f"sqlite:///{os.path.join(db_dir, 'app_v2_multi.db').replace(os.sep, '/')}"

    subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8090"],
        cwd=ROOT_DIR,
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    time.sleep(2.0)


class DesktopApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TestingPrac AI Desktop")
        self.root.geometry("1320x860")
        self.root.configure(bg="#0d111a")

        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TNotebook", background="#0d111a", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 8), background="#1a2233", foreground="#c9d5ff")

        self.state = AppState()
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.chat_frame = tk.Frame(self.notebook, bg="#111827")
        self.agents_frame = tk.Frame(self.notebook, bg="#111827")
        self.code_frame = tk.Frame(self.notebook, bg="#111827")
        self.admin_frame = tk.Frame(self.notebook, bg="#111827")

        self.notebook.add(self.chat_frame, text="Chat")
        self.notebook.add(self.agents_frame, text="Agents")
        self.notebook.add(self.code_frame, text="Code Studio")
        self.notebook.add(self.admin_frame, text="Admin")

        self._build_chat_tab()
        self._build_agents_tab()
        self._build_code_tab()
        self._build_admin_tab()

        self.refresh_agents()
        self.refresh_admin_events()

    def _label(self, parent, text):
        return tk.Label(parent, text=text, fg="#d8e3ff", bg="#111827", font=("Segoe UI", 10, "bold"))

    def _entry(self, parent, show=None):
        e = tk.Entry(parent, bg="#0b1220", fg="#eaf0ff", insertbackground="#eaf0ff", relief="flat", show=show)
        e.config(highlightthickness=1, highlightbackground="#283753", highlightcolor="#5f7dff")
        return e

    def _button(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd, bg="#4458d8", fg="white", relief="flat", padx=12, pady=6)

    def _build_chat_tab(self):
        top = tk.Frame(self.chat_frame, bg="#111827")
        top.pack(fill="x", padx=12, pady=10)

        self._label(top, "Email").grid(row=0, column=0, sticky="w")
        self.email_entry = self._entry(top)
        self.email_entry.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        self._label(top, "Password").grid(row=0, column=1, sticky="w")
        self.pass_entry = self._entry(top, show="*")
        self.pass_entry.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        self._label(top, "Display Name").grid(row=0, column=2, sticky="w")
        self.name_entry = self._entry(top)
        self.name_entry.grid(row=1, column=2, padx=4, pady=4, sticky="ew")

        self._button(top, "Register", self.on_register).grid(row=1, column=3, padx=8)
        self._button(top, "Login", self.on_login).grid(row=1, column=4, padx=8)
        self._button(top, "New Chat", self.new_chat).grid(row=1, column=5, padx=8)

        self.mode_var = tk.StringVar(value="fast")
        self.provider_var = tk.StringVar(value="")
        self.agent_var = tk.StringVar(value="general")

        mode_box = ttk.Combobox(top, textvariable=self.mode_var, values=["fast", "think"], width=8, state="readonly")
        mode_box.grid(row=1, column=6, padx=4)
        provider_box = ttk.Combobox(
            top,
            textvariable=self.provider_var,
            values=["", "openai", "anthropic", "builtin", "ollama"],
            width=12,
            state="readonly",
        )
        provider_box.grid(row=1, column=7, padx=4)
        agent_box = ttk.Combobox(top, textvariable=self.agent_var, values=["general", "coder", "analyst"], width=12, state="readonly")
        agent_box.grid(row=1, column=8, padx=4)

        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)
        top.grid_columnconfigure(2, weight=1)

        self.status_label = tk.Label(self.chat_frame, text="Not logged in", fg="#9fb0d9", bg="#111827")
        self.status_label.pack(anchor="w", padx=14)

        self.chat_log = ScrolledText(self.chat_frame, bg="#0b1220", fg="#eaf0ff", insertbackground="#eaf0ff", relief="flat", height=24)
        self.chat_log.pack(fill="both", expand=True, padx=12, pady=8)
        self.chat_log.insert("end", "Welcome to TestingPrac AI Desktop.\n")
        self.chat_log.config(state="disabled")

        bottom = tk.Frame(self.chat_frame, bg="#111827")
        bottom.pack(fill="x", padx=12, pady=8)
        self.prompt_input = ScrolledText(bottom, bg="#0b1220", fg="#eaf0ff", insertbackground="#eaf0ff", relief="flat", height=5)
        self.prompt_input.pack(side="left", fill="both", expand=True)
        self._button(bottom, "Send", self.send_message).pack(side="right", padx=8)

    def _build_agents_tab(self):
        self.agent_list = ScrolledText(self.agents_frame, bg="#0b1220", fg="#eaf0ff", relief="flat")
        self.agent_list.pack(fill="both", expand=True, padx=12, pady=12)
        self.agent_list.insert("end", "Loading agents...\n")
        self.agent_list.config(state="disabled")

    def _build_code_tab(self):
        split = tk.PanedWindow(self.code_frame, orient="horizontal", bg="#111827", sashwidth=6)
        split.pack(fill="both", expand=True, padx=12, pady=12)

        left = tk.Frame(split, bg="#111827")
        right = tk.Frame(split, bg="#111827")
        split.add(left, stretch="always")
        split.add(right, stretch="always")

        self._label(left, "Code Editor").pack(anchor="w")
        file_bar = tk.Frame(left, bg="#111827")
        file_bar.pack(fill="x", pady=(4, 2))
        self.file_path_entry = self._entry(file_bar)
        self.file_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._button(file_bar, "Open", self.open_code_file).pack(side="left")
        self._button(file_bar, "Save", self.save_code_file).pack(side="left", padx=(6, 0))

        self.code_editor = ScrolledText(left, bg="#0b1220", fg="#eaf0ff", insertbackground="#eaf0ff", relief="flat")
        self.code_editor.pack(fill="both", expand=True, pady=6)
        self.code_editor.insert("end", "# Write code or prompts here.\n")

        controls = tk.Frame(left, bg="#111827")
        controls.pack(fill="x")
        self._button(controls, "Run Python Snippet", self.run_code_snippet).pack(side="left")
        self._button(controls, "Explain With Coder Agent", self.explain_code_with_agent).pack(side="left", padx=8)

        self._label(right, "Output / Analysis").pack(anchor="w")
        self.code_output = ScrolledText(right, bg="#0b1220", fg="#eaf0ff", relief="flat")
        self.code_output.pack(fill="both", expand=True, pady=6)

    def _build_admin_tab(self):
        hdr = tk.Frame(self.admin_frame, bg="#111827")
        hdr.pack(fill="x", padx=12, pady=10)
        self._button(hdr, "Refresh Login Events", self.refresh_admin_events).pack(side="left")
        self.admin_log = ScrolledText(self.admin_frame, bg="#0b1220", fg="#eaf0ff", relief="flat")
        self.admin_log.pack(fill="both", expand=True, padx=12, pady=8)

    def _append_chat(self, role: str, text: str):
        self.chat_log.config(state="normal")
        self.chat_log.insert("end", f"{role}: {text}\n\n")
        self.chat_log.see("end")
        self.chat_log.config(state="disabled")

    def _set_status(self, text: str):
        self.status_label.config(text=text)

    def on_register(self):
        self._auth_action("register")

    def on_login(self):
        self._auth_action("login")

    def _auth_action(self, action: str):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()
        name = self.name_entry.get().strip() or "User"
        if not email or not password:
            return messagebox.showerror("Missing fields", "Email and password are required.")
        try:
            if action == "register":
                data = http_json("/api/auth/register", "POST", {"email": email, "password": password, "display_name": name})
            else:
                data = http_json("/api/auth/login", "POST", {"email": email, "password": password})
            self.state.token = data["access_token"]
            me = http_json("/api/me", token=self.state.token)
            self._set_status(f"Logged in as {me['display_name']} ({me['email']})")
            ws = http_json("/api/workspaces", token=self.state.token)
            if ws:
                self.state.workspace_id = ws[0]["id"]
            self.refresh_admin_events()
        except Exception as exc:
            messagebox.showerror("Auth failed", str(exc))

    def new_chat(self):
        self.state.conversation_id = None
        self.chat_log.config(state="normal")
        self.chat_log.delete("1.0", "end")
        self.chat_log.insert("end", "New conversation started.\n\n")
        self.chat_log.config(state="disabled")

    def send_message(self):
        msg = self.prompt_input.get("1.0", "end").strip()
        if not msg:
            return
        if not self.state.token:
            return messagebox.showerror("Login required", "Please register or login first.")

        self._append_chat("You", msg)
        self.prompt_input.delete("1.0", "end")

        def worker():
            try:
                payload = {
                    "message": msg,
                    "mode": self.mode_var.get(),
                    "provider": self.provider_var.get() or None,
                    "conversation_id": self.state.conversation_id,
                    "workspace_id": self.state.workspace_id,
                    "agent_id": self.agent_var.get(),
                }
                data = http_json("/api/chat/send", "POST", payload, token=self.state.token)
                self.state.conversation_id = data["conversation_id"]
                assistant = data["assistant_message"]
                self.root.after(0, lambda: self._append_chat("AI", assistant["content"]))
                self.root.after(0, lambda: self._set_status(f"{assistant['provider']}/{assistant['model']} | {assistant['latency_ms']}ms"))
            except Exception as exc:
                self.root.after(0, lambda: self._append_chat("System", f"Error: {exc}"))

        threading.Thread(target=worker, daemon=True).start()

    def refresh_agents(self):
        try:
            agents = http_json("/api/agents")
        except Exception as exc:
            agents = [{"id": "error", "name": "Unavailable", "description": str(exc)}]
        self.agent_list.config(state="normal")
        self.agent_list.delete("1.0", "end")
        for agent in agents:
            self.agent_list.insert("end", f"{agent['id']} | {agent['name']}\n{agent['description']}\n\n")
        self.agent_list.config(state="disabled")

    def open_code_file(self):
        path = filedialog.askopenfilename(initialdir=ROOT_DIR, title="Open file")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.file_path_entry.delete(0, "end")
            self.file_path_entry.insert(0, path)
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("end", content)
        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))

    def save_code_file(self):
        path = self.file_path_entry.get().strip()
        if not path:
            path = filedialog.asksaveasfilename(initialdir=ROOT_DIR, title="Save file as")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.code_editor.get("1.0", "end"))
            self.file_path_entry.delete(0, "end")
            self.file_path_entry.insert(0, path)
            self._set_status(f"Saved {os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))

    def run_code_snippet(self):
        code = self.code_editor.get("1.0", "end")
        self.code_output.delete("1.0", "end")
        try:
            proc = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.code_output.insert("end", proc.stdout or "")
            if proc.stderr:
                self.code_output.insert("end", f"\n[stderr]\n{proc.stderr}")
        except Exception as exc:
            self.code_output.insert("end", f"Execution error: {exc}")

    def explain_code_with_agent(self):
        code = self.code_editor.get("1.0", "end").strip()
        if not code:
            return
        if not self.state.token:
            return messagebox.showerror("Login required", "Please login first.")
        prompt = f"Analyze and improve this code:\n\n{code}"
        try:
            data = http_json(
                "/api/chat/send",
                "POST",
                {
                    "message": prompt,
                    "mode": "think",
                    "agent_id": "coder",
                    "workspace_id": self.state.workspace_id,
                    "provider": self.provider_var.get() or None,
                },
                token=self.state.token,
            )
            self.code_output.delete("1.0", "end")
            self.code_output.insert("end", data["assistant_message"]["content"])
        except Exception as exc:
            self.code_output.insert("end", f"Agent error: {exc}")

    def refresh_admin_events(self):
        self.admin_log.config(state="normal")
        self.admin_log.delete("1.0", "end")
        if not self.state.token:
            self.admin_log.insert("end", "Login to view admin events.\n")
            self.admin_log.config(state="disabled")
            return
        try:
            events = http_json("/api/admin/login-events", token=self.state.token)
            if not events:
                self.admin_log.insert("end", "No login events yet.\n")
            else:
                for ev in events:
                    self.admin_log.insert(
                        "end",
                        f"{ev['created_at']} | {ev['action']} | {ev['email']} | {ev['ip_address']}\nUA: {ev['user_agent']}\n\n",
                    )
        except Exception as exc:
            self.admin_log.insert("end", f"Admin feed unavailable: {exc}\n")
        self.admin_log.config(state="disabled")


def main():
    ensure_backend()
    root = tk.Tk()
    DesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

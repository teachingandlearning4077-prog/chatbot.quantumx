from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.engine import ChatEngine

app = FastAPI(title="QuantumX Chatbot")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
engines_by_session: dict[str, ChatEngine] = {}


def _get_engine(request: Request) -> tuple[str, ChatEngine, bool]:
    session_id = request.cookies.get("qx_session")
    created = False
    if not session_id:
        session_id = str(uuid4())
        created = True

    if session_id not in engines_by_session:
        engines_by_session[session_id] = ChatEngine()

    return session_id, engines_by_session[session_id], created


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    session_id, engine, created = _get_engine(request)

    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "messages": engine.history,
        },
    )
    if created:
        response.set_cookie("qx_session", session_id, httponly=True, samesite="lax")
    return response


@app.post("/chat")
def chat(request: Request, message: str = Form(...), mode: str = Form("text")):
    clean_message = message.strip()
    if not clean_message:
        return JSONResponse({"response": "Mensagem vazia. Digite algo para continuar.", "image_base64": None, "mode": mode}, status_code=400)

    valid_mode = mode if mode in {"text", "image"} else "text"

    session_id, engine, created = _get_engine(request)
    result = engine.ask(clean_message, mode=valid_mode)
    payload = {
        "response": result.text,
        "image_base64": result.image_base64,
        "mode": valid_mode,
    }
    response = JSONResponse(payload)
    if created:
        response.set_cookie("qx_session", session_id, httponly=True, samesite="lax")
    return response


@app.get("/health")
def health():
    return {
        "status": "ok",
        "name": "QuantumX",
        "active_sessions": len(engines_by_session),
    }

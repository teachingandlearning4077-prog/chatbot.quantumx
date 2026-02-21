from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.engine import ChatEngine

app = FastAPI(title="QuantumX Chatbot")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
engine = ChatEngine()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "messages": engine.history,
        },
    )


@app.post("/chat")
def chat(message: str = Form(...)):
    answer = engine.ask(message)
    return JSONResponse({"response": answer})


@app.get("/health")
def health():
    return {"status": "ok", "name": "QuantumX"}

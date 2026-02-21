from __future__ import annotations

import ast
import importlib
import math
import re
from dataclasses import dataclass, field
from typing import Iterable

from app.settings import get_env

SYSTEM_PROMPT = (
    "Você é QuantumX, um assistente super inteligente, claro e amigável. "
    "Responda em português com precisão e objetividade."
)


@dataclass
class ChatResult:
    text: str
    image_base64: str | None = None


@dataclass
class ChatEngine:
    history: list[dict[str, str]] = field(default_factory=list)

    def ask(self, user_message: str, mode: str = "text") -> ChatResult:
        self.history.append({"role": "user", "content": user_message})

        if mode == "image":
            result = self._generate_image(user_message)
        else:
            result = self._ask_text(user_message)

        self.history.append({"role": "assistant", "content": result.text})
        self.history = self.history[-20:]
        return result

    def _ask_text(self, user_message: str) -> ChatResult:
        response = self._ask_openai_text(user_message)
        if response is None:
            response = self._fallback_response(user_message)
        return ChatResult(text=response)

    def _ask_openai_text(self, user_message: str) -> str | None:
        api_key = get_env("OPENAI_API_KEY")
        if not api_key:
            return None
        if importlib.util.find_spec("openai") is None:
            return None

        from openai import OpenAI

        model = get_env("OPENAI_MODEL", "gpt-4o-mini")
        client = OpenAI(api_key=api_key)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *self.history[:-1],
            {"role": "user", "content": user_message},
        ]

        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.4,
            )
            return completion.choices[0].message.content or "Desculpe, não consegui responder agora."
        except Exception:
            return None

    def _generate_image(self, prompt: str) -> ChatResult:
        api_key = get_env("OPENAI_API_KEY")
        if not api_key:
            return ChatResult(
                text=(
                    "Para gerar imagens, configure `OPENAI_API_KEY` no ambiente/.env. "
                    "Exemplo: cp .env.example .env"
                )
            )
        if importlib.util.find_spec("openai") is None:
            return ChatResult(text="Dependência OpenAI não instalada no servidor.")

        from openai import OpenAI

        image_model = get_env("OPENAI_IMAGE_MODEL", "gpt-image-1")
        client = OpenAI(api_key=api_key)
        try:
            image = client.images.generate(model=image_model, prompt=prompt, size="1024x1024")
            b64 = image.data[0].b64_json
            if not b64:
                return ChatResult(text="Não consegui gerar imagem agora. Tente novamente.")
            return ChatResult(text="Imagem criada com sucesso!", image_base64=b64)
        except Exception:
            return ChatResult(text="Falha ao gerar imagem no momento. Tente com outro prompt.")

    def _fallback_response(self, text: str) -> str:
        lowered = text.lower()

        if any(token in lowered for token in ("calcule", "quanto é", "resolver", "conta")):
            expr = _extract_math_expression(text)
            if expr:
                result = safe_eval(expr)
                if result is not None:
                    return f"Resultado de `{expr}`: **{result}**"

        if "resuma" in lowered or "resumo" in lowered:
            return summarize_text(text)

        if "lista" in lowered or "tarefas" in lowered:
            items = extract_items(text)
            if items:
                formatted = "\n".join(f"- [ ] {item}" for item in items)
                return f"Perfeito! Aqui está sua lista de tarefas:\n{formatted}"

        return (
            "Posso responder praticamente qualquer pergunta, gerar ideias, estudar conteúdos, "
            "criar textos e ajudar com código. Para modo avançado estilo ChatGPT e criação de imagens, "
            "configure `OPENAI_API_KEY` no servidor."
        )


def _extract_math_expression(text: str) -> str | None:
    match = re.search(r"([\d\s\+\-\*\/\(\)\.\^]+)", text)
    if not match:
        return None
    candidate = match.group(1).strip().replace("^", "**")
    if not candidate or all(c in "+-*/(). " for c in candidate):
        return None
    return candidate


def safe_eval(expr: str) -> float | int | None:
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError:
        return None

    allowed_nodes: tuple[type[ast.AST], ...] = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Mod,
    )

    if not all(isinstance(n, allowed_nodes) for n in ast.walk(node)):
        return None

    try:
        value = eval(compile(node, "<expr>", "eval"), {"__builtins__": {}, "math": math}, {})
    except Exception:
        return None

    if isinstance(value, (int, float)):
        return round(value, 6)
    return None


def summarize_text(text: str, max_sentences: int = 3) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    summary = " ".join(parts[:max_sentences]).strip()
    if len(summary) < 25:
        return "Envie um texto maior e eu faço um resumo objetivo em tópicos."
    return f"Resumo rápido:\n{summary}"


def extract_items(text: str) -> Iterable[str]:
    separators = [",", ";", " e "]
    payload = text
    for keyword in ("lista", "tarefas", ":"):
        idx = payload.lower().find(keyword)
        if idx >= 0:
            payload = payload[idx + len(keyword) :]
    for sep in separators:
        if sep in payload:
            items = [x.strip(" .") for x in payload.split(sep)]
            return [x for x in items if len(x) > 2]
    return [payload.strip(" .")] if len(payload.strip()) > 3 else []

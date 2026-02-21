from __future__ import annotations

import ast
import math
import os
import re
from dataclasses import dataclass, field
from typing import Iterable

try:
    from openai import OpenAI
except Exception:  # import can fail if dependency is not installed
    OpenAI = None


SYSTEM_PROMPT = (
    "Você é QuantumX, um chatbot super inteligente, claro e amigável. "
    "Responda em português e, quando possível, entregue passos práticos."
)


@dataclass
class ChatEngine:
    history: list[dict[str, str]] = field(default_factory=list)

    def ask(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        response = self._ask_openai(user_message)
        if response is None:
            response = self._fallback_response(user_message)

        self.history.append({"role": "assistant", "content": response})
        self.history = self.history[-20:]
        return response

    def _ask_openai(self, user_message: str) -> str | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or OpenAI is None:
            return None

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        client = OpenAI(api_key=api_key)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *self.history[:-1], {"role": "user", "content": user_message}]

        try:
            completion = client.chat.completions.create(model=model, messages=messages, temperature=0.5)
            return completion.choices[0].message.content or "Desculpe, não consegui responder agora."
        except Exception:
            return None

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

        if "traduz" in lowered:
            return (
                "Posso traduzir com API externa quando você configurar OPENAI_API_KEY. "
                "Sem API, ainda posso ajudar com explicações e reescritas em português."
            )

        return (
            "Sou o **QuantumX** 🤖 e posso te ajudar com planejamento, resumos, listas, ideias, código e cálculos. "
            "Se quiser algo no estilo ChatGPT, configure `OPENAI_API_KEY` e eu uso um modelo avançado automaticamente."
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

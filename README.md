# QuantumX Chatbot

Um chatbot chamado **QuantumX**, com interface web e arquitetura pronta para funcionar no estilo ChatGPT.

## O que ele faz

- Conversa com fallback inteligente local (sem API).
- Faz cálculos matemáticos simples com segurança.
- Gera listas de tarefas.
- Faz resumo rápido de texto.
- Pode usar modelo avançado (OpenAI) quando `OPENAI_API_KEY` estiver configurada.

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Depois abra: `http://127.0.0.1:8000`

## Deploy no GitHub

1. Suba este projeto para um repositório no GitHub.
2. Use GitHub Codespaces ou qualquer serviço compatível com FastAPI.
3. Defina variável de ambiente opcional:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` (ex.: `gpt-4o-mini`)

## Estrutura

- `app/main.py`: API e rotas web.
- `app/engine.py`: cérebro do QuantumX.
- `app/templates/` e `app/static/`: frontend.
- `tests/`: testes automatizados.

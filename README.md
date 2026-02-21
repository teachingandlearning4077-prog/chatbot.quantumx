# QuantumX Chatbot

Um chatbot chamado **QuantumX**, com interface web rica e pronto para funcionar **com ou sem FastAPI/OpenAI**.

## ✅ O que já funciona 100%

- Site com elementos visuais (hero, cards, temas, atalhos rápidos e imagem local).
- Chat de texto com fallback local inteligente (sem API externa).
- Se o backend falhar, o frontend ativa fallback local no próprio navegador para o chat não parar.
- Cálculos, resumos e listas no fallback local.
- Modo imagem quando `OPENAI_API_KEY` estiver configurada.
- Suporte multiusuário por sessão (cookie por visitante).

## Modos de execução

### 1) Modo automático (recomendado)

```bash
python start.py
```

- Se `fastapi` + `uvicorn` estiverem instalados, usa o app FastAPI.
- Se não estiverem, sobe automaticamente o servidor local sem dependências externas.

### 2) Modo FastAPI (opcional)

```bash
uvicorn app.main:app --reload
```

### 3) Modo local sem API/framework

```bash
python -m app.local_server
```

Depois abra: `http://127.0.0.1:8000`

## Configurar OpenAI (opcional para modo avançado)

```bash
cp .env.example .env
```

No `.env`:

```env
OPENAI_API_KEY=sk-proj-sua-chave-real
OPENAI_MODEL=gpt-4o-mini
OPENAI_IMAGE_MODEL=gpt-image-1
```

## Estrutura

- `start.py`: inicialização automática (FastAPI se disponível, senão local).
- `app/local_server.py`: servidor HTTP local sem FastAPI.
- `app/main.py`: API FastAPI.
- `app/engine.py`: cérebro do QuantumX (texto + imagem + fallback).
- `app/templates/` e `app/static/`: frontend.
- `tests/`: testes automatizados.

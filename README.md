# QuantumX Chatbot

Um chatbot chamado **QuantumX**, com interface web e arquitetura para funcionar como assistente estilo ChatGPT.

## O que ele faz agora

- Chat em linguagem natural para perguntas gerais.
- Suporte a múltiplos usuários por sessão (cookie por visitante).
- Modo de **geração de imagens** via OpenAI (`gpt-image-1`).
- Interface nova com cards de recursos, atalhos rápidos e ilustração visual.
- Fallback local quando API não estiver configurada (cálculos, resumos e listas).

## Configurar OpenAI API (obrigatório para modo avançado)

> **Importante:** não commite sua chave no código.

1. Copie o exemplo:

```bash
cp .env.example .env
```

2. Edite `.env` e coloque sua chave real:

```env
OPENAI_API_KEY=sk-proj-sua-chave-real
OPENAI_MODEL=gpt-4o-mini
OPENAI_IMAGE_MODEL=gpt-image-1
```

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Depois abra: `http://127.0.0.1:8000`

## Estrutura

- `app/main.py`: API, sessões por usuário e rotas web.
- `app/engine.py`: núcleo de resposta textual e geração de imagens.
- `app/settings.py`: leitura segura de variáveis e `.env`.
- `app/templates/` e `app/static/`: frontend.
- `tests/`: testes automatizados.

from app.engine import ChatEngine, safe_eval


def test_safe_eval_basic_math():
    assert safe_eval("2 + 2 * 3") == 8


def test_safe_eval_blocks_unsafe_expression():
    assert safe_eval("__import__('os').system('echo x')") is None


def test_engine_todo_generation_text_mode():
    engine = ChatEngine()
    result = engine.ask("crie uma lista: estudar IA, publicar no github", mode="text")
    assert "- [ ]" in result.text


def test_engine_image_mode_without_key_returns_instruction(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    engine = ChatEngine()
    result = engine.ask("astronauta andando em marte", mode="image")
    assert "OPENAI_API_KEY" in result.text
    assert result.image_base64 is None

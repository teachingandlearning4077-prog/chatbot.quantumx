from app.engine import ChatEngine, safe_eval


def test_safe_eval_basic_math():
    assert safe_eval("2 + 2 * 3") == 8


def test_safe_eval_blocks_unsafe_expression():
    assert safe_eval("__import__('os').system('echo x')") is None


def test_engine_todo_generation():
    engine = ChatEngine()
    answer = engine.ask("crie uma lista: estudar IA, publicar no github")
    assert "- [ ]" in answer

from pathlib import Path

from app import settings


def test_get_env_from_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / '.env'
    env_file.write_text('OPENAI_API_KEY=test-key\n', encoding='utf-8')

    monkeypatch.setattr(settings, 'ENV_FILE', env_file)
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)

    assert settings.get_env('OPENAI_API_KEY') == 'test-key'


def test_get_env_prefers_real_environment(tmp_path, monkeypatch):
    env_file = tmp_path / '.env'
    env_file.write_text('OPENAI_API_KEY=from-dotenv\n', encoding='utf-8')

    monkeypatch.setattr(settings, 'ENV_FILE', env_file)
    monkeypatch.setenv('OPENAI_API_KEY', 'from-env')

    assert settings.get_env('OPENAI_API_KEY') == 'from-env'

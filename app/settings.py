from __future__ import annotations

import os
from pathlib import Path


ENV_FILE = Path('.env')


def _read_dotenv_file() -> dict[str, str]:
    if not ENV_FILE.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in ENV_FILE.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_env(name: str, default: str | None = None) -> str | None:
    direct = os.getenv(name)
    if direct:
        return direct

    from_dotenv = _read_dotenv_file().get(name)
    if from_dotenv:
        return from_dotenv

    return default

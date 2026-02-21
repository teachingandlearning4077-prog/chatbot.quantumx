from __future__ import annotations

import importlib.util


def main() -> None:
    if importlib.util.find_spec("fastapi") and importlib.util.find_spec("uvicorn"):
        import uvicorn

        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
        return

    from app.local_server import run_local_server

    run_local_server(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

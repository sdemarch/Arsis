"""Entrypoint for the single-process local Arsis runtime."""

import argparse
import os
import threading
import webbrowser

import uvicorn


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Avvia Arsis in modalita locale")
    parser.add_argument("--host", default=None, help="Indirizzo di ascolto, predefinito 127.0.0.1")
    parser.add_argument("--port", type=int, default=None, help="Porta HTTP locale")
    parser.add_argument("--no-browser", action="store_true", help="Non aprire il browser")
    return parser.parse_args()


def main() -> None:
    """Run one loopback-bound process serving both API and compiled frontend."""

    arguments = _arguments()
    os.environ["ARSIS_SERVE_FRONTEND"] = "true"
    from arsis.core.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()
    if not settings.frontend_dir.joinpath("index.html").is_file():
        raise SystemExit(
            f"Frontend compilato non trovato in {settings.frontend_dir}. "
            "Compilare e includere il frontend prima dell'avvio locale."
        )
    host = arguments.host or settings.local_bind_host
    port = arguments.port or settings.local_bind_port
    if not arguments.no_browser:
        threading.Timer(0.8, webbrowser.open, args=(f"http://{host}:{port}",)).start()
    uvicorn.run("arsis.main:app", host=host, port=port, log_level=settings.log_level.lower())


if __name__ == "__main__":
    main()

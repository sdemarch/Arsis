"""Entrypoint for the single-process local Arsis runtime."""

import argparse
import json
import os
import socket
import sys
import threading
import urllib.request
import webbrowser
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import uvicorn

TITLE = "Arsis"


def _arguments(arguments: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Avvia Arsis in modalita locale")
    parser.add_argument("--host", default=None, help="Indirizzo di ascolto, predefinito 127.0.0.1")
    parser.add_argument("--port", type=int, default=None, help="Porta HTTP locale")
    parser.add_argument("--no-browser", action="store_true", help="Non aprire il browser")
    return parser.parse_args(arguments)


def report_error(message: str) -> None:
    """Show a fatal error: a dialog in the windowed exe, stderr otherwise."""
    if getattr(sys, "frozen", False) and sys.platform == "win32":
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, message, TITLE, 0x10)  # MB_ICONERROR
    else:
        print(message, file=sys.stderr)


def port_in_use(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def is_arsis(url: str) -> bool:
    """Whether the program answering on ``url`` is an Arsis runtime."""
    try:
        with urllib.request.urlopen(f"{url}/health/live", timeout=2) as response:
            return bool(json.load(response).get("status") == "ok")
    except OSError, ValueError:
        return False


def _redirect_output_to_log(data_dir: Path) -> None:
    # A windowed exe has no console: uvicorn would fail writing to a missing stream.
    if sys.stdout is not None and sys.stderr is not None:
        return
    log_dir = data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stream = open(log_dir / "arsis.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or stream
    sys.stderr = sys.stderr or stream


def start(
    arguments: Sequence[str] | None = None,
    *,
    serve: Callable[..., Any] = uvicorn.run,
    open_browser: Callable[[str], Any] = webbrowser.open,
    report: Callable[[str], None] = report_error,
) -> int:
    """Prepare the data, then serve API and compiled frontend from one loopback process.

    Returns the process exit code.
    """
    options = _arguments(arguments)
    # Settings field serve_frontend, read from SERVE_FRONTEND.
    os.environ["SERVE_FRONTEND"] = "true"
    from arsis.core.config import get_settings
    from arsis.core.migrations import MigrationError
    from arsis.migrate import run_migrations

    get_settings.cache_clear()
    settings = get_settings()
    _redirect_output_to_log(settings.data_dir)
    host = options.host or settings.local_bind_host
    port = options.port or settings.local_bind_port
    url = f"http://{host}:{port}"

    if port_in_use(host, port):
        if is_arsis(url):
            # Already running: a second launch just brings the user to it.
            if not options.no_browser:
                open_browser(url)
            return 0
        report(
            f"La porta {port} è già usata da un altro programma, quindi Arsis non può partire.\n"
            "Chiudere quel programma oppure avviare Arsis con --port e un altro numero."
        )
        return 1

    if not settings.frontend_dir.joinpath("index.html").is_file():
        report(
            f"Frontend compilato non trovato in {settings.frontend_dir}. "
            "Compilare e includere il frontend prima dell'avvio locale."
        )
        return 1

    try:
        run_migrations()
    except MigrationError as exception:
        report(
            "Impossibile aggiornare il database di Arsis.\n\n"
            f"{exception}\n\n"
            f"I dati si trovano in {settings.data_dir}; eventuali backup in {settings.backups_dir}."
        )
        return 1

    from arsis.main import create_app

    if not options.no_browser:
        threading.Timer(0.8, open_browser, args=(url,)).start()
    # Built from these settings, not the module-level app made at first import.
    serve(create_app(settings), host=host, port=port, log_level=settings.log_level.lower())
    return 0


def main() -> None:
    raise SystemExit(start())


if __name__ == "__main__":
    main()

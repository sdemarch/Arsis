from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from arsis import local_runtime
from arsis.core.config import get_settings
from arsis.core.migrations import MigrationError


class Recorder:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.calls.append((*args, kwargs))


@pytest.fixture
def runtime_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "index.html").write_text("<h1>Arsis</h1>", encoding="utf-8")
    monkeypatch.setenv("ARSIS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("FRONTEND_DIST_DIR", str(frontend))
    monkeypatch.setenv("SERVE_FRONTEND", "false")  # start() overrides it; restored after
    monkeypatch.setattr(local_runtime, "port_in_use", lambda host, port: False)
    get_settings.cache_clear()
    yield tmp_path / "data"
    get_settings.cache_clear()


def test_first_start_migrates_the_database_then_serves(runtime_env: Path) -> None:
    serve, browser, report = Recorder(), Recorder(), Recorder()

    code = local_runtime.start(
        ["--no-browser", "--port", "8899"], serve=serve, open_browser=browser, report=report
    )

    assert code == 0
    assert (runtime_env / "arsis.db").is_file()
    assert len(serve.calls) == 1
    assert serve.calls[0][-1]["port"] == 8899
    with TestClient(serve.calls[0][0]) as client:
        # Deep links get the compiled frontend, the API keeps answering.
        assert client.get("/school/courses").text == "<h1>Arsis</h1>"
        assert client.get("/api/v1/auth/setup").json() == {"required": True}
    assert browser.calls == [] and report.calls == []


def test_second_launch_opens_the_running_instance(
    runtime_env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(local_runtime, "port_in_use", lambda host, port: True)
    monkeypatch.setattr(local_runtime, "is_arsis", lambda url: True)
    serve, browser, report = Recorder(), Recorder(), Recorder()

    code = local_runtime.start([], serve=serve, open_browser=browser, report=report)

    assert code == 0
    assert browser.calls == [("http://127.0.0.1:8765", {})]
    assert serve.calls == [] and report.calls == []


def test_port_taken_by_another_program_is_reported(
    runtime_env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(local_runtime, "port_in_use", lambda host, port: True)
    monkeypatch.setattr(local_runtime, "is_arsis", lambda url: False)
    serve, report = Recorder(), Recorder()

    code = local_runtime.start([], serve=serve, open_browser=Recorder(), report=report)

    assert code == 1
    assert "porta 8765" in report.calls[0][0]
    assert serve.calls == []


def test_failed_migration_is_reported_and_nothing_is_served(
    runtime_env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail() -> None:
        raise MigrationError("Changeset 0009 non applicato: errore di prova")

    monkeypatch.setattr("arsis.migrate.run_migrations", fail)
    serve, report = Recorder(), Recorder()

    code = local_runtime.start(["--no-browser"], serve=serve, report=report)

    assert code == 1
    assert "errore di prova" in report.calls[0][0]
    assert str(runtime_env / "backups") in report.calls[0][0]
    assert serve.calls == []

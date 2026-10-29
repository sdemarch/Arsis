from pathlib import Path

from fastapi.testclient import TestClient

from arsis.core.config import Settings
from arsis.main import create_app


def test_local_runtime_serves_spa_and_keeps_api_routes(tmp_path: Path) -> None:
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    frontend_dir.joinpath("index.html").write_text("<h1>Arsis locale</h1>", encoding="utf-8")
    frontend_dir.joinpath("main.js").write_text("console.log('ok')", encoding="utf-8")
    application = create_app(Settings(serve_frontend=True, frontend_dist_dir=frontend_dir))

    with TestClient(application) as client:
        assert client.get("/school/courses").text == "<h1>Arsis locale</h1>"
        assert client.get("/main.js").text == "console.log('ok')"
        assert client.get("/health/live").status_code == 200

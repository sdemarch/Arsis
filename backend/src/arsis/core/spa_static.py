"""Static-file support for the compiled Angular single-page application."""

from collections.abc import MutableMapping
from pathlib import PurePosixPath
from typing import Any

from fastapi.staticfiles import StaticFiles
from starlette.responses import Response


class SpaStaticFiles(StaticFiles):
    """Serve files normally and redirect client-side routes to Angular's index page."""

    async def get_response(self, path: str, scope: MutableMapping[str, Any]) -> Response:
        filename = PurePosixPath(path).name
        if "." not in filename:
            return await super().get_response("index.html", scope)
        return await super().get_response(path, scope)

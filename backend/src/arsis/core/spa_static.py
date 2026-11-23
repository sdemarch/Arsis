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
            response = await super().get_response("index.html", scope)
            # The installer replaces the generated chunks on every update.  Never let
            # a browser reuse an old index document that refers to removed chunks.
            response.headers["Cache-Control"] = "no-store"
            return response

        response = await super().get_response(path, scope)
        # Angular names production assets with a content hash, so they are safe to
        # cache indefinitely and cannot be confused with assets from another build.
        if response.status_code == 200:
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

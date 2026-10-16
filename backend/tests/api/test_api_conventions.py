from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.testclient import TestClient

from arsis.core.api_models import PaginationParams
from arsis.core.errors import ResourceNotFoundError
from arsis.main import create_app


def test_every_response_has_a_request_id() -> None:
    response = TestClient(create_app()).get("/api/v1")

    assert response.status_code == 200
    assert response.json() == {"name": "Arsis API", "api_version": "v1"}
    assert UUID(response.headers["X-Request-ID"])


def test_valid_client_request_id_is_preserved() -> None:
    response = TestClient(create_app()).get(
        "/health/live", headers={"X-Request-ID": "client-request-42"}
    )

    assert response.headers["X-Request-ID"] == "client-request-42"


def test_domain_errors_use_the_shared_envelope() -> None:
    application = create_app()

    @application.get("/_test/missing", include_in_schema=False)
    def missing() -> None:
        raise ResourceNotFoundError("Persona", "person-1")

    response = TestClient(application).get(
        "/_test/missing", headers={"X-Request-ID": "request-domain-error"}
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": "Risorsa non trovata: Persona",
            "details": {"resource": "Persona", "resource_id": "person-1"},
            "request_id": "request-domain-error",
        }
    }


def test_request_validation_uses_the_shared_envelope() -> None:
    application = create_app()

    @application.get("/_test/page", include_in_schema=False)
    def page(params: Annotated[PaginationParams, Depends()]) -> dict[str, int]:
        return {"offset": params.offset}

    response = TestClient(application).get(
        "/_test/page?page=0", headers={"X-Request-ID": "request-validation-error"}
    )

    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["request_id"] == "request-validation-error"
    assert body["details"]["issues"][0]["loc"] == ["query", "page"]


def test_unexpected_errors_are_hidden_and_keep_the_request_id() -> None:
    application = create_app()

    @application.get("/_test/error", include_in_schema=False)
    def error() -> None:
        raise RuntimeError("sensitive internal detail")

    response = TestClient(application, raise_server_exceptions=False).get(
        "/_test/error", headers={"X-Request-ID": "request-internal-error"}
    )

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "request-internal-error"
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Errore interno del server",
            "details": None,
            "request_id": "request-internal-error",
        }
    }


def test_openapi_operation_ids_are_stable_and_unique() -> None:
    schema = create_app().openapi()
    operation_ids = [
        operation["operationId"]
        for path in schema["paths"].values()
        for operation in path.values()
        if "operationId" in operation
    ]

    assert len(operation_ids) == len(set(operation_ids))
    assert "health_live" in operation_ids
    assert "core_api_index" in operation_ids

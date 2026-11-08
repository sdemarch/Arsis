import pytest
from httpx import ASGITransport, AsyncClient

from arsis.auth.rate_limit import login_rate_limiter
from arsis.main import app


@pytest.fixture(autouse=True)
def reset_login_rate_limiter():
    """Failed logins of one test must not throttle the next."""
    login_rate_limiter.reset()
    yield
    login_rate_limiter.reset()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

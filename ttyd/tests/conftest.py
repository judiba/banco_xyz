import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DEV_OFFLINE", "true")
os.environ.setdefault("APP_ENV", "dev")

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)

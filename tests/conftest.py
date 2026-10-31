import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _no_real_api_key(monkeypatch):
    # Tests only ever use FakeClient; make sure a real client could not authenticate by accident.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)


@pytest.fixture
def orders_data():
    return json.loads((FIXTURES / "orders.json").read_text())


@pytest.fixture
def orders(orders_data):
    return orders_data["orders"]

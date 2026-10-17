"""Every test uses a mocked Apify boundary; real starts and HTTP are forbidden."""

import socket
from unittest.mock import create_autospec

import httpx
import pytest
from apify_client import ApifyClient
from apify_client._models import Run
from apify_client._resource_clients.actor import ActorClient, ActorClientAsync
from apify_client._resource_clients.dataset import DatasetClient

from hirepulse_tools import _runner


def forbidden(*args, **kwargs):
    raise AssertionError("Network calls and real Actor starts are forbidden in tests")


@pytest.fixture(autouse=True)
def mock_apify(monkeypatch):
    factory = create_autospec(ApifyClient)
    client = factory.return_value
    actor = create_autospec(ActorClient, instance=True)
    dataset = create_autospec(DatasetClient, instance=True)
    client.actor.return_value = actor
    client.dataset.return_value = dataset
    actor.call.return_value = Run.model_construct(
        status="SUCCEEDED", default_dataset_id="mock-dataset"
    )
    dataset.list_items.return_value.items = [{"fixture": "mock row"}]
    monkeypatch.setenv("APIFY_TOKEN", "your_token_here")
    monkeypatch.setattr(_runner, "ApifyClient", factory)
    monkeypatch.setattr(ActorClient, "start", forbidden)
    monkeypatch.setattr(ActorClientAsync, "start", forbidden)
    monkeypatch.setattr(httpx.Client, "send", forbidden)
    monkeypatch.setattr(httpx.AsyncClient, "send", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    return factory, client, actor, dataset

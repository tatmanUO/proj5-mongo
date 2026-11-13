
"""
Automated tests for CS 322 Project 5.

Tests Flask routes and MongoDB operations using mocks,
without modifying the actual database.
"""

from unittest.mock import patch, MagicMock

import pytest
from pymongo.errors import PyMongoError

from flask_brevets import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def sample_controls():
    return [
        {
            "miles": "31.1",
            "km": "50",
            "location": "Control 1",
            "open": "Fri 11/13 11:30",
            "close": "Fri 11/13 13:30"
        },
        {
            "miles": "62.1",
            "km": "100",
            "location": "Control 2",
            "open": "Fri 11/13 13:00",
            "close": "Fri 11/13 16:00"
        }
    ]


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACP Brevet Times" in response.data


def test_calculate_times(client):
    response = client.get(
        "/_calc_times",
        query_string={
            "km": 100,
            "brevet_dist": 200,
            "start_time": "2026-11-13T10:00:00-08:00"
        }
    )

    assert response.status_code == 200

    result = response.get_json()["result"]
    assert "open" in result
    assert "close" in result


def test_calculate_times_missing_parameters(client):
    response = client.get("/_calc_times")
    assert response.status_code == 400


def test_submit_valid_controls(client):
    controls = sample_controls()

    with patch(
        "flask_brevets.controls_collection.insert_many"
    ) as mock_insert:
        mock_insert.return_value.inserted_ids = ["1", "2"]

        response = client.post(
            "/submit",
            json={"controls": controls}
        )

        assert response.status_code == 201
        assert response.get_json()["count"] == 2

        mock_insert.assert_called_once_with(controls)


def test_submit_empty_controls(client):
    response = client.post(
        "/submit",
        json={"controls": []}
    )

    assert response.status_code == 400


def test_submit_invalid_json(client):
    response = client.post(
        "/submit",
        data="not valid json",
        content_type="application/json"
    )

    assert response.status_code == 400


def test_submit_missing_fields(client):
    response = client.post(
        "/submit",
        json={
            "controls": [
                {"km": "50"}
            ]
        }
    )

    assert response.status_code == 400


def test_submit_database_error(client):
    with patch(
        "flask_brevets.controls_collection.insert_many",
        side_effect=PyMongoError("Database unavailable")
    ):
        response = client.post(
            "/submit",
            json={"controls": sample_controls()}
        )

        assert response.status_code == 503


def test_display_controls(client):
    controls = sample_controls()

    with patch(
        "flask_brevets.controls_collection.find",
        return_value=controls
    ):
        response = client.get("/display")

        assert response.status_code == 200
        assert b"Saved Brevet Controls" in response.data
        assert b"Control 1" in response.data
        assert b"Control 2" in response.data


def test_display_empty_database(client):
    with patch(
        "flask_brevets.controls_collection.find",
        return_value=[]
    ):
        response = client.get("/display")

        assert response.status_code == 200
        assert b"No Saved Controls" in response.data


def test_display_database_error(client):
    with patch(
        "flask_brevets.controls_collection.find",
        side_effect=PyMongoError("Database unavailable")
    ):
        response = client.get("/display")

        assert response.status_code == 503


def test_unknown_route(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404

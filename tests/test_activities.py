import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Save and restore the module-level `activities` between tests."""
    backup = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(backup)


def test_get_activities():
    # Arrange
    url = "/activities"

    # Act
    resp = client.get(url)

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@example.com"
    url = f"/activities/{activity}/signup"

    # Act
    resp = client.post(url, params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]


def test_signup_already_signed_up():
    # Arrange
    activity = "Chess Club"
    email = "already@mergington.edu"
    url = f"/activities/{activity}/signup"

    # Act
    resp1 = client.post(url, params={"email": email})
    resp2 = client.post(url, params={"email": email})

    # Assert
    assert resp1.status_code == 200
    assert resp2.status_code == 400


def test_unregister_success():
    # Arrange
    activity = "Programming Class"
    existing = app_module.activities[activity]["participants"][0]
    url = f"/activities/{activity}/signup"

    # Act
    resp = client.delete(url, params={"email": existing})

    # Assert
    assert resp.status_code == 200
    assert existing not in app_module.activities[activity]["participants"]


def test_activity_not_found():
    # Arrange
    url = "/activities/NoSuchActivity/signup"

    # Act
    resp = client.post(url, params={"email": "a@b.com"})

    # Assert
    assert resp.status_code == 404

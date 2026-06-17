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
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    activity = "Chess Club"
    email = "newstudent@example.com"
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]


def test_signup_already_signed_up():
    activity = "Chess Club"
    email = "already@mergington.edu"
    resp1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp1.status_code == 200
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_unregister_success():
    activity = "Programming Class"
    existing = app_module.activities[activity]["participants"][0]
    resp = client.delete(f"/activities/{activity}/signup", params={"email": existing})
    assert resp.status_code == 200
    assert existing not in app_module.activities[activity]["participants"]


def test_activity_not_found():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404

import copy

from fastapi.testclient import TestClient

from src.app import app, activities


def _restore_activities(original: dict) -> None:
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_data_and_no_store_header():
    client = TestClient(app)

    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.headers.get("cache-control") == "no-store"


def test_signup_adds_participant_and_is_visible_in_subsequent_get():
    client = TestClient(app)
    original = copy.deepcopy(activities)

    try:
        activity_name = "Chess Club"
        email = "new.student@mergington.edu"

        pre = client.get("/activities").json()[activity_name]["participants"]
        assert email not in pre

        signup = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert signup.status_code == 200

        post = client.get("/activities").json()[activity_name]["participants"]
        assert email in post
    finally:
        _restore_activities(original)


def test_unregister_removes_participant_and_is_visible_in_subsequent_get():
    client = TestClient(app)
    original = copy.deepcopy(activities)

    try:
        activity_name = "Programming Class"
        email = activities[activity_name]["participants"][0]

        unregister = client.post(
            f"/activities/{activity_name}/unregister", params={"email": email}
        )
        assert unregister.status_code == 200

        post = client.get("/activities").json()[activity_name]["participants"]
        assert email not in post
    finally:
        _restore_activities(original)


def test_signup_duplicate_is_rejected():
    client = TestClient(app)
    original = copy.deepcopy(activities)

    try:
        activity_name = "Drama Club"
        email = activities[activity_name]["participants"][0]

        signup = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert signup.status_code == 400
        assert signup.json()["detail"] == "Student already signed up for this activity"
    finally:
        _restore_activities(original)


def test_unregister_missing_participant_is_404():
    client = TestClient(app)
    original = copy.deepcopy(activities)

    try:
        activity_name = "Art Studio"
        email = "not.signed.up@mergington.edu"

        unregister = client.post(
            f"/activities/{activity_name}/unregister", params={"email": email}
        )
        assert unregister.status_code == 404
        assert unregister.json()["detail"] == "Student is not signed up for this activity"
    finally:
        _restore_activities(original)

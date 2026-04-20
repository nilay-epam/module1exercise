import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    # Arrange: No special setup needed for this endpoint

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status code and response content
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data  # Check for a known activity
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_success(client):
    # Arrange: Prepare signup data for an activity with available spots
    activity_name = "Basketball Team"  # This activity starts with no participants
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check successful signup
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]

    # Verify the participant was added
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_duplicate(client):
    # Arrange: First, sign up a student
    activity_name = "Chess Club"
    email = "testduplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Try to sign up the same student again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check for duplicate error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" in data["detail"]


def test_remove_participant_success(client):
    # Arrange: First, sign up a student to an activity
    activity_name = "Soccer Club"
    email = "removetest@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Make DELETE request to remove the participant
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert: Check successful removal
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Removed {email} from {activity_name}" in data["message"]

    # Verify the participant was removed
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_found(client):
    # Arrange: Try to remove a participant who is not signed up
    activity_name = "Art Club"
    email = "nonexistent@mergington.edu"

    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert: Check for not found error
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]
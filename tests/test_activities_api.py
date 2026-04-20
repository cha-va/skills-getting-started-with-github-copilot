"""
Integration tests for Mergington High School Activities API endpoints.

These tests verify the complete HTTP request/response cycle for all API endpoints.
Each test follows the AAA (Arrange-Act-Assert) pattern:
  - Arrange: Set up the test client and test data
  - Act: Execute the HTTP request
  - Assert: Verify the response and state changes
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_all_activities_returns_all_nine(self, client):
        """
        Arrange: Create test client
        Act: Send GET request to /activities
        Assert: Verify all 9 activities are returned
        """
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Club", "Art Club",
            "Drama Club", "Debate Club", "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert set(data.keys()) == set(expected_activities)

    def test_get_activities_returns_correct_structure(self, client):
        """
        Arrange: Create test client
        Act: Send GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity in data.items():
            assert isinstance(activity, dict)
            assert required_fields.issubset(activity.keys()), \
                f"{activity_name} missing required fields"

    def test_get_activities_participants_are_lists(self, client):
        """
        Arrange: Create test client
        Act: Send GET request to /activities
        Assert: Verify participants field is a list of strings
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity in data.items():
            assert isinstance(activity["participants"], list), \
                f"{activity_name} participants is not a list"
            for participant in activity["participants"]:
                assert isinstance(participant, str), \
                    f"{activity_name} has non-string participant"

    def test_get_activities_has_initial_participants(self, client):
        """
        Arrange: Create test client
        Act: Send GET request to /activities
        Assert: Verify some activities have initial participants
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_adds_participant(self, client):
        """
        Arrange: Create test client with a new email
        Act: Post to signup endpoint with valid data
        Assert: Verify participant is added and response is successful
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup",
                              params={"email": email})
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was actually added
        check_response = client.get("/activities")
        activities = check_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_missing_email_returns_error(self, client):
        """
        Arrange: Create test client without email parameter
        Act: Post to signup endpoint without email
        Assert: Verify 422 error is returned
        """
        # Arrange
        activity_name = "Art Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Create test client with invalid activity name
        Act: Post to signup with non-existent activity
        Assert: Verify 404 error with appropriate message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup",
                              params={"email": email})
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_error(self, client):
        """
        Arrange: Create test client, then signup same student twice
        Act: Post to signup endpoint with already-registered email
        Assert: Verify 400 error for duplicate signup
        """
        # Arrange
        activity_name = "Soccer Club"
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        # Act: Try to signup again with same email
        response = client.post(f"/activities/{activity_name}/signup",
                              params={"email": email})
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_already_signed_up_not_added_twice(self, client):
        """
        Arrange: Create test client, signup a student
        Act: Attempt duplicate signup
        Assert: Verify participant count doesn't increase
        """
        # Arrange
        activity_name = "Art Club"
        email = "student@mergington.edu"
        
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity_name]["participants"])
        
        # First signup
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        response2 = client.get("/activities")
        after_first = len(response2.json()[activity_name]["participants"])
        
        # Act: Try duplicate signup
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        response3 = client.get("/activities")
        after_second = len(response3.json()[activity_name]["participants"])
        
        # Assert
        assert after_first == initial_count + 1
        assert after_second == after_first  # Should not increase again

    def test_signup_multiple_different_students(self, client):
        """
        Arrange: Create test client, signup multiple different students
        Act: Post signup for two different emails
        Assert: Verify both participants are in the activity
        """
        # Arrange
        activity_name = "Drama Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email1})
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email2})
        
        response = client.get("/activities")
        
        # Assert
        participants = response.json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants
        assert len(participants) == 2  # Only the two we added

    def test_signup_with_existing_participant(self, client):
        """
        Arrange: Create test client (Chess Club already has participants)
        Act: Try to signup with existing participant email
        Assert: Verify error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup",
                              params={"email": email})
        
        # Assert
        assert response.status_code == 400


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success_removes_participant(self, client):
        """
        Arrange: Create test client, signup student first
        Act: Delete from activity
        Assert: Verify participant is removed
        """
        # Arrange
        activity_name = "Programming Class"
        email = "remove_me@mergington.edu"
        
        # First signup
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister",
                                params={"email": email})
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        check_response = client.get("/activities")
        activities_data = check_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Create test client with invalid activity name
        Act: Delete from non-existent activity
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister",
                                params={"email": email})
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up_returns_error(self, client):
        """
        Arrange: Create test client with student not signed up
        Act: Delete from activity without prior signup
        Assert: Verify 400 error
        """
        # Arrange
        activity_name = "Science Club"
        email = "never_signed_up@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister",
                                params={"email": email})
        
        # Assert
        assert response.status_code == 400
        assert "Not signed up" in response.json()["detail"]

    def test_unregister_missing_email_returns_error(self, client):
        """
        Arrange: Create test client without email parameter
        Act: Delete from activity without email
        Assert: Verify 422 error
        """
        # Arrange
        activity_name = "Debate Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister")
        
        # Assert
        assert response.status_code == 422

    def test_unregister_from_initial_participant(self, client):
        """
        Arrange: Create test client (Chess Club has initial participants)
        Act: Unregister an initial participant
        Assert: Verify they are removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Initial participant
        
        # Verify they start as a participant
        response1 = client.get("/activities")
        assert email in response1.json()[activity_name]["participants"]
        
        # Act
        response = client.delete(f"/activities/{activity_name}/unregister",
                                params={"email": email})
        
        # Assert
        assert response.status_code == 200
        
        response2 = client.get("/activities")
        assert email not in response2.json()[activity_name]["participants"]

    def test_unregister_cannot_unregister_twice(self, client):
        """
        Arrange: Create test client, signup then unregister
        Act: Try to unregister again
        Assert: Verify second unregister fails with 400
        """
        # Arrange
        activity_name = "Gym Class"
        email = "twice@mergington.edu"
        
        # Signup
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        # First unregister
        response1 = client.delete(f"/activities/{activity_name}/unregister",
                                 params={"email": email})
        assert response1.status_code == 200
        
        # Act: Try to unregister again
        response2 = client.delete(f"/activities/{activity_name}/unregister",
                                 params={"email": email})
        
        # Assert
        assert response2.status_code == 400
        assert "Not signed up" in response2.json()["detail"]

    def test_unregister_decreases_participant_count(self, client):
        """
        Arrange: Create test client, signup then unregister
        Act: Track participant count before and after unregister
        Assert: Verify count decreases by exactly 1
        """
        # Arrange
        activity_name = "Art Club"
        email = "counter@mergington.edu"
        
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity_name]["participants"])
        
        # Signup
        client.post(f"/activities/{activity_name}/signup",
                   params={"email": email})
        
        response2 = client.get("/activities")
        after_signup = len(response2.json()[activity_name]["participants"])
        
        # Act
        client.delete(f"/activities/{activity_name}/unregister",
                     params={"email": email})
        
        response3 = client.get("/activities")
        after_unregister = len(response3.json()[activity_name]["participants"])
        
        # Assert
        assert after_signup == initial_count + 1
        assert after_unregister == initial_count

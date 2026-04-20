"""
Unit tests for Mergington High School Activities API business logic.

These tests verify the logic and data structures of individual components.
Each test follows the AAA (Arrange-Act-Assert) pattern:
  - Arrange: Set up the test data or conditions
  - Act: Execute the operation being tested
  - Assert: Verify the results and state
"""

import pytest
from src.app import activities


class TestActivityInitialization:
    """Test suite for activity data initialization"""

    def test_all_nine_activities_exist(self, client):
        """
        Arrange: Get activities from app
        Act: Count the activities
        Assert: Verify exactly 9 activities exist
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Art Club" in data
        assert "Drama Club" in data
        assert "Debate Club" in data
        assert "Science Club" in data

    def test_activity_has_description_field(self, client):
        """
        Arrange: Get activities from app
        Act: Check Chess Club
        Assert: Verify description field exists and is non-empty
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        # Assert
        assert "description" in chess_club
        assert isinstance(chess_club["description"], str)
        assert len(chess_club["description"]) > 0

    def test_activity_has_schedule_field(self, client):
        """
        Arrange: Get activities from app
        Act: Check Programming Class
        Assert: Verify schedule field exists and is non-empty
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        prog_class = data["Programming Class"]
        
        # Assert
        assert "schedule" in prog_class
        assert isinstance(prog_class["schedule"], str)
        assert len(prog_class["schedule"]) > 0

    def test_activity_has_max_participants_field(self, client):
        """
        Arrange: Get activities from app
        Act: Check Gym Class
        Assert: Verify max_participants field exists and is integer
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        gym_class = data["Gym Class"]
        
        # Assert
        assert "max_participants" in gym_class
        assert isinstance(gym_class["max_participants"], int)
        assert gym_class["max_participants"] > 0

    def test_activity_has_participants_field(self, client):
        """
        Arrange: Get activities from app
        Act: Check Basketball Team
        Assert: Verify participants field is a list
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        basketball = data["Basketball Team"]
        
        # Assert
        assert "participants" in basketball
        assert isinstance(basketball["participants"], list)

    def test_activity_max_participants_is_positive(self, client):
        """
        Arrange: Get activities from app
        Act: Check max_participants for all activities
        Assert: Verify all max_participants values are positive integers
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity in data.items():
            assert activity["max_participants"] > 0, \
                f"{activity_name} has invalid max_participants"


class TestParticipantCounting:
    """Test suite for participant counting logic"""

    def test_empty_activity_has_zero_participants(self, client):
        """
        Arrange: Get activities from app
        Act: Check Basketball Team which starts empty
        Assert: Verify participant list is empty
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        basketball = data["Basketball Team"]
        
        # Assert
        assert len(basketball["participants"]) == 0

    def test_activity_with_participants_has_correct_count(self, client):
        """
        Arrange: Get activities from app
        Act: Check Chess Club which has initial participants
        Assert: Verify participant count matches expected value
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        # Assert
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_participant_count_increases_on_signup(self, client):
        """
        Arrange: Get initial count from Soccer Club
        Act: Signup a new participant
        Assert: Verify count increases by exactly 1
        """
        # Arrange
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Soccer Club"]["participants"])
        
        # Act
        client.post("/activities/Soccer Club/signup",
                   params={"email": "new@mergington.edu"})
        
        response2 = client.get("/activities")
        
        # Assert
        new_count = len(response2.json()["Soccer Club"]["participants"])
        assert new_count == initial_count + 1

    def test_participant_count_decreases_on_unregister(self, client):
        """
        Arrange: Get count from Programming Class, signup, then check
        Act: Unregister the student
        Assert: Verify count decreases by exactly 1
        """
        # Arrange
        email = "temp@mergington.edu"
        
        client.post("/activities/Programming Class/signup",
                   params={"email": email})
        
        response1 = client.get("/activities")
        count_before_unregister = len(response1.json()["Programming Class"]["participants"])
        
        # Act
        client.delete("/activities/Programming Class/unregister",
                     params={"email": email})
        
        response2 = client.get("/activities")
        
        # Assert
        count_after_unregister = len(response2.json()["Programming Class"]["participants"])
        assert count_after_unregister == count_before_unregister - 1

    def test_different_activities_have_independent_counts(self, client):
        """
        Arrange: Get counts from two different activities
        Act: Signup to one activity
        Assert: Verify only that activity's count changes
        """
        # Arrange
        email = "test@mergington.edu"
        
        response1 = client.get("/activities")
        chess_count_before = len(response1.json()["Chess Club"]["participants"])
        art_count_before = len(response1.json()["Art Club"]["participants"])
        
        # Act
        client.post("/activities/Art Club/signup",
                   params={"email": email})
        
        response2 = client.get("/activities")
        
        # Assert
        chess_count_after = len(response2.json()["Chess Club"]["participants"])
        art_count_after = len(response2.json()["Art Club"]["participants"])
        
        assert chess_count_after == chess_count_before
        assert art_count_after == art_count_before + 1


class TestDataConsistency:
    """Test suite for data consistency and integrity"""

    def test_no_duplicate_participants_in_activity(self, client):
        """
        Arrange: Get an activity with participants
        Act: Extract participants list
        Assert: Verify no duplicates exist (set length == list length)
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity in data.items():
            participants = activity["participants"]
            assert len(participants) == len(set(participants)), \
                f"{activity_name} has duplicate participants"

    def test_all_participants_are_email_strings(self, client):
        """
        Arrange: Get all activities
        Act: Check all participant values
        Assert: Verify all participants are non-empty email-like strings
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity in data.items():
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant, f"Not email-like: {participant}"
                assert len(participant) > 3

    def test_activity_name_keys_match_response_structure(self, client):
        """
        Arrange: Get activities response
        Act: Extract activity names from response
        Assert: Verify all activity names are properly formatted
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name in data.keys():
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            assert activity_name[0].isupper()  # Should start with capital letter

    def test_max_participants_reasonable_values(self, client):
        """
        Arrange: Get all activities
        Act: Check max_participants for all
        Assert: Verify values are within reasonable range (1-500)
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity in data.items():
            max_p = activity["max_participants"]
            assert 1 <= max_p <= 500, \
                f"{activity_name} has unreasonable max_participants: {max_p}"

    def test_schedule_field_contains_time_information(self, client):
        """
        Arrange: Get all activities
        Act: Check schedule fields
        Assert: Verify schedules contain time-related keywords
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        time_keywords = ["AM", "PM", "Monday", "Tuesday", "Wednesday", 
                        "Thursday", "Friday", "Saturday", "Sunday"]
        
        for activity_name, activity in data.items():
            schedule = activity["schedule"]
            has_time_info = any(keyword in schedule for keyword in time_keywords)
            assert has_time_info, \
                f"{activity_name} schedule lacks time information"


class TestSignupValidation:
    """Test suite for signup validation logic"""

    def test_email_parameter_required(self, client):
        """
        Arrange: Prepare request without email parameter
        Act: Send signup request
        Assert: Verify request fails with 422 error
        """
        # Arrange & Act
        response = client.post("/activities/Art Club/signup")
        
        # Assert
        assert response.status_code == 422

    def test_activity_name_required(self, client):
        """
        Arrange: Prepare request with email but invalid activity
        Act: Send signup request with wrong activity name
        Assert: Verify request fails with 404 error
        """
        # Arrange
        email = "test@mergington.edu"
        
        # Act
        response = client.post("/activities/Invalid/signup",
                              params={"email": email})
        
        # Assert
        assert response.status_code == 404

    def test_cannot_signup_multiple_times_same_email(self, client):
        """
        Arrange: Signup a student once successfully
        Act: Attempt signup again with same email
        Assert: Verify error response on second attempt
        """
        # Arrange
        activity = "Drama Club"
        email = "twice@mergington.edu"
        
        client.post(f"/activities/{activity}/signup",
                   params={"email": email})
        
        # Act
        response = client.post(f"/activities/{activity}/signup",
                              params={"email": email})
        
        # Assert
        assert response.status_code == 400

    def test_same_email_can_signup_to_different_activities(self, client):
        """
        Arrange: Prepare to signup same student to multiple activities
        Act: Signup student to Activity 1, then Activity 2
        Assert: Verify both signups succeed without error
        """
        # Arrange
        email = "multi@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Science Club"
        
        # Act
        response1 = client.post(f"/activities/{activity1}/signup",
                               params={"email": email})
        response2 = client.post(f"/activities/{activity2}/signup",
                               params={"email": email})
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify in both activities
        data = client.get("/activities").json()
        assert email in data[activity1]["participants"]
        assert email in data[activity2]["participants"]

"""
Tests for the Mergington High School Activities API.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- ARRANGE: Set up test data and preconditions
- ACT: Execute the endpoint being tested
- ASSERT: Verify the response and state changes
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_success(self, client, fresh_activities):
        """
        ARRANGE: No special setup needed - activities already loaded
        ACT: Make GET request to /activities
        ASSERT: Should return 200 with all activities
        """
        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data

    def test_activities_have_correct_structure(self, client, fresh_activities):
        """
        ARRANGE: No special setup needed
        ACT: Get activities and inspect structure
        ASSERT: Each activity should have required fields
        """
        # ACT
        response = client.get("/activities")
        activities_data = response.json()

        # ASSERT
        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_chess_club_has_initial_participants(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities fixture provides initial participants
        ACT: Get activities and check Chess Club
        ASSERT: Should have 2 participants
        """
        # ACT
        response = client.get("/activities")
        activities_data = response.json()

        # ASSERT
        chess_club = activities_data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self, client, fresh_activities):
        """
        ARRANGE: Use fresh_activities with known state
        ACT: Sign up a new participant for Chess Club
        ASSERT: Should return 200 and add participant to activity
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_already_registered_returns_error(self, client, fresh_activities):
        """
        ARRANGE: Pick an email already in Chess Club
        ACT: Try to sign up same email again
        ASSERT: Should return 400 error
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_not_found(self, client, fresh_activities):
        """
        ARRANGE: Use an activity name that doesn't exist
        ACT: Try to sign up for fake activity
        ASSERT: Should return 404 error
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "newstudent@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_activities_same_student(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities with known state
        ACT: Sign up same student for two different activities
        ASSERT: Should succeed for both
        """
        # ARRANGE
        email = "testuser@mergington.edu"

        # ACT
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )

        # ASSERT
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in fresh_activities["Chess Club"]["participants"]
        assert email in fresh_activities["Programming Class"]["participants"]

    def test_signup_email_case_sensitivity(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities
        ACT: Sign up with different email cases
        ASSERT: Emails should be stored as provided
        """
        # ARRANGE
        activity_name = "Art Studio"

        # ACT
        response1 = client.post(
            f"/activities/{activity_name}/signup?email=Student@Test.com"
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup?email=student@test.com"
        )

        # ASSERT
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert "Student@Test.com" in fresh_activities[activity_name]["participants"]
        assert "student@test.com" in fresh_activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_success(self, client, fresh_activities):
        """
        ARRANGE: Use a participant already registered in an activity
        ACT: Unregister them from the activity
        ASSERT: Should return 200 and remove participant
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        initial_count = len(fresh_activities[activity_name]["participants"])

        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_not_registered_returns_error(self, client, fresh_activities):
        """
        ARRANGE: Use an email not registered for the activity
        ACT: Try to unregister them
        ASSERT: Should return 400 error
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_not_found(self, client, fresh_activities):
        """
        ARRANGE: Use an activity name that doesn't exist
        ACT: Try to unregister from fake activity
        ASSERT: Should return 404 error
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "anyone@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_all_participants(self, client, fresh_activities):
        """
        ARRANGE: Get all participants from Tennis Club
        ACT: Unregister each one
        ASSERT: Should remove all, activity should be empty
        """
        # ARRANGE
        activity_name = "Tennis Club"
        participants = fresh_activities[activity_name]["participants"].copy()

        # ACT & ASSERT
        for email in participants:
            response = client.post(
                f"/activities/{activity_name}/unregister?email={email}"
            )
            assert response.status_code == 200
            assert email not in fresh_activities[activity_name]["participants"]

        # ASSERT final state
        assert len(fresh_activities[activity_name]["participants"]) == 0


class TestIntegrationSignupUnregister:
    """Integration tests for signup and unregister workflows"""

    def test_signup_then_unregister_workflow(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities
        ACT: Sign up a student, then unregister them
        ASSERT: Participant should be added then removed
        """
        # ARRANGE
        activity_name = "Robotics Club"
        email = "workflow@test.edu"

        # ACT: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT signup worked
        assert signup_response.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]

        # ACT: Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT unregister worked
        assert unregister_response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]

    def test_signup_unregister_signup_again_workflow(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities
        ACT: Sign up, unregister, then sign up again
        ASSERT: All operations should succeed
        """
        # ARRANGE
        activity_name = "Debate Team"
        email = "repeater@test.edu"

        # ACT & ASSERT: First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response1.status_code == 200

        # ACT & ASSERT: Unregister
        response2 = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response2.status_code == 200

        # ACT & ASSERT: Signup again (should succeed)
        response3 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response3.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]

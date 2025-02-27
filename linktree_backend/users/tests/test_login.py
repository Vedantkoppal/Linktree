import pytest
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
class TestUserLogin:
    
    def setup_method(self, method):
        """Set up API client and test user before each test."""
        self.client = APIClient()
        User.objects.all().delete()  # ✅ Clean database
        self.user = User.objects.create_user(username="john", email="john@example.com", password="password123")  # ✅ Test user

    def test_valid_login(self):
        """Test if a user can log in successfully."""
        response = self.client.post("/api/login/", {
            "username": "john",
            "password": "password123"
        }, format="json")

        assert response.status_code == 200
        assert "access" in response.data  # ✅ JWT access token
        assert "refresh" in response.data  # ✅ JWT refresh token

    def test_invalid_password(self):
        """Test login with an incorrect password."""
        response = self.client.post("/api/login/", {
            "username": "john",
            "password": "wrongpassword"
        }, format="json")

        assert response.status_code == 401
        assert response.data["detail"] == "No active account found with the given credentials"

    def test_non_existent_user(self):
        """Test login with a username that does not exist."""
        response = self.client.post("/api/login/", {
            "username": "nonexistent",
            "password": "password123"
        }, format="json")

        assert response.status_code == 401
        assert response.data["detail"] == "No active account found with the given credentials"

    def test_missing_credentials(self):
        """Test login with missing username or password."""
        response = self.client.post("/api/login/", {
            "username": "john"
        }, format="json")  # Missing password

        assert response.status_code == 400
        assert "password" in response.data
        assert response.data["password"][0] == "This field is required."

        response = self.client.post("/api/login/", {
            "password": "password123"
        }, format="json")  # Missing username

        assert response.status_code == 400
        assert "username" in response.data
        assert response.data["username"][0] == "This field is required."

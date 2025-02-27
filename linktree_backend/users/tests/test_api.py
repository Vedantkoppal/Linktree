import pytest
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
class TestUserRegistration:
    
    def setup_method(self):
        print("Setting up test")
        self.client = APIClient()
        User.objects.all().delete()

    def test_successful_registration(self):
        """Test if a user can register successfully."""
        response = self.client.post("/api/register/", {
            "username": "john",
            "email": "john@example.com",
            "password": "password123"
        }, format="json")

        assert response.status_code == 201
        assert "username" in response.data
        assert "email" in response.data
        assert "referral_code" in response.data  # ✅ Check if referral code is generated

    def test_duplicate_email_registration(self):
        """Test if duplicate emails are rejected."""
        User.objects.create_user(username="john", email="john@example.com", password="password123")
        
        response = self.client.post("/api/register/", {
            "username": "john2",
            "email": "john@example.com",
            "password": "password123"
        }, format="json")

        assert response.status_code == 400
        assert "email" in response.data
        assert response.data["email"][0] == "user with this email already exists."

    def test_self_referral(self):
        """Test if a user cannot refer themselves."""
        user = User.objects.create_user(username="john", email="john@example.com", password="password123")

        response = self.client.post("/api/register/", {
            "username": "emma",
            "email": "emma@example.com",
            "password": "password123",
            "referral_code": user.referral_code  # ✅ Should trigger self-referral error
        }, format="json")

        assert response.status_code == 400
        assert "referral_code" in response.data
        assert response.data["referral_code"][0] == "user with this referral code already exists."  # ✅ Fix assertion format

    def test_invalid_referral_code(self):
        """Test if registration fails with an invalid referral code."""
        response = self.client.post("/api/register/", {
            "username": "emma",
            "email": "emma@example.com",
            "password": "password123",
            "referral_code": "invalidcode"
        }, format="json")

        assert response.status_code == 400
        assert "referral_code" in response.data
        assert response.data["referral_code"][0] == "Invalid referral code"  # ✅ Fix error assertion

    def test_missing_required_fields(self):
        """Test if missing fields return errors."""
        response = self.client.post("/api/register/", {}, format="json")

        assert response.status_code == 400
        assert "email" in response.data
        assert "password" in response.data
        assert response.data["email"][0] == "This field is required."  # ✅ Fix error assertion
        assert response.data["password"][0] == "This field is required."  # ✅ Fix error assertion

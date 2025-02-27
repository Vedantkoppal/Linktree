import pytest
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
class TestUserReferrals:

    def setup_method(self, method):
        """Set up API client and test users before each test."""
        self.client = APIClient()
        User.objects.all().delete()  # ✅ Clean database

        # ✅ Register the referrer using the API
        referrer_response = self.client.post("/api/register/", {
            "username": "don",
            "email": "don@example.com",
            "password": "password123"
        }, format="json")

        # ✅ Extract referral code from the response
        self.referrer_code = referrer_response.data.get("referral_code")

        # ✅ Authenticate referrer
        login_response = self.client.post("/api/login/", {
            "username": "don",
            "password": "password123"
        }, format="json")

        self.access_token = login_response.data["access"]
        self.auth_headers = {"Authorization": f"Bearer {self.access_token}"}  # ✅ Auth headers for requests

        # ✅ Register referred users using the referral code
        self.client.post("/api/register/", {
            "username": "ved",
            "email": "ved@example.com",
            "password": "password123",
            "referral_code": self.referrer_code  # ✅ Corrected key``
        }, format="json")

        self.client.post("/api/register/", {
            "username": "nik",
            "email": "nik@example.com",
            "password": "password123",
            "referral_code": self.referrer_code  # ✅ Corrected key
        }, format="json")

    def test_get_referrals_list(self):
        """Test if a user can fetch their list of referred users."""
        response = self.client.get("/api/referrals/", headers=self.auth_headers)

        assert response.status_code == 200
        assert len(response.data) == 2  # ✅ Don referred Ved & Nik
        assert response.data[0]["username"] in ["ved", "nik"]
        assert response.data[1]["username"] in ["ved", "nik"]

    def test_get_referrals_list_empty(self):
        """Test if a user with no referrals gets an empty list."""
        # Create a new user without referrals
        new_user_response = self.client.post("/api/register/", {
            "username": "david",
            "email": "david@example.com",
            "password": "password123"
        }, format="json")

        new_user_login = self.client.post("/api/login/", {
            "username": "david",
            "password": "password123"
        }, format="json")

        auth_headers = {"Authorization": f"Bearer {new_user_login.data['access']}"}

        response = self.client.get("/api/referrals/", headers=auth_headers)

        assert response.status_code == 200
        assert response.data == []  # ✅ No referrals

    def test_get_referral_stats(self):
        """Test if a user can fetch their referral stats."""
        response = self.client.get("/api/referral-stats/", headers=self.auth_headers)

        assert response.status_code == 200
        assert response.data["total_referrals"] == 2  # ✅ Don referred 2 users

    def test_unauthenticated_access_referrals(self):
        """Test if an unauthenticated user cannot access referrals."""
        response = self.client.get("/api/referrals/")  # ❌ No auth headers

        assert response.status_code == 401
        assert "detail" in response.data
        assert response.data["detail"] == "Authentication credentials were not provided."

    def test_unauthenticated_access_referral_stats(self):
        """Test if an unauthenticated user cannot access referral stats."""
        response = self.client.get("/api/referral-stats/")  # ❌ No auth headers

        assert response.status_code == 401
        assert "detail" in response.data
        assert response.data["detail"] == "Authentication credentials were not provided."

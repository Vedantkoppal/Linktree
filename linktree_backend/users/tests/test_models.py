import pytest
from users.models import User, Referral, Reward
from django.core.exceptions import ValidationError
from django.utils.timezone import now

@pytest.mark.django_db  # ✅ Ensures database access for tests
def test_user_creation():
    """Test user model to ensure it saves correctly."""
    user = User.objects.create_user(username="john", email="john@example.com", password="password123")
    assert user.username == "john"
    assert user.email == "john@example.com"
    assert user.check_password("password123")  # ✅ Ensures password is hashed

@pytest.mark.django_db
def test_email_uniqueness():
    """Ensure duplicate emails are not allowed."""
    User.objects.create_user(username="john", email="john@example.com", password="password123")
    with pytest.raises(ValidationError):  # ✅ Expect an error
        user2 = User(username="john2", email="john@example.com")
        user2.full_clean()  # This triggers Django validation

@pytest.mark.django_db
def test_referral_code_validation():
    """Ensure referral code belongs to an existing user."""
    referrer = User.objects.create_user(username="john", email="john@example.com", password="password123")
    referred = User(username="emma", email="emma@example.com", password="password123", referred_by=referrer)
    referred.full_clean()  # ✅ No error should occur

@pytest.mark.django_db
def test_self_referral():
    """Prevent users from referring themselves."""
    user = User.objects.create_user(username="john", email="john@example.com", password="password123")
    with pytest.raises(ValidationError):
        user.referred_by = user
        user.full_clean()  # Should raise an error

@pytest.mark.django_db
def test_reward_creation():
    """Ensure rewards are assigned correctly."""
    referrer = User.objects.create_user(username="john", email="john@example.com", password="password123")
    Reward.objects.create(user=referrer, reward_type="credits", amount=10, date_earned=now())
    assert Reward.objects.filter(user=referrer).count() == 1

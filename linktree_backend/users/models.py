import hashlib
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import AbstractUser 
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Added timestamp for user creation

    # ✅ Fix for groups and permissions conflict
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",  # ✅ Fix for clash with auth.User.groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",  # ✅ Fix for clash with auth.User.user_permissions
        blank=True
    )

    def clean(self):
        """Prevent users from referring themselves."""
        if self.referred_by and self.referred_by == self:
            raise ValidationError("A user cannot refer themselves.")

    def save(self, *args, **kwargs):
        if not self.referral_code:
            secret_key = settings.SECRET_KEY  # Use Django's SECRET_KEY as salt
            hash_input = (self.email + secret_key).encode()  # Combine email & secret key
            self.referral_code = hashlib.sha256(hash_input).hexdigest()[:20]  # Take first 20 chars
        super().save(*args, **kwargs)

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referred_users")
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referrer_of")
    date_referred = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('successful', 'Successful')], default='pending')

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"

class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rewards")
    reward_type = models.CharField(max_length=50, choices=[("credits", "Credits"), ("premium", "Premium Access")])
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_earned = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.reward_type}: {self.amount}"

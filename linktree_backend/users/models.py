from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:10]  # Generate a unique referral code
        super().save(*args, **kwargs)

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referrer_set")
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referred_user_set")
    date_referred = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('successful', 'Successful')], default='pending')

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"

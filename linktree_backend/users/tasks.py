from celery import shared_task
from users.models import User, Referral, Reward
from django.utils.timezone import now

@shared_task
def process_referral(user_id):
    try:
        # Get the referred user (newly registered user)
        referred_user = User.objects.get(id=user_id)
        
        # Ensure the user was actually referred
        if not referred_user.referred_by:
            return "User was not referred by anyone."

        referrer = referred_user.referred_by  # Get the referrer
        referral_entry = Referral.objects.filter(referred_user=referred_user).first()

        # If referral entry does not exist, create one
        if not referral_entry:
            referral_entry = Referral.objects.create(
                referrer=referrer,
                referred_user=referred_user,
                date_referred=now(),
                status="pending",
            )

        # ✅ Update referral status to "successful" if needed
        if referral_entry.status == "pending":
            referral_entry.status = "successful"
            referral_entry.save()

            # ✅ Reward the referrer (Example: Give 10 credits)
            reward = Reward.objects.create(
                user=referrer,
                reward_type="credits",
                amount=10,  # ✅ You can adjust reward logic
                date_earned=now(),
            )

            return f"Referral processed: {referrer.username} earned {reward.amount} credits."

        return "Referral already processed."
    
    except User.DoesNotExist:
        return "User does not exist."
    except Exception as e:
        return f"Error processing referral: {str(e)}"

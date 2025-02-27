from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])  # ✅ Enforce strong passwords

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'referral_code']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        """Ensure email is unique with a custom message before database-level validation."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")  # ✅ Custom error message
        return value

        
    def validate_referral_code(self, value):
        """Ensure referral code belongs to a valid user and prevent self-referral."""
        if not value:  # ✅ Allow users to register without a referral
            return value

        referrer = User.objects.filter(referral_code=value).first()
        
        if not referrer:
            raise serializers.ValidationError("Invalid referral code")  # ✅ Custom error message

        request_user = self.context.get("request").user if self.context.get("request") else None
        if request_user and referrer == request_user:
            raise serializers.ValidationError("A user cannot refer themselves.")  # ✅ Fix error message

        return value

    def create(self, validated_data):
        """Prevent self-referral & ensure correct validation order."""
        referral_code = validated_data.pop("referral_code", None)
        user = User.objects.create_user(**validated_data)  # ✅ Create the user first

        # ✅ Validate referral before saving user
        if referral_code:
            referrer = User.objects.filter(referral_code=referral_code).first()
            if referrer and user.email == referrer.email:  # ✅ Prevent self-referral
                raise serializers.ValidationError({"referral_code": ["A user cannot refer themselves."]})

            user.referred_by = referrer  # ✅ Link referred user
            user.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

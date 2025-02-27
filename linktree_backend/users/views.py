from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import exception_handler


from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.core.cache import cache

from users.tasks import process_referral  # ✅ Import the Celery task



def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code  # ✅ Add status code to response

    return response

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # ✅ Call Celery task only if referred_by exists
        if user.referred_by:
            process_referral.delay(user.id) 

        return Response({
            "message": "User registered successfully",
            "username": user.username,
            "email": user.email,
            "referral_code": user.referral_code
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


    @method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True))
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny] 

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # Generate reset token (This should ideally be a secure password reset flow)
        reset_token = get_random_string(20)

        # Send email (Replace with actual email sending mechanism)
        send_mail(
            "Password Reset",
            f"Use this token to reset your password: {reset_token}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

class ReferralsView(generics.ListAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(referred_by=self.request.user)

class ReferralStatsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        cache_key = f"referral_stats_{user.id}"  # ✅ Unique cache key for each user
        data = cache.get(cache_key)

        if not data:  # If not cached, fetch from DB
            total_referrals = User.objects.filter(referred_by=user).count()
            successful_referrals = User.objects.filter(referred_by=user, referrals__status="successful").count()
            data = {"total_referrals": total_referrals, "successful_referrals": successful_referrals}

            cache.set(cache_key, data, timeout=600)  # ✅ Cache for 10 minutes

        return Response(data, status=200)


# Create your views here.

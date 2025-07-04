from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework import status, generics
from .models import User, Prediction, UserProfile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .utils import predict_stock_price
from .serializers import PredictionSerializer
from django.conf import settings

import stripe

# Create your views here.
class RegisterApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")
        confirm_password = request.data.get("confirm_password", "")

        if not all([username, email, password, confirm_password]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        
        return Response({
            "message": "User successfully created",
            "login_page": request.build_absolute_uri(reverse('login'))
        }, status=status.HTTP_201_CREATED)
    
class LoginApiView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({"message": "Login successful", "dashboard": request.build_absolute_uri(reverse('dashboard'))}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class PredictView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticker = request.data.get("ticker")
        if not ticker:
            return Response({"error": "Ticker is required"}, status=400)
        try:
            result = predict_stock_price(ticker)

            prediction = Prediction.objects.create(
                user=request.user,
                ticker=ticker,
                predicted_price=result["next_day_price"],
                mse=result["mse"],
                rmse=result["rmse"],
                r2=result["r2"],
                plot_history=result["plot_history"].replace(settings.MEDIA_ROOT + "/", ""),
                plot_comparison=result["plot_comparison"].replace(settings.MEDIA_ROOT + "/", ""),
            )

            return Response({
                "next_day_price": result["next_day_price"],
                "mse": result["mse"],
                "rmse": result["rmse"],
                "r2": result["r2"],
                "plot_urls": [request.build_absolute_uri(settings.MEDIA_URL + prediction.plot_history),
                              request.build_absolute_uri(settings.MEDIA_URL + prediction.plot_comparison)]
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class ListPredictionsView(generics.ListAPIView):
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Prediction.objects.filter(user=self.request.user)

        ticker = self.request.query_params.get('ticker')
        date = self.request.query_params.get('date')

        if ticker:
            queryset = queryset.filter(ticker__iexact=ticker)
        if date:
            queryset = queryset.filter(created_at__date=date)

        return queryset.order_by('-created_at')

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Ensure Stripe customer exists
        if not user.userprofile.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            user.userprofile.stripe_customer_id = customer.id
            user.userprofile.save()

        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            customer=user.userprofile.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': 19900,
                    'recurring': {'interval': 'month'},
                    'product_data': {'name': 'Pro Membership'},
                },
                'quantity': 1,
            }],
            mode="subscription",
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/",
        )

        return Response({"session_id": session.id})
    
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=webhook_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        # Handle events
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            customer_id = session.get("customer")
            if customer_id:
                UserProfile.objects.filter(stripe_customer_id=customer_id).update(is_pro=True)

        elif event["type"] == "customer.subscription.deleted":
            customer_id = event["data"]["object"].get("customer")
            if customer_id:
                UserProfile.objects.filter(stripe_customer_id=customer_id).update(is_pro=False)

        return HttpResponse(status=200)
    
def login_page(request):
    return render(request, "stock_predict_app/login.html")

def register_page(request):
    return render(request, "stock_predict_app/register.html")

@login_required
def dashboard(request):
    predictions = Prediction.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "stock_predict_app/dashboard.html", {
        "predictions": predictions
    })
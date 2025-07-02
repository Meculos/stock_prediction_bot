from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics
from .models import User, Prediction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout

from .utils import predict_stock_price
from .serializers import PredictionSerializer
from django.conf import settings

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
        }, status=status.HTTP_201_CREATED)

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

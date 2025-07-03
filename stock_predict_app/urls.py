from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # DRF views urls
    path('api/v1/register/', views.RegisterApiView.as_view()),
    path('api/v1/predict/', views.PredictView.as_view()),
    path('api/v1/predictions/', views.ListPredictionsView.as_view()),
    path('api/subscribe/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path("webhooks/stripe/", views.StripeWebhookView.as_view(), name="stripe-webhook"),

    # JWT urls
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
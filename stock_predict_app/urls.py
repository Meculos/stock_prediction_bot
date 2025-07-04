from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # DRF views urls
    path('api/v1/register/', views.RegisterApiView.as_view()),
    path('api/v1/login/', views.LoginApiView.as_view()),
    path('api/v1/predict/', views.PredictView.as_view()),
    path('api/v1/predictions/', views.ListPredictionsView.as_view()),
    path('api/subscribe/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhooks/stripe/', views.StripeWebhookView.as_view(), name="stripe-webhook"),

    # django template urls
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # JWT urls
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
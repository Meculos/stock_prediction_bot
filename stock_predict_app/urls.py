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

    # JWT urls
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
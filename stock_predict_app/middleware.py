from datetime import date
from django.utils.deprecation import MiddlewareMixin
from .models import Prediction
from django.http import JsonResponse

class PredictionQuotaMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated and not request.user.userprofile.is_pro:
            if request.path == "/api/v1/predict/" and request.method == "POST":
                today = date.today()
                count = Prediction.objects.filter(user=request.user, created_at__date=today).count()
                if count >= 5:
                    return JsonResponse(
                        {"detail": "Free tier limit reached. Upgrade to Pro."},
                        status=429
                    )
        return None

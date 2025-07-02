from rest_framework import serializers
from .models import Prediction

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ["id", "user", "ticker", "predicted_price", "mse", "rmse", "r2", "plot_history", "plot_comparism", "created_at"]
        read_only_fields = ["id", "created_at"]
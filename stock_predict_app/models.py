from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    predicted_price = models.FloatField()
    mse = models.FloatField()
    rmse = models.FloatField()
    r2 = models.FloatField()
    plot_history = models.ImageField(upload_to='plots/')
    plot_comparison = models.ImageField(upload_to='plots/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} on {self.created_at.date()}"


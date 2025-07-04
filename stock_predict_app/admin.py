from django.contrib import admin
from .models import Prediction, UserProfile, TelegramUser

# Register your models here.
admin.site.register(Prediction)
admin.site.register(UserProfile)
admin.site.register(TelegramUser)
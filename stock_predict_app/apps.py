from django.apps import AppConfig


class StockPredictAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock_predict_app'

    def ready(self):
        import stock_predict_app.signals

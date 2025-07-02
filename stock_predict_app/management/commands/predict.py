import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from stock_predict_app.utils import predict_stock_price
from stock_predict_app.models import Prediction

User = get_user_model()

class Command(BaseCommand):
    help = 'Run stock prediction for a given ticker or all tickers'

    def add_arguments(self, parser):
        parser.add_argument('--ticker', type=str, help='Single stock ticker (e.g., TSLA)')
        parser.add_argument('--all', action='store_true', help='Predict for all tickers in DB')

    def handle(self, *args, **options):
        ticker = options['ticker']
        predict_all = options['all']

        if not ticker and not predict_all:
            raise CommandError("You must provide --ticker or --all")

        if ticker:
            self.stdout.write(f"🔮 Predicting for ticker: {ticker}")
            predict_stock_price(ticker)
        elif predict_all:
            tickers = Prediction.objects.values_list('ticker', flat=True).distinct()
            for tk in tickers:
                self.stdout.write(f"🔮 Predicting for: {tk}")
                predict_stock_price(tk)

        self.stdout.write(self.style.SUCCESS('✅ Prediction(s) complete.'))

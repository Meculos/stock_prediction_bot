import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score
from keras.models import load_model
import os
import joblib
import uuid

from django.conf import settings

async def predict_stock_price(ticker):
    model_path = settings.MODEL_PATH
    model = load_model(model_path)

    scaler_path = model_path.replace(".keras", "_scaler.save")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError("Scaler file missing")

    scaler = joblib.load(scaler_path)

    df = yf.download(ticker, period="10y")
    if df.empty or "Close" not in df.columns:
        raise ValueError("Invalid or missing data from yfinance")

    close_prices = df["Close"].values.reshape(-1, 1)
    scaled_prices = scaler.transform(close_prices)

    X = []
    y = []

    for i in range(60, len(scaled_prices)):
        X.append(scaled_prices[i - 60:i, 0])
        y.append(scaled_prices[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    predictions = model.predict(X)
    predictions_rescaled = scaler.inverse_transform(predictions.reshape(-1, 1))
    y_rescaled = scaler.inverse_transform(y.reshape(-1, 1))

    mse = mean_squared_error(y_rescaled, predictions_rescaled)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_rescaled, predictions_rescaled)

    plot_dir = os.path.join(settings.MEDIA_ROOT, 'plots')
    os.makedirs(plot_dir, exist_ok=True)

    plot1_path = os.path.join(plot_dir, f"{uuid.uuid4()}_history.png")
    plot2_path = os.path.join(plot_dir, f"{uuid.uuid4()}_comparison.png")

    plt.figure(figsize=(10, 4))
    plt.plot(df["Close"])
    plt.title(f"{ticker} Closing Price History")
    plt.savefig(plot1_path)
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.plot(y_rescaled, label='Actual')
    plt.plot(predictions_rescaled, label='Predicted')
    plt.title("Actual vs Predicted")
    plt.legend()
    plt.savefig(plot2_path)
    plt.close()

    return {
        "next_day_price": float(predictions_rescaled[-1]),
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
        "plot_history": plot1_path,
        "plot_comparison": plot2_path,
    }

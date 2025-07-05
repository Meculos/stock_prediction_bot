📈 Stock Prediction Platform

This is a full-stack Django project built for the Internshala Telegram Bot Internship Final Assignment. The platform allows users to:

Register/login (JWT & Django session-based)

Predict stock prices using an LSTM .keras model

View metrics (MSE, RMSE, R²) and PNG charts

Use a Telegram bot (/predict, /latest, /subscribe, etc.)

Manage free/pro subscriptions using Stripe (test mode)

Bonus: Docker + Gunicorn setup for production-ready deployment



---

⚙ Features

Django + DRF backend

Tailwind CSS frontend

JWT + session-based login

Celery-like async behavior via Django management commands

Telegram bot integration

Stripe test-mode billing

Dockerized (Gunicorn, PostgreSQL, collectstatic)

/healthz/ endpoint for container health check



---

🚨 Docker Note

> Due to local system storage limits (Docker build consumed over 20GB), I was unable to run the final Docker container after a successful build.

✅ docker-compose build ran successfully.

✅ Dockerfile and Compose config were finalized (Gunicorn, PostgreSQL, collectstatic, health check).

❌ Final docker-compose up could not be executed due to system memory constraints.


If needed, this can be easily tested in a higher-resource machine or cloud CI/CD environment.

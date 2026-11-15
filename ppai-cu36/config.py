import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ppai-dsi-2026-cu36")

    # Base de datos SQLite (archivo local)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "bolsines.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API GPS Tracker de la cátedra (modelo XTR-4500L)
    GPS_API_URL = os.environ.get("GPS_API_URL", "http://localhost:8080")
    GPS_API_KEY_XTR = os.environ.get("GPS_API_KEY_XTR", "sk_xtr_9F3a7C21bE6d4A10f2c8e5b7d913")
    GPS_API_TIMEOUT = float(os.environ.get("GPS_API_TIMEOUT", "5"))

import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:abcd1234@localhost/repair_service_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # For flash messages
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

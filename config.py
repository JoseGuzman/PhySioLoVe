"""
Set Flask Config variables.

We need a file called .env where the variables are stored.

Check here: https://hackersandslackers.com/configure-flask-applications/
Check here to use S3 for static content:
https://abhishekm47.medium.com/serve-static-assets-on-s3-bucket-a-complete-flask-guide-fbe128d97e71
"""

from os import environ
from pathlib import Path

from dotenv import load_dotenv

BASEDIR = Path(__file__).resolve().parent

# Load .env file from project root
load_dotenv(BASEDIR / ".env")


class Config:
    """Base configuration (shared by all environments)."""

    SECRET_KEY = environ.get("SECRET_KEY", "dev-fallback-key")

    SQLALCHEMY_DATABASE_URI = environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///physiolove.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Convert string to boolean safely
    DEBUG = environ.get("FLASK_DEBUG", "False").lower() == "true"

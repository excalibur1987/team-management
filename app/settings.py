import os
import random
import string
from datetime import timedelta

import pytz
from sqlalchemy.pool import NullPool

from app.utils.extended_objects import SubscriptableEnum


class Config(object):
    # General Flask configurations
    APP_NAME = os.getenv("APP_NAME")
    FLASK_APP = os.getenv("FLASK_APP", "autoapp:app")
    TZ = pytz.timezone(os.getenv("TZ", "UTC"))
    SERVER_NAME = os.getenv("SERVER_NAME", None)
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", 0) == 1
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "".join(
            random.choices(
                string.ascii_lowercase
                + string.ascii_uppercase
                + string.digits
                + string.printable,
                k=20,
            )
        ),
    )

    # Regex rule to check against user's password
    PASSWORD_RULE = os.getenv("PASSWORD_RULE", ".*")
    # Storage target to handle file storage
    STORAGE_TARGET = os.getenv("STORAGE_TARGET", "s3")

    # Sqlalchemy Configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    SESSION_PERMANENT = True
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}

    # JWT Configurations
    JWT_SECRET_KEY = os.getenv(
        "SECRET_KEY",
        SECRET_KEY,
    )
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_IDENTITY_CLAIM = "user"
    JWT_ERROR_MESSAGE_KEY = "error"
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE", "GET"]
    JWT_CSRF_IN_COOKIES = False

    # AWS Configurations
    AWS_ACCESS_KEY_ID = os.getenv("BUCKETEER_AWS_ACCESS_KEY_ID", None)
    AWS_REGION = os.getenv("BUCKETEER_AWS_REGION", None)
    AWS_SECRET_ACCESS_KEY = os.getenv("BUCKETEER_AWS_SECRET_ACCESS_KEY", None)
    S3_BUCKET_NAME = os.getenv("BUCKETEER_BUCKET_NAME", None)
    AWS_ENDPOINT = os.getenv("AWS_ENDPOINT", None)

    VALID_DEPARTMENTS = SubscriptableEnum(
        list(
            set(
                [item.upper() for item in os.getenv("VALID_DEPARTMENTS", "").split(",")]
                + ["OTHER"]
            )
        )
    )
    VALID_POSITIONS = SubscriptableEnum(
        [
            "CEO",
            "MANAGER",
            "ASSISTANT MANAGER",
            "EMPLOYEE",
            "TRAINEE",
        ]
    )

    # Flak-Mail Settings
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_SSL = bool(int(os.getenv("MAIL_USE_SSL")))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class DevConfig(Config):

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60 * 60)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASK_ENV = "development"
    SECRET_KEY = "secretkey"
    JWT_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False


class TestConfig(DevConfig):

    TESTING = True


class ProdConfig(Config):

    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=180)
    FLASK_ENV = "production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

from flask import Flask
from flask_cors import CORS
import os

from . import config

from .app_blueprint import bp
import logging

__version__ = "0.2.12"


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app, expose_headers='WWW-Authenticate')

    configure_app(app)

    if test_config is not None:
        app.config.update(test_config)

    app.register_blueprint(bp)
    app.url_map.strict_slashes = False

    return app


def configure_app(app):

    # Load logging scheme from config.py
    app_settings = os.getenv('APP_SETTINGS')
    if not app_settings:
        app.config.from_object(config.BaseConfig)
    else:
        app.config.from_object(app_settings)

    # Configure logging
    # handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
    # handler.setLevel(app.config['LOGGING_LEVEL'])
    # formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    # handler.setFormatter(formatter)
    # app.logger.addHandler(handler)



import logging
import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    HOME = os.path.expanduser("~")
    CORS_HEADERS = 'Content-Type'
    SECRET_KEY = '1d94e52c-1c89-4515-b87a-f48cf3cb7f0b'
    LOGGING_LEVEL = logging.DEBUG
    JSON_SORT_KEYS = False
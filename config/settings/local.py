from .base import *  # noqa
from .base import env

DEBUG = env.bool("DEBUG", default=True)

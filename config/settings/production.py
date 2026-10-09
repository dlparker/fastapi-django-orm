from .base import *  # noqa
from .base import env

# No defaults: fail at startup rather than run with an insecure configuration
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
DEBUG = False

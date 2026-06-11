from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Limitador de tasa (anti fuerza bruta). El almacenamiento se configura por
# entorno (RATELIMIT_STORAGE_URI); en producción usar Redis/Memcached.
limiter = Limiter(key_func=get_remote_address)

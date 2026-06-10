import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Solo para ejecución directa en desarrollo. En contenedor/producción se
    # sirve con gunicorn (ver Dockerfile). El host se toma del entorno y por
    # defecto escucha solo en localhost para no exponer la app sin querer.
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "8000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)

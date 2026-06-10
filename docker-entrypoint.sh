#!/bin/sh
set -e

# Crea tablas y, si SEED_ON_START=1, carga datos de ejemplo
flask --app wsgi init-db
if [ "$SEED_ON_START" = "1" ]; then
  flask --app wsgi seed
fi

exec "$@"

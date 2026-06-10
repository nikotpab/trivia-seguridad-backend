FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY wsgi.py gunicorn.conf.py docker-entrypoint.sh ./

# Permisos del entrypoint y usuario no-root
RUN chmod +x docker-entrypoint.sh \
    && useradd --create-home appuser \
    && chown -R appuser /srv/app
USER appuser

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]

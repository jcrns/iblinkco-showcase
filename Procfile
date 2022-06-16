worker: celery -A webapp worker -l info -B --loglevel=info
beat: celery -A webapp beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
web: bin/start-pgbouncer-stunnel gunicorn webapp.wsgi
web: daphne webapp.asgi:application --port $PORT --bind 0.0.0.0 -v2
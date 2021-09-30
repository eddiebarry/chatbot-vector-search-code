timeout = 300
bind = "127.0.0.1:8381"
workers = 5
worker_class = "gevent"
# newrelic-admin run-program gunicorn --bind=0.0.0.0:8000 --workers 1 --max-requests=1000 -c /app/logging/project/docker_gunicorn_configuration.py wsgi:application
#!/bin/bash
# tail -f /dev/null
newrelic-admin run-program gunicorn --bind=0.0.0.0:8000 --workers $NUM_WORKERS --max-requests=1000 -c /app/vector/docker_gunicorn_configuration.py wsgi:app
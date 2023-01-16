#!/bin/bash

docker-compose -f docker-compose.yml up -d

if [ "$DATABASE" = "postgres" ]; then
  echo "Checking for postgres..."

  while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
    sleep 0.1
  done

  echo "PostgreSQL is up."
fi

python manage.py migrate
tox
docker-compose -f docker-compose.yml stop

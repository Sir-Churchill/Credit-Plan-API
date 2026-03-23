#!/usr/bin/env bash

set -e

echo "Waiting for database to be ready at $host:3306..."

while ! nc -z ${host:-db} 3306; do
  echo "MySQL at ${host:-db}:3306 is unavailable - sleeping..."
  sleep 2
done

echo "Database is up! Starting the application..."

exec "$@"
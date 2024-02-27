#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# If we want to delete all data
# python manage.py flush --no-input
python manage.py migrate

# If we have several languages in django
# python manage.py compilemessages

# If we have Elastic Search
# python manage.py search_index --rebuild

exec "$@"

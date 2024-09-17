web: daphne wavetext.asgi:application --port $PORT --bind 0.0.0.0 -v2
chatworker: python manage.py runworker --settings=wavetext.settings -v2

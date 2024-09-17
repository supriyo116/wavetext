web: gunicorn wavetext.wsgi:application --log-file -
daphne: daphne wavetext.asgi:application --port $PORT --bind 0.0.0.0

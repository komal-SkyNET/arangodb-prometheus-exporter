GUNICORN_CONFIG=config/gunicorn.conf ARANGO_PASSWORD='bkwdbfvwdv' gunicorn -k gevent -c "${GUNICORN_CONFIG}" "source.wsgi_app:run(True)"

GUNICORN_CONFIG=source/config/gunicorn.conf ARANGO_PASSWORD='7ggchjvb' gunicorn -k gevent -c "${GUNICORN_CONFIG}" "source.wsgi_app:run(True)"

FROM python:3.7.6-slim
RUN apt-get update && apt-get install -y curl 
WORKDIR /source
COPY ./source/ .
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt --trusted-host=pypi.org --trusted-host=files.pythonhosted.org
EXPOSE 9101/tcp
CMD gunicorn -k gevent -c "${GUNICORN_CONFIG}" "source.wsgi_app:run(True)" ${GUNI_ARGS}

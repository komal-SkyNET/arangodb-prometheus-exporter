from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import yaml, logging, logging.config
from source.processor import Processor

with open('source/config/config.yaml', 'r') as yamlFile:
    config = yaml.load(yamlFile, Loader=yaml.FullLoader)
logging.config.dictConfig(config['LOGGING'])
logger = logging.getLogger(__name__)
logger.debug('load configs: %s' % config)
app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})
proc = None
def run(start=False):
    global proc
    if start:
        proc = Processor(config)
        proc.update_metrics_background_job()
    return app
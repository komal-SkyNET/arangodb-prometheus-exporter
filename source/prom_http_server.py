import logging, os, logging.config
import yaml
import time
import threading
import signal, sys
from metrics import start_metrics_server
from processor import Processor
with open('config/config.yaml', 'r') as yamlFile:
    config = yaml.load(yamlFile, Loader=yaml.FullLoader)
logging.config.dictConfig(config['LOGGING'])
logger = logging.getLogger(__name__)
logger.debug('load configs: %s' % config)

class App:
    
    def __init__(self):
        global logger, config
        self.logger = logger
        self.config = config
        self._stop = False
        signal.signal(signal.SIGINT, self.stop)
        pass
    
    def run(self):
        proc = Processor(self.config)
        start_metrics_server(self.config['APP']['port'])
        logger.info("Metrics server started")
        while not self._stop:
            logger.debug("Begin generating metrics")
            proc.generate_all_metrics()
            time.sleep(self.config['APP']['scrape_interval_secs'])
            logger.debug("Completed generating metrics")
        logger.info('Metrics server shutting down.')
        sys.exit(0)
    
    def stop(self, *args):
        self.logger.info('Received interrupt. Stopping.')
        self._stop = True

app = App()
if __name__ == '__main__':
    app.run()
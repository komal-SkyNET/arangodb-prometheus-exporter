from source.database import Database
from requests import ConnectionError
import logging, signal, threading, sys, time
from source.metrics import *


logger = logging.getLogger(__name__)
EXPOSED_METRICS_MAP = {}

class Processor:

    def __init__(self, config):
        self.db = Database(config)
        self.config = config
        self.io_metrics = {}
        self.admin_stat_metrics = {}
        self._stop = False
        self.thread = None
        signal.signal(signal.SIGINT, self.stop)
    
    def _update_metrics_loop(self):
        while not self._stop:
            logger.debug("Begin generating/updating metrics")
            self.generate_all_metrics()
            time.sleep(self.config['APP']['scrape_interval_secs'])
            logger.debug("Completed generating metrics")
        logger.info('Stopping update metrics thread')
        sys.exit(0)

    def update_metrics_background_job(self):
        if self.thread:
            if self.thread.isAlive:
                logger.warn('metrics updater thread is already running')
                return
        self.thread = threading.Thread(target=self._update_metrics_loop, daemon=True)
        self.thread.start()
    
    def stop(self, *args):
        logger.info('Received interrupt. Stopping.')
        self._stop = True

    def generate_all_metrics(self):
        if self.db.is_connected:
            try:
                if self.is_leader():
                    ARANGODB_LEADER.set(1)
                    self.generate_ticks_metric()
                    self.generate_io_metrics()
                    self.generate_admin_stats_metrics()
                else:
                    ARANGODB_LEADER.set(0)
            except IndexError as e1:
                logger.error(e1)
            except ConnectionError as e2:
                logger.error(e2)
                self.db.setup_connection()
        else:
            # unregister_stats_metrics_offline()
            self.db.setup_connection()

    def is_leader(self):
        url = '/_admin/server/mode'
        response = self.db.http_handler.get(url).json()
        if response.get('errorNum') == 1496:
            return False
        elif response.get('code') == 200:
            return True
        return False


    def generate_ticks_metric(self):
        url = '/_api/replication/logger-state'
        response = self.db.http_handler.get(url).json()
        LAST_LEADER_TICK.set(response['state']['lastLogTick'])
        try:
            LAST_FOLLOWER_TICK.set(response['clients'][0]['lastServedTick'])
        except IndexError as e:
            logger.warn('ArangoDB: NO follower! %s' % e)

    def generate_io_metrics(self):
        url = '/_db/_system/_admin/aardvark/statistics/short'
        response = self.db.http_handler.get(url).json()
        io_metrics_map = flatten_json(response)
        set_gauge_metrics_from_dict(io_metrics_map)
    
    def generate_admin_stats_metrics(self):
        url = '/_admin/statistics'
        response = self.db.http_handler.get(url).json()
        stat_metrics_map = flatten_json(response)
        set_gauge_metrics_from_dict(stat_metrics_map)


def flatten_json(ip_json, prefix='arangodb', result_map={}):
    for k, v in ip_json.items():
        if type(v) in (int, float, bool):
            key = prefix+'_'+k
            result_map[key] = v
        elif type(v) == dict:
            key = prefix+'_'+k
            flatten_json(v, key, result_map)
    return result_map

def set_gauge_metrics_from_dict(ip_map):
    for k, v in ip_map.items():
        if EXPOSED_METRICS_MAP.get(k):
            EXPOSED_METRICS_MAP.get(k).set(v)
        else:
            EXPOSED_METRICS_MAP[k] = Gauge(k.replace('-','_'), '')
            EXPOSED_METRICS_MAP[k].set(v)

# def unregister_stats_metrics_offline():
#     for k in EXPOSED_METRICS_MAP.keys():
#         REGISTRY.unregister(k)
#     EXPOSED_METRICS_MAP.clear()
    

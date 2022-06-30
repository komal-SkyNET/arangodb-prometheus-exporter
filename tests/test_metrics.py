from tests.util import BaseTestCase
import threading, time, unittest
import requests, json
from prometheus_client import REGISTRY
from time import sleep
from source.processor import Processor

class TestMetrics(BaseTestCase):

    # call generate_all_metrics twice to handle db not already connected scenario
    def test_follower(self):
        #admin_stats, admin_mode, replication, admin_stats_short
        self.set_arango_response(None, 'admin_server_mode_follower.json', 'replication_state_follower.json', None)
        self.side_effect_connection_not_leader()
        Processor(self.config).generate_all_metrics()
        Processor(self.config).generate_all_metrics()
        c = self.app.test_client()
        response = c.get('/metrics')
        response_dict = self.prometheus_http_metrics_map(response)
        self.assertEquals(200, response.status_code)
        self.assertEquals(response_dict['arangodb_is_leader'], 0.0)
        self.assertEquals(response_dict['arangodb_up'], 1.0)

    def test_admin_leader(self):
        self.set_arango_response('admin_statistics.json', 'admin_server_mode_leader.json', 'replication_state_leader.json', 'admin_statistics_short.json')
        c = self.app.test_client()
        Processor(self.config).generate_all_metrics()
        Processor(self.config).generate_all_metrics()
        response = c.get('/metrics')
        response_dict = self.prometheus_http_metrics_map(response)
        self.assertEquals(200, response.status_code)
        self.assertEquals(response_dict['arangodb_is_leader'], 1.0)
        self.assertEquals(response_dict['arangodb_up'], 1.0)
        self.assertEquals(response_dict['arangodb_last_leader_tick'], 5779239)
        self.assertEquals(response_dict['arangodb_last_follower_tick'], 5779227)

    def test_admin_stats(self):
        self.set_arango_response('admin_statistics.json', 'admin_server_mode_leader.json', 'replication_state_leader.json', 'admin_statistics_short.json')
        c = self.app.test_client()
        Processor(self.config).generate_all_metrics()
        Processor(self.config).generate_all_metrics()
        response = c.get('/metrics')
        response_dict = self.prometheus_http_metrics_map(response)
        self.assertEquals(200, response.status_code)
        self.assertEquals(response_dict['arangodb_is_leader'], 1.0)
        self.assertEquals(response_dict['arangodb_up'], 1.0)
        self.assertEquals(response_dict['arangodb_code'], 200)
        self.assertEquals(response_dict['arangodb_server_physicalMemory'], 33547984896)
        self.assertEquals(response_dict['arangodb_client_httpConnections'], 18)


    def prometheus_http_metrics_map(self, http_response):
        result = {}
        for line in http_response.data.splitlines():
            val = line.split()
            if not val[0] == b'#':
                result[val[0].decode("utf-8")] = float(val[1].decode("utf-8"))
        return result
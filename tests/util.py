import mock, threading, time, sys, yaml, json
from unittest import TestCase
from source.wsgi_app import app, run, proc

class BaseTestCase(TestCase):
    

    def setUp(self):
        with open('tests/config.yaml') as test_configs:
            self.config = yaml.load(test_configs, Loader=yaml.FullLoader)
        self.patch_arango = mock.patch('source.database.Connection')
        self.mock_arango = self.patch_arango.start()
        self.mock_arango_response = mock.MagicMock()
        self.mock_arango.return_value.__getitem__.return_value.connection.action.get = self.mock_arango_response
        self.mock_arango_response.side_effect = self.side_effect_for_arango_response
        self.arango_response = {}
        self.app = app
        self.run = run
        self.proc = proc

    def tearDown(self):
        self.patch_arango.stop()

    def set_arango_response(self, admin_stats, admin_mode, replication, admin_stats_short):  
        def file_read(file_name):
            if file_name:
                json_mock = mock.MagicMock()
                with open('tests/data_samples/'+file_name, 'r') as ip:
                    json_mock.json.return_value = json.loads(ip.read())
                    return json_mock
            else:
                return None
        self.arango_response['/_admin/statistics'] = file_read(admin_stats)
        self.arango_response['/_db/_system/_admin/aardvark/statistics/short'] = file_read(admin_stats_short)
        self.arango_response['/_api/replication/logger-state'] = file_read(replication)
        self.arango_response['/_admin/server/mode'] = file_read(admin_mode)

    def side_effect_for_arango_response(self, *args, **kwargs):
        return self.arango_response[args[0]]

    def side_effect_connection_not_leader(self, *args, **kwargs):
        self.mock_arango.side_effect = Exception('not a leader')

from pyArango.connection import Connection
import os, logging, time
from source.metrics import ARANGODB_UP, ARANGODB_LEADER
logger = logging.getLogger(__name__)

class Database:

    def __init__(self, config, name=None):
        # @name : database name to connect to
        self.is_connected = False
        self.endpoint = config['APP']['arango']['endpoint']
        self.username = config['APP']['arango']['username']
        self.max_retries = config['APP']['arango']['max_retries']
        self.password = os.environ.get('ARANGO_PASSWORD', 'root')
        self.setup_connection(name)

    def setup_connection(self, name=None):
        try:
            logger.debug('Triggered setup_connection() to DB')
            conn = Connection(self.endpoint, self.username, self.password, max_retries=self.max_retries)
            self.db = conn[name if name else '_system']
            self.http_handler = self.db.connection.action
            self.is_connected=True
            ARANGODB_UP.set(1)
            logger.info('Connected to %s' % self.db)
        except Exception as e:
            if ("not a leader" in str(e)):
                logger.debug(
                    "Arango %s NOT A LEADER", self.endpoint)
                ARANGODB_UP.set(1)
                self.is_connected = False
                ARANGODB_LEADER.set(0)
            else:
                ARANGODB_UP.set(0)
                ARANGODB_LEADER.set(0)
                self.is_connected = False
                logger.error("Exception while trying to connect %s", str(e))
        time.sleep(2)


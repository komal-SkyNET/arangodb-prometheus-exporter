from prometheus_client import start_http_server, Counter, Gauge, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, CollectorRegistry
# In-built arango metrics not defined here, dynamically generated from internal API calls
# Unregister default metrics
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_collected_total'])


LAST_LEADER_TICK = Gauge('arangodb_last_leader_tick',
                                     'Last tick received form arangodb leader')
LAST_FOLLOWER_TICK = Gauge('arangodb_last_follower_tick',
                                     'Last tick received form arangodb follower')
ARANGODB_UP = Gauge('arangodb_up',
                                    'State of arango DB')
ARANGODB_LEADER = Gauge('arangodb_is_leader',
                                    'Is the DB leader')
ARANGODB_UP.set(0)

def start_metrics_server(port):
    start_http_server(port)
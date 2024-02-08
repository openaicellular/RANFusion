#system_monitoring.py is located in health_check directory
import psutil
from collections import defaultdict
from logs.logger_config import setup_logger 
from logs.logger_config import setup_logger, TEST_RUN_ID

# Set up the system resource logger
system_resource_logger = setup_logger('system_resource_logger', 'logs/system_resource.log', TEST_RUN_ID)


def default_resource_usage():
    return {'cpu': [], 'memory': []}

class SystemMonitor:
    def __init__(self, network_state):
        self.network_state = network_state
        self.entity_resource_usage = defaultdict(default_resource_usage)

    def get_system_resources(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        return {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage
        }

    def track_entity_resource_usage(self, entity_id, entity_type):
        entity_cpu_usage = psutil.cpu_percent(interval=0.1)
        entity_memory_usage = psutil.virtual_memory().percent
        self.entity_resource_usage[entity_id]['cpu'].append(entity_cpu_usage)
        self.entity_resource_usage[entity_id]['memory'].append(entity_memory_usage)
        return {
            'entity_id': entity_id,
            'entity_type': entity_type,
            'cpu_usage': entity_cpu_usage,
            'memory_usage': entity_memory_usage
        }

    def log_resource_usage(self):
        system_resources = self.get_system_resources()
        system_resource_logger.info({
            'type': 'System',
            'cpu_usage': system_resources['cpu_usage'],
            'memory_usage': system_resources['memory_usage']
        })

        for ue in self.network_state.ues:
            ue_resources = self.track_entity_resource_usage(ue.id, 'UE')
            system_resource_logger.info({
                'type': 'UE',
                'id': ue.id,
                'cpu_usage': ue_resources['cpu_usage'],
                'memory_usage': ue_resources['memory_usage']
            })

        for cell_id, cell in self.network_state.cells.items():
            cell_resources = self.track_entity_resource_usage(cell_id, 'Cell')
            system_resource_logger.info({
                'type': 'Cell',
                'id': cell_id,
                'cpu_usage': cell_resources['cpu_usage'],
                'memory_usage': cell_resources['memory_usage']
            })

        for gNodeB_id, gNodeB in self.network_state.gNodeBs.items():
            gNodeB_resources = self.track_entity_resource_usage(gNodeB_id, 'gNodeB')
            system_resource_logger.info({
                'type': 'gNodeB',
                'id': gNodeB_id,
                'cpu_usage': gNodeB_resources['cpu_usage'],
                'memory_usage': gNodeB_resources['memory_usage']
            })


# do_health_check.py located in health_check directory
import sys
import time
from .server_status import check_server_status
from .database_status import check_database_status
from .system_resources import check_system_resources
from database.time_utils import get_current_time_ntp, server_pools
from logs.logger_config import health_check_logger  # Make sure this import is correct

# Configuration for database retries
MAX_RETRIES = 3
RETRY_INTERVAL = 5  # in seconds

def check_time_utility():
    try:
        current_time = get_current_time_ntp()
        return {'status': 'UP', 'time': current_time}
    except Exception as e:
        health_check_logger.error(f"Time utility check failed: {str(e)}")
        return {'status': 'DOWN', 'error': str(e)}

def perform_health_check(network_state):
    health_check_logger.info("Performing health check...waiting for all components to be up...")
    server_status = check_server_status()
    system_resources = check_system_resources()
    time_utility_status = check_time_utility()

    # Attempt to check database status with retries
    database_status = None
    for attempt in range(MAX_RETRIES):
        database_status = check_database_status(network_state)
        if database_status.get('status') == 'UP':
            break
        health_check_logger.warning(f"Database check failed, attempt {attempt + 1}/{MAX_RETRIES}. Retrying in {RETRY_INTERVAL} seconds...")
        time.sleep(RETRY_INTERVAL)

    health_check_logger.info(f"Server Status: {server_status}")
    health_check_logger.info(f"Database Status: {database_status}")
    health_check_logger.info(f"System Resources: {system_resources}")
    health_check_logger.info(f"Time Utility Status: {time_utility_status}")

    if (server_status.get('status') != 'UP' or
        database_status.get('status') != 'UP' or
        system_resources.get('status') != 'UP' or
        time_utility_status.get('status') != 'UP'):
        health_check_logger.error("Health check failed. Exiting...")
        sys.exit(1)
    else:
        health_check_logger.info("All systems are operational.")
        return True
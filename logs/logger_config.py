# logger_config.py for define all log in log folder
import logging
import os
import json
import gzip
from datetime import datetime
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor
from database.time_utils import get_current_time_ntp
import uuid

# Generate a unique test run ID
TEST_RUN_ID = str(uuid.uuid4())

class JsonFormatter(logging.Formatter):
    def __init__(self, test_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_id = test_id

    def format(self, record):
        log_record = {
            "level": record.levelname,
            "timestamp": get_current_time_ntp(),
            "message": record.getMessage(),
            "test_id": self.test_id  # Include the test identifier in the log record
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)


def setup_logger(name, log_file, test_id, level=logging.INFO, max_log_size=100 * 1024 * 1024, backup_count=10):
    """Function to set up a logger with asynchronous and buffered logging."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create log directory if it doesn't exist
    log_directory = os.path.dirname(log_file)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Create a rotating file handler with asynchronous logging
    file_handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
    file_handler.setLevel(level)
    formatter = JsonFormatter(test_id=test_id)

    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger

def compress_log_file(log_file):
    """Compress the log file using gzip, if it exists, after log rotation."""
    log_file_backup = log_file + ".1"  # Assuming 1 is the first backup file

    if os.path.exists(log_file_backup):
        with open(log_file_backup, 'rb') as log:
            with gzip.open(log_file_backup + '.gz', 'wb') as compressed_log:
                compressed_log.writelines(log)

        # Remove the original log file (backup)
        os.remove(log_file_backup)

# Initialize loggers for all components
ue_logger = setup_logger('ue_logger', 'logs/ue_logger.log', TEST_RUN_ID)
cell_logger = setup_logger('cell_logger', 'logs/cell_logger.log', TEST_RUN_ID)
gnodeb_logger = setup_logger('gnodeb_logger', 'logs/gnodeb_logger.log', TEST_RUN_ID)
cell_load_logger = setup_logger('cell_load_logger', 'logs/cell_load.log', TEST_RUN_ID)
traffic_update = setup_logger('traffic_update', 'logs/traffic_update.log', TEST_RUN_ID)
database_logger = setup_logger('database_logger', 'logs/database_logger.log', TEST_RUN_ID)
system_resource_logger = setup_logger('system_resource_logger', 'logs/system_resource.log', TEST_RUN_ID)
health_check_logger = setup_logger('health_check_logger', 'logs/health_check_logger.log', TEST_RUN_ID)
server_logger = setup_logger('server_logger', 'logs/server_logger.log', TEST_RUN_ID)
sector_logger = setup_logger('sector_logger', 'logs/sector_logger.log', TEST_RUN_ID)
# Dictionary to hold loggers and their respective log files for compression
log_files = {
    'ue_logger': 'logs/ue_logger.log',
    'cell_logger': 'logs/cell_logger.log',
    'gnodeb_logger': 'logs/gnodeb_logger.log',
    'cell_load_logger': 'logs/cell_load.log',
    'traffic_update': 'logs/traffic_update.log',
    'database_logger': 'logs/database_logger.log',
    'system_resource_logger': 'logs/system_resource.log',
    'server_logger': 'logs/server_logger.log',
    'sector_logger': 'logs/sector_logger.log'
}

# Use ThreadPoolExecutor to compress log files
with ThreadPoolExecutor(max_workers=1) as executor:
    for log_file in log_files.values():
        # Schedule log compression for older log files (e.g., once a day)
        executor.submit(compress_log_file, log_file)
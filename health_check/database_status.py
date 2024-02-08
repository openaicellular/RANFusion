#database_status.py is located in health check directory
from database.database_manager import DatabaseManager

def check_database_status(network_state):
    # Now passing network_state to DatabaseManager
    db_manager = DatabaseManager(network_state)
    connected = db_manager.test_connection()
    return {
        'status': 'UP' if connected else 'DOWN',
        'details': 'Successfully connected to the database' if connected else 'Failed to connect to the database'
    }

if __name__ == "__main__":
    status = check_database_status()
    print(status)
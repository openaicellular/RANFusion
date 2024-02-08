#system_resources.py
#This file located in health check directory
# system_resources.py
import psutil

def check_system_resources():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent

    # Define what you consider to be healthy thresholds for CPU and memory usage
    cpu_threshold = 85  # Example threshold
    memory_threshold = 85  # Example threshold

    # Determine the status based on the usage
    status = 'UP' if cpu_usage < cpu_threshold and memory_usage < memory_threshold else 'DOWN'

    return {
        'status': status,  # Include the 'status' key
        'cpu_usage': f'{cpu_usage}%',
        'memory_usage': f'{memory_usage}%'
    }

if __name__ == "__main__":
    resources = check_system_resources()
    print(resources)
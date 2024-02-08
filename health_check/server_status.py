# server_status.py located in health_check directory
import os
import platform
import subprocess

def get_system_uptime():
    try:
        if platform.system() == "Windows":
            # Using systeminfo on Windows to get the uptime
            uptime_info = subprocess.check_output('systeminfo | find "System Boot Time"', shell=True)
            return uptime_info.decode().strip()
        elif platform.system() == "Linux" or platform.system() == "Darwin":
            # Using the 'uptime' command on Unix-like systems
            return os.popen('uptime').readline().strip()
        else:
            raise Exception("Unsupported operating system")
    except Exception as e:
        return "Error retrieving uptime: " + str(e)

def check_server_status():
    uptime = get_system_uptime()
    return {
        'status': 'UP' if uptime and not uptime.startswith("Error") else 'DOWN',
        'uptime': uptime
    }

if __name__ == "__main__":
    status = check_server_status()
    print(status)
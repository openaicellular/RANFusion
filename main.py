import os
import logging
from Config_files.config import Config
from logo import create_logo
from database.database_manager import DatabaseManager
from network.initialize_network import initialize_network
from traffic.traffic_generator import TrafficController
from network.ue_manager import UEManager
from network.gNodeB_manager import gNodeBManager
import time
import threading

def monitor_ue_updates():
    log_file_path = 'ue_updates.log'
    # Ensure the file exists, create if it doesn't
    open(log_file_path, 'a').close()
    with open(log_file_path, 'r') as file:
        # Move to the end of the file
        file.seek(0,2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                continue
            print(line.strip(), flush=True)

def log_traffic(ues):
    # Initialize the TrafficController inside the child process
    traffic_controller = TrafficController()
    
    while True:
        # Generate traffic using the traffic_controller
        for ue in ues:
            # Calculate throughput for the UE
            throughput_data = traffic_controller.calculate_throughput(ue)
            
            # Log the traffic details in the desired format, including throughput, delay, jitter, and packet loss rate
            logging.info(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Throughput: {throughput_data['throughput']:.2f}bps, Interval: {throughput_data['interval']:.2f}s, Delay: {throughput_data['jitter']}ms, Jitter: {throughput_data['packet_loss_rate']}%, Packet Loss Rate: {throughput_data['packet_loss_rate']}%")
        
        time.sleep(1)  # Logging interval

def main():

    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    logo_text = create_logo()
    print(logo_text)

    # Singleton instance of DatabaseManager is created here. This will be the same instance throughout the application.
    db_manager = DatabaseManager()
    time.sleep(1)

    # Call the new initialization function
    gNodeBs, cells, sectors, ues = initialize_network(base_dir, num_ues_to_launch=10)

    print("Network Initialization Complete")
    print(f" this is for debug and so Initialized sectors: {sectors}")  

    # Start monitoring UE operations in a separate thread
    threading.Thread(target=log_traffic, args=(ues,), daemon=True).start()

    # Keep the main program running until manually stopped
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")

if __name__ == "__main__":
    main()
# Functions for generating different types of traffic (voice, video, gaming, IoT).
# traffic_generator.py in traffic folder
import random
import time
from datetime import datetime
from logs.logger_config import traffic_update
from network.ue import UE
from database.database_manager import DatabaseManager
class TrafficController:
    def __init__(self):
        self.voice_traffic_params = {'bitrate': (8, 16)}  # in Kbps
        self.video_traffic_params = {'num_streams': (1, 5), 'stream_bitrate': (3, 8)}  # in Mbps
        self.gaming_traffic_params = {'bitrate': (30, 70)}  # in Kbps
        self.iot_traffic_params = {'packet_size': (5, 15), 'interval': (10, 60)}  # packet size in KB, interval in seconds
        self.data_traffic_params = {'bitrate': (1, 10), 'interval': (0.5, 2)}  # in Mbps

        # Initialize jitter, delay, and packet loss for each traffic type
        #for example (5, 15)  # Jitter range in milliseconds or (10, 50)  # Delay range in milliseconds or (0.01, 0.05)  # Packet loss rate range
        self.ue_voice_jitter = 0
        self.ue_voice_delay = 0
        self.ue_voice_packet_loss_rate = 0
        self.ue_video_jitter = 0
        self.ue_video_delay = 0
        self.ue_video_packet_loss_rate = 0
        self.ue_gaming_jitter = 0
        self.ue_gaming_delay = 0
        self.ue_gaming_packet_loss_rate = 0
        self.ue_iot_jitter = 0
        self.ue_iot_delay = 0
        self.ue_iot_packet_loss_rate = 0
        self.ue_data_jitter = 0
        self.ue_data_delay = 0
        self.ue_data_packet_loss_rate = 0.1

    def generate_traffic(self, ue):
        # Determine the type of traffic to generate based on the UE's service type
        if ue.ServiceType.lower() == 'voice':
            return self.generate_voice_traffic()
        elif ue.ServiceType.lower() == 'video':
            return self.generate_video_traffic()
        elif ue.ServiceType.lower() == 'game':
            return self.generate_gaming_traffic()
        elif ue.ServiceType.lower() == 'iot':
            return self.generate_iot_traffic()
        elif ue.ServiceType.lower() == 'data':
            return self.generate_data_traffic()
        else:
            raise ValueError(f"Unknown service type: {ue.ServiceType}")  
    
##############################################################################################################################
    # Traffic generation methods with conditional application of jitter, delay, and packet loss
    def generate_voice_traffic(self):
        # Record the start timestamp
        start_time = datetime.now()
        time.sleep(self.ue_voice_delay)  # Use voice-specific delay
        jitter = random.uniform(0, self.ue_voice_jitter) if self.ue_voice_jitter > 0 else 0
        bitrate = random.uniform(*self.voice_traffic_params['bitrate'])  # in Kbps
        interval = 0.02  # Interval duration in seconds
        # Convert to KB, then to bytes, and ensure it's an integer
        data_size = int((bitrate * interval) / 8 * 1024)  
        # Apply jitter
        time.sleep(jitter)
        # Simulate packet loss
        packet_loss_occurred = random.random() < self.ue_voice_packet_loss_rate
        if packet_loss_occurred:
            data_size = 0  # Packet is lost
        # Record the end timestamp
        end_time = datetime.now()
        traffic_data = {
            'data_size': data_size,  # Now in bytes and ensured to be an integer
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'ue_delay': self.ue_voice_delay,
            'ue_jitter': jitter,
            'ue_packet_loss_rate': self.ue_voice_packet_loss_rate
        }
        return traffic_data
###################################################################################################################
    def generate_video_traffic(self):
        # Record the start timestamp
        start_time = datetime.now()
        time.sleep(self.ue_video_delay)  # Use video-specific delay
        jitter = random.uniform(0, self.ue_video_jitter) if self.ue_video_jitter > 0 else 0
        time.sleep(jitter)  # Apply jitter
        num_streams = random.randint(*self.video_traffic_params['num_streams'])
        data_size = 0  # Initialize data_size as 0 bytes
        interval = 1  # Interval duration in seconds
        for _ in range(num_streams):
            stream_bitrate = random.uniform(*self.video_traffic_params['stream_bitrate'])  # in Mbps
            if random.random() < self.ue_video_packet_loss_rate:
                continue  # Skip this stream due to packet loss
            # Convert to MB, then to bytes, and accumulate
            data_size += int((stream_bitrate * interval) / 8 * 1024 * 1024)  
        # Record the end timestamp
        end_time = datetime.now()
        traffic_data = {
            'data_size': data_size,  # Now in bytes and ensured to be an integer
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'num_streams': num_streams,
            'interval': interval,
            'ue_delay': self.ue_video_delay,
            'ue_jitter': jitter,
            'ue_packet_loss_rate': self.ue_video_packet_loss_rate
        }
        return traffic_data
###################################################################################################################
    def generate_gaming_traffic(self):
        try:
            # Record the start timestamp
            start_time = datetime.now()
            # Use gaming-specific delay
            time.sleep(self.ue_gaming_delay)              
            jitter = random.uniform(0, self.ue_gaming_jitter) if self.ue_gaming_jitter > 0 else 0
            bitrate = random.uniform(*self.gaming_traffic_params['bitrate'])  # in Kbps
            interval = 0.1  # Interval duration in seconds
            # Convert to KB, then to bytes, and ensure it's an integer
            data_size = int((bitrate * interval) / 8 * 1024)  
            # Apply jitter
            time.sleep(jitter)
            # Simulate packet loss
            packet_loss_occurred = random.random() < self.ue_gaming_packet_loss_rate
            if packet_loss_occurred:
                data_size = 0  # Packet is lost
            # Record the end timestamp
            end_time = datetime.now()
            traffic_data = {
                'data_size': data_size,  # Now in bytes and ensured to be an integer
                'start_timestamp': start_time,
                'end_timestamp': end_time,
                'interval': interval,
                'ue_delay': self.ue_gaming_delay,
                'ue_jitter': jitter,
                'ue_packet_loss_rate': self.ue_gaming_packet_loss_rate
            }
            return traffic_data
        except Exception as e:
            traffic_update.error(f"Failed to generate gaming traffic: {e}")
            # Handle the exception by returning a default data structure
            return {
                'data_size': 0,  # Ensure this is consistent even in error handling
                'start_timestamp': datetime.now(),
                'end_timestamp': datetime.now(),
                'interval': 0.1,
                'delay': self.ue_gaming_delay,
                'jitter': 0,
                'packet_loss_rate': self.ue_gaming_packet_loss_rate
            }
#####################################################################################
    def generate_iot_traffic(self):
        # Record the start timestamp
        start_time = datetime.now()
        time.sleep(self.ue_iot_delay)  # Use IoT-specific delay
        jitter = random.uniform(0, self.ue_iot_jitter) if self.ue_iot_jitter > 0 else 0
        packet_size = random.randint(*self.iot_traffic_params['packet_size'])  # in KB
        interval = random.uniform(*self.iot_traffic_params['interval'])  # in seconds
        # Convert packet_size from KB to bytes, and ensure it's an integer
        data_size = int(packet_size * 1024)  
        # Apply jitter
        time.sleep(jitter)
        # Simulate packet loss
        if random.random() < self.ue_iot_packet_loss_rate:
            data_size = 0  # Packet is lost
        # Record the end timestamp
        end_time = datetime.now()
        traffic_data = {
            'data_size': data_size,  # Now in bytes and ensured to be an integer
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'ue_delay': self.ue_iot_delay,
            'ue_jitter': jitter,
            'ue_packet_loss_rate': self.ue_iot_packet_loss_rate
        }
        return traffic_data
###########################################################################################
    def generate_data_traffic(self):
        # Record the start timestamp
        start_time = datetime.now()
        time.sleep(self.ue_data_delay)  # Use data-specific delay
    
        # Ensure jitter is calculated and set in the dictionary
        jitter = random.uniform(0, self.ue_data_jitter) if self.ue_data_jitter > 0 else 0
    
        bitrate = random.uniform(*self.data_traffic_params['bitrate'])  # in Mbps
        interval = random.uniform(*self.data_traffic_params['interval'])  # in seconds
    
        # Convert bitrate from Mbps to bytes, then calculate data_size for the interval, and ensure it's an integer
        data_size = int((bitrate * interval) / 8 * 1024 * 1024)
    
        # Apply jitter
        time.sleep(jitter)
    
        # Simulate packet loss
        if random.random() < self.ue_data_packet_loss_rate:
            data_size = 0  # Packet is lost
    
        # Record the end timestamp
        end_time = datetime.now()
    
        traffic_data = {
            'data_size': data_size,  # Now in bytes and ensured to be an integer
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'ue_delay': self.ue_data_delay,
            'ue_jitter': jitter,  # Ensure this is included
            'ue_packet_loss_rate': self.ue_data_packet_loss_rate
        }
    
        return traffic_data
############################################################################################
    def calculate_throughput(self, ue):
        # Parameter validation
        if not isinstance(ue, UE):
            raise TypeError("Invalid UE object")

        # Generate traffic and retrieve traffic parameters for the UE
        traffic_data = self.generate_traffic(ue)

        # Assertions to fail fast if assumptions are violated
        assert isinstance(traffic_data['data_size'], int), "Invalid data type for data_size"
        assert traffic_data['interval'] >= 0, "Negative interval is not allowed"

        # Retrieve jitter, packet loss, and delay from the traffic data
        jitter = traffic_data['ue_jitter']  # Adjusted to use 'ue_jitter'
        packet_loss_rate = traffic_data['ue_packet_loss_rate']  # Adjusted to use 'ue_packet_loss_rate'
        interval = traffic_data['interval']
        ue_delay = traffic_data['ue_delay']

        # data_size is expected to be in bytes (as an integer)
        data_size_bytes = traffic_data['data_size']
        data_size_bits = data_size_bytes * 8  # Convert bytes to bits

        # Calculate throughput
        throughput = data_size_bits / interval if interval > 0 else 0
        # Update the UE's throughput attribute with the calculated value
        ue.throughput = throughput
        
        # Prepare the data for InfluxDB with units for clarity
        influxdb_data = {
            "measurement": "ue_throughput",
            "tags": {
                "ue_id": ue.ID
            },
            "fields": {
                "throughput": f"{throughput} bps",  # Adding units
                "jitter": jitter,
                "packet_loss": packet_loss_rate,
                "ue_delay": ue_delay,
            },
            "time": datetime.utcnow().isoformat()
        }

        # Assuming DatabaseManager and other necessary imports are correctly handled
        database_manager = DatabaseManager()
        database_manager.insert_data(influxdb_data)
        database_manager.close_connection()

        # Return the raw numeric value of throughput along with other metrics
        return {
            'throughput': throughput,
            'jitter': jitter,
            'packet_loss_rate': packet_loss_rate,
            "ue_delay": ue_delay,
            'interval': interval
        }
############################################################################################

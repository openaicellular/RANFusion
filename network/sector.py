#this is sectory.py which is located in network directory
#You can extend this class with additional methods to handle sector-specific logic, such as calculating signal strength, managing handovers, or adjusting parameters for load balancing. Remember to test this class thoroughly to ensure it integrates well with the rest of your codebase.
global all_sectors 
all_sectors = {}
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
import time
import uuid
import threading
from logs.logger_config import sector_logger
from database.database_manager import DatabaseManager

sector_lock = threading.Lock()

# Assume a global list or set for UE IDs is defined at the top level of your module
global_ue_ids = set()


#print("Print all_sectors at Top of sector.py")
#print(all_sectors)
#print("Print all sectors id")
#print(id(all_sectors))

class Sector:
    def __init__(self, sector_id, cell_id, cell, capacity, azimuth_angle, beamwidth, frequency, duplex_mode, tx_power, bandwidth, mimo_layers, beamforming, ho_margin, load_balancing, max_throughput, connected_ues=None, current_load=0):
        self.sector_id = sector_id  # String, kept as is for identifiers
        self.instance_id = str(uuid.uuid4())  # Generic unique identifier for the instance of the sector
        self.cell_id = cell_id  # String, kept as is for identifiers
        self.cell = cell  # Cell object, no change needed
        self.ues = {}  # Add a dictionary to track UEs mapped to their IDs
        # Numeric fields optimized based on usage
        self.capacity = int(capacity)  # Integer, as capacity is a count
        self.remaining_capacity = int(capacity)  # Initialize remaining_capacity with the total capacity
        self.azimuth_angle = int(azimuth_angle)  # Integer, as angles can be represented without decimal precision
        self.beamwidth = int(beamwidth)  # Integer, as beamwidth can be represented without decimal precision
        self.frequency = float(frequency)  # Float, as frequency may require decimal precision
        self.tx_power = int(tx_power)  # Integer, assuming power levels can be integers
        self.bandwidth = int(bandwidth)  # Integer, assuming bandwidth can be represented without decimal precision
        self.mimo_layers = int(mimo_layers)  # Integer, as layer count is a whole number
        self.beamforming = bool(beamforming)  # Boolean, kept as is
        self.ho_margin = int(ho_margin)  # Integer, assuming handover margin can be represented without decimal precision
        self.load_balancing = int(load_balancing)  # Integer, assuming load balancing metrics can be integers
        self.duplex_mode = duplex_mode
        self.max_throughput = max_throughput  # Maximum data handling capacity in bps (value is available in sector config)
        # List of UEs and current load, no change needed
        self.connected_ues = connected_ues if connected_ues is not None else []
        self.current_load = int(current_load)  # Integer, as load is a count

    @classmethod
    def from_json(cls, data, cell):
    # Ensure the 'capacity' key exists in data, if not, set a default value or handle it appropriately
        if 'capacity' not in data:
            # Handle the missing 'capacity' key, for example by setting a default value
            data['capacity'] = 3  # Replace with an actual default value or raise an error
        else:
            data['capacity'] = int(data['capacity'])  # Ensure capacity is an integer

        # The 'cell' object is passed as an argument, so we set it directly
        data['cell'] = cell

        # The 'cell_id' is obtained from the 'cell' object
        data['cell_id'] = cell.ID

        return cls(**data)
    
    def serialize_for_influxdb(self):
        point = Point("sector_metrics") \
            .tag("sector_id", self.sector_id) \
            .tag("cell_id", self.cell_id) \
            .tag("entity_type", "sector") \
            .tag("instance_id", str(self.instance_id)) \
            .field("azimuth_angle", self.azimuth_angle) \
            .field("beamwidth", self.beamwidth) \
            .field("frequency", self.frequency) \
            .field("duplex_mode", self.duplex_mode) \
            .field("tx_power", self.tx_power) \
            .field("bandwidth", self.bandwidth) \
            .field("mimo_layers", self.mimo_layers) \
            .field("beamforming", int(self.beamforming)) \
            .field("ho_margin", self.ho_margin) \
            .field("load_balancing", self.load_balancing) \
            .field("connected_ues", len(self.connected_ues)) \
            .field("current_load", self.current_load) \
            .field("capacity", self.capacity) \
            .field("max_throughput", self.max_throughput) \
            .time(time.time_ns(), WritePrecision.NS)
        return point

    def add_ue(self, ue):
        with sector_lock:  # Use the correct lock defined at the global scope
            if len(self.connected_ues) >= self.capacity:
                sector_logger.warning(f"Sector {self.sector_id} at max capacity! Cannot add UE {ue.ID}")


            if ue.ID not in self.connected_ues:
                self.connected_ues.append(ue.ID)  # Store only the ID, not the UE object
                self.current_load += 1  # Increment the current load
                global_ue_ids.add(ue.ID)  # Add the UE ID to the global list
                self.remaining_capacity = self.capacity - len(self.connected_ues)  # Update remaining_capacity
                ue.ConnectedCellID = self.cell_id
                ue.gNodeB_ID = self.cell.gNodeB_ID
                self.ues[ue.ID] = ue
                global_ue_ids.add(ue.ID)
                point = self.serialize_for_influxdb()
                DatabaseManager().insert_data(point)
                sector_logger.info(f"UE with ID {ue.ID} has been added to the sector {self.sector_id}. Current load: {self.current_load}")

            else:
                sector_logger.warning(f"UE with ID {ue.ID} is already connected to the sector {self.sector_id}.")

    def remove_ue(self, ue_id):
        with sector_lock:
            if ue_id in self.connected_ues:
                self.connected_ues.remove(ue_id)  # Correctly remove the ID string
                self.current_load -= 1  # Decrement the current load
                global_ue_ids.discard(ue_id)  # Correctly discard the ID string
                self.remaining_capacity = self.capacity - len(self.connected_ues)  # Update remaining_capacity
                del self.ues[ue_id]  # Correctly delete the UE from the dictionary
                point = self.serialize_for_influxdb()
                DatabaseManager().insert_data(point)
                sector_logger.info(f"UE with ID {ue_id} has been removed from the sector. Current load: {self.current_load}")
            else:
                sector_logger.warning(f"UE with ID {ue_id} is not connected to the sector.")
                
    @classmethod
    def get_sector_by_id(cls, sector_id):
        db_manager = DatabaseManager()
        sector_data = db_manager.get_sector_by_id(sector_id)
        if sector_data:
            return cls.from_json(sector_data)  # Assuming a method to create a Sector instance from data
        return None
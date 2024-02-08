#Defines the gNodeB class with properties like ID, location, cells, etc. thi is located insde network directory
import os
import json
import random
import uuid
import time
from database.time_utils import get_current_time_ntp
import logging
from network.cell import Cell
from time import sleep
from logs.logger_config import cell_logger, gnodeb_logger
from datetime import datetime
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
from database.time_utils import get_current_time_ntp, server_pools
from multiprocessing import Lock
from network.sector import Sector

current_time = get_current_time_ntp()
DEFAULT_BLACKLISTED_CELLS = []
DEFAULT_MEASUREMENT_BANDWIDTH = 20

def load_gNodeB_config():
    # Correct the path to point to the 'Config_files' directory
    # This assumes that 'Config_files' is a direct subdirectory of the base directory where 'main.py' is located
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'Config_files', 'gNodeB_config.json')

    with open(file_path, 'r') as file:
        return json.load(file)

##Using the function to load the configuration
gNodeBs_config = load_gNodeB_config()

class gNodeB:
    
    def __init__(self, gnodeb_id, latitude, longitude, coverageRadius, power, frequency, bandwidth, location, region, maxUEs, cellCount, sectorCount, handoverMargin, handoverHysteresis, timeToTrigger, interFreqHandover, xnInterface, sonCapabilities, loadBalancingOffset, cellIds, sectorIds, MeasurementBandwidth=None, BlacklistedCells=None, **kwargs):
        self.ID = gnodeb_id  # str: Unique identifier for the gNodeB
        self.instance_id = str(uuid.uuid4())  # Generic unique identifier for the instance of the GNodeB
        self.Latitude = latitude  # float: Geographic latitude where the gNodeB is located
        self.Longitude = longitude  # float: Geographic longitude where the gNodeB is located
        self.CoverageRadius = coverageRadius  # int: The radius (in meters) that the gNodeB covers
        self.TransmissionPower = power  # float: Transmission power of the gNodeB in Watts
        self.Frequency = frequency  # float: Operating frequency of the gNodeB in MHz
        self.Bandwidth = bandwidth  # int: Bandwidth available at the gNodeB in MHz
        self.Location = location  # list: Physical location of the gNodeB, typically a list [latitude, longitude]
        self.Region = region if isinstance(region, str) else ','.join(region)  # str: Region where the gNodeB is deployed, can be a single string or a list of regions joined as a string
        self.MaxUEs = maxUEs  # int: Maximum number of UEs (User Equipments) that can be connected to the gNodeB or #total UEs across all its cells.
        self.HandoverMargin = handoverMargin  # float: Margin for handover to trigger in dB
        self.HandoverHysteresis = handoverHysteresis  # float: Hysteresis value for handover in dB
        self.TimeToTrigger = timeToTrigger  # int: Time to trigger the handover in milliseconds
        self.InterFreqHandover = interFreqHandover  # bool: Whether inter-frequency handover is supported (True/False)
        self.XnInterface = xnInterface  # bool: Status of Xn interface availability (True/False)
        self.SONCapabilities = sonCapabilities  # dict: SON (Self-Organizing Network) capabilities of the gNodeB
        self.MeasurementBandwidth = MeasurementBandwidth if MeasurementBandwidth is not None else DEFAULT_MEASUREMENT_BANDWIDTH  # int: Measurement bandwidth used for handover decisions in MHz
        self.BlacklistedCells = BlacklistedCells if BlacklistedCells is not None else DEFAULT_BLACKLISTED_CELLS  # list: List of cells that are blacklisted
        self.LoadBalancingOffset = loadBalancingOffset  # int: Offset used for load balancing among cells
        self.CellIds = cellIds  # list: List of cell IDs under this gNodeB
        self.CellCount = cellCount  # int: Number of cells under this gNodeB
        self.SectorCount = sectorCount  # int: Number of sectors under this gNodeB
        self.handover_success_count = 0  # int: Count of successful handovers
        self.handover_failure_count = 0  # int: Count of failed handovers
        self.SectorIds = sectorIds  # list: List of sector IDs under this gNodeB
        self.Cells = []  # list: List to hold cell objects associated with this gNodeB
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #gnodeb_logger.info(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells at '{current_time}'.")
        #debug_print(f"Debug End: gNodeB '{self.ID}' initialized with {self.CellCount} cells.")
        # Handle any additional keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)
        print(f"gNodeB '{self.ID}' has been launched with {self.CellCount} cells capacity.")
        time.sleep(1)  # Delay for 1 second

    @staticmethod
    def from_json(json_data):
        gNodeBs_dict = {}
        for item in json_data["gNodeBs"]:
            gnodeb = gNodeB(**item)  # Unpack the dictionary directly
            gNodeBs_dict[gnodeb.ID] = gnodeb
        return gNodeBs_dict
    ###############################################################################################################
    # add serialization methods to the gNodeB class to convert gNodeB instances into a format suitable for InfluxDB
    def serialize_for_influxdb(self):
        point = Point("gnodeb_metrics") \
            .tag("gnodeb_id", self.ID) \
            .tag("entity_type", "gnodeb")\
            .tag("instance_id", str(self.instance_id)) \
        # Convert the location list to a string if it's not None
        location_str = ','.join(map(str, self.Location)) if self.Location is not None else None

        # Convert the blacklisted cells list to a string if it's not None
        blacklisted_cells_str = ','.join(map(str, self.BlacklistedCells)) if self.BlacklistedCells is not None else None

        # Ensure the 'region' field is a string
        region_str = str(self.Region) if self.Region is not None else None

        # Create a dictionary of fields to include in the Point
        fields = {
            "latitude": float(self.Latitude),
            "longitude": float(self.Longitude),
            "coverage_radius": float(self.CoverageRadius),
            "transmission_power": int(self.TransmissionPower),
            "frequency": float(self.Frequency),
            "region": region_str,
            "max_ues": int(self.MaxUEs), 
            "cell_count": int(self.CellCount),
            "sector_count": int(self.SectorCount),
            "measurement_bandwidth": float(self.MeasurementBandwidth),
            "blacklisted_cells": blacklisted_cells_str,
            "handover_success_count": int(self.handover_success_count),
            "handover_failure_count": int(self.handover_failure_count),
            "location": location_str,
            "bandwidth": float(self.Bandwidth),
            "handover_margin": float(self.HandoverMargin),
            "handover_hysteresis": float(self.HandoverHysteresis),
            "time_to_trigger": int(self.TimeToTrigger),
            "inter_freq_handover": int(self.InterFreqHandover),
            "xn_interface": str(self.XnInterface),
            "son_capabilities": str(self.SONCapabilities),
            "load_balancing_offset": int(self.LoadBalancingOffset),
            "cell_ids": ','.join(map(str, self.CellIds)) if self.CellIds is not None else None,
            "sector_ids": ','.join([str(sector_id) for sector_id in self.SectorIds])
        }

        # Add fields to the Point if they are not None
        for field, value in fields.items():
            if value is not None:
                point = point.field(field, value)

        # Set the time for the Point
        point = point.time(time.time_ns(), WritePrecision.NS)

        return point
######################################################################################################
##################################################Cell and sector add Management##########################
    def add_cell_to_gNodeB(self, cell):

            try:
                #debug_print(f"Debug: Attempting to add cell {cell.ID} to gNodeB {self.ID}")
                current_cell_ids = [c.ID for c in self.Cells]
                #debug_print(f"Debug: Current cells in gNodeB {self.ID} before adding: {current_cell_ids}")
                #cell_logger.info(f"Current cells in gNodeB {self.ID} before adding: {current_cell_ids}")

                # Proactive check to prevent adding a cell with a duplicate ID
                if cell.ID in current_cell_ids:
                    print(f" Cell {cell.ID} is already added to gNodeB {self.ID}. Ignoring.")
                    cell_logger.warning(f"Cell {cell.ID} is already added to gNodeB {self.ID}. Ignoring.")
                    return

                if len(self.Cells) >= self.CellCount:
                    print(f"gNodeB {self.ID} has reached max cell capacity of {self.CellCount}. Cannot add more cells.")
                    cell_logger.error(f"gNodeB {self.ID} has reached its maximum cell capacity. Cannot add more cells.")
                    return

                # Set the parent gNodeB reference for the cell
                cell.set_gNodeB(self)

                # Add the cell to the gNodeB's list of cells
                self.Cells.append(cell)
                #print(f"Debug: Cell {cell.ID} has been added to gNodeB {self.ID}.")
                cell_logger.info(f"Cell '{cell.ID}' has been added to gNodeB '{self.ID}'.")

                # Add sectors to the cell if they are not already present
                for sector in cell.sectors:
                    if not cell.has_sector(sector):
                        self.add_sector_to_cell(sector, cell)
                        print(f"Debug: Sector {sector.ID} has been added to Cell {cell.ID}.")
                        cell_logger.info(f"Sector '{sector.ID}' has been added to Cell '{cell.ID}'.")

                # Reactive check to ensure no duplicate cells have been added
                self.verify_no_duplicate_cells()

                # Delay for 1 second as per the original requirement
                time.sleep(1)
            except Exception as e:
                print(f"Error: An exception occurred while adding cell {cell.ID} to gNodeB {self.ID}: {e}")
                cell_logger.error(f"An exception occurred while adding cell {cell.ID} to gNodeB {self.ID}: {e}")

    def verify_no_duplicate_cells(self):
        
            cell_ids = [cell.ID for cell in self.Cells]
            if len(cell_ids) != len(set(cell_ids)):
                raise ValueError("Duplicate Cell IDs detected after addition.")
###################################################################################################

###################################################################################################



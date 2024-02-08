# sector_manager.py inside the network folder
# SectorManager class can centralize the management of sectors, including their initialization, updates,
# and the handling of User Equipment (UE) associations. This approach can streamline interactions with the
# database and ensure consistent state management across the application.

from network.sector import Sector, all_sectors
from database.database_manager import DatabaseManager
from influxdb_client import Point, WritePrecision
from logs.logger_config import cell_logger, gnodeb_logger, ue_logger, sector_logger
import threading

class SectorManager:
    def __init__(self, db_manager):
        self.sectors = all_sectors  # Use the global all_sectors dictionary to track sectors
        self.db_manager = db_manager  # Instance of DatabaseManager for DB operations
        self.lock = threading.Lock()  # Lock for thread-safe operations on sectors
        self.gnodeb_sectors_map = {}  # New attribute to track gNodeB to sectors association

    def initialize_sectors(self, sectors_config, gnodeb_manager, cell_manager):
        print("Initializing sectors...")
        initialized_sectors = {}
        processed_sectors = set()

        for sector_data in sectors_config['sectors']:
            sector_id = sector_data['sector_id']
            cell_id = sector_data.get('cell_id')
            if not cell_id:
                print(f"Cell ID not provided for sector {sector_id}. Skipping.")
                continue

            cell = cell_manager.get_cell(cell_id)
            if not cell:
                print(f"Cell {cell_id} not found for sector {sector_id}. Skipping.")
                continue

            gnodeb_id = cell.gNodeB_ID
            if not gnodeb_manager.get_gNodeB(gnodeb_id):
                print(f"gNodeB {gnodeb_id} not initialized, cannot allocate sector {sector_id}.")
                continue

            sector_gnodeb_combo = (gnodeb_id, sector_id)
            if sector_gnodeb_combo in processed_sectors:
                print(f"Sector {sector_id} already processed for gNodeB {gnodeb_id}. Skipping.")
                continue

            processed_sectors.add(sector_gnodeb_combo)

            with self.lock:
                if sector_id not in self.sectors:
                    new_sector = Sector(
                        sector_id=sector_id,
                        cell_id=cell_id,
                        cell=cell,
                        capacity=sector_data['capacity'],
                        azimuth_angle=sector_data['azimuth_angle'],
                        beamwidth=sector_data['beamwidth'],
                        frequency=sector_data['frequency'],
                        duplex_mode=sector_data['duplex_mode'],
                        tx_power=sector_data['tx_power'],
                        bandwidth=sector_data['bandwidth'],
                        mimo_layers=sector_data['mimo_layers'],
                        beamforming=sector_data['beamforming'],
                        ho_margin=sector_data['ho_margin'],
                        load_balancing=sector_data['load_balancing'],
                        connected_ues=[],
                        max_throughput=sector_data['max_throughput'],
                        current_load=0
                    )
                    # Update the gNodeB to sectors mapping instead of calling gnodeb.add_sector
                    if gnodeb_id not in self.gnodeb_sectors_map:
                        self.gnodeb_sectors_map[gnodeb_id] = []
                    self.gnodeb_sectors_map[gnodeb_id].append(new_sector)

                    # Add sector to cell
                    cell.add_sector_to_cell(new_sector)

                    self.sectors[new_sector.sector_id] = new_sector
                    initialized_sectors[new_sector.sector_id] = new_sector
                    point = new_sector.serialize_for_influxdb()
                    self.db_manager.insert_data(point)
                    print(f"Sector {new_sector.sector_id} initialized and associated with gNodeB {gnodeb_id} and Cell {cell_id}.")
                else:
                    print(f"Sector {sector_id} already exists in the manager.")

        print("Sectors initialization completed.")
        return list(initialized_sectors.values()) #Return a list of Sector instances


    def remove_ue_from_sector(self, sector_id, ue_id):
        global global_ue_ids
        with self.lock:  # Use the SectorManager's lock for thread safety
            sector = self.sectors.get(sector_id)
            if sector and ue_id in sector.connected_ues:
                sector.connected_ues.remove(ue_id)  # Correctly remove the ID string
                sector.current_load -= 1  # Decrement the current load
                global_ue_ids.discard(ue_id)  # Correctly discard the ID string
                sector.remaining_capacity = sector.capacity - len(sector.connected_ues)  # Update remaining_capacity
                del sector.ues[ue_id]  # Correctly delete the UE from the dictionary
                point = sector.serialize_for_influxdb()
                self.db_manager.insert_data(point)  # Use SectorManager's db_manager to insert data
                sector_logger.info(f"UE with ID {ue_id} has been removed from the sector {sector_id}. Current load: {sector.current_load}")
            else:
                sector_logger.warning(f"UE with ID {ue_id} is not connected to the sector {sector_id}.")

    def update_sector(self, sector_id, updates):
        """
        Updates properties of a specified sector.
        :param sector_id: ID of the sector to update.
        :param updates: Dictionary containing updates (property: new_value).
        """
        with self.lock:
            sector = self.sectors.get(sector_id)
            if sector:
                for key, value in updates.items():
                    if hasattr(sector, key):
                        setattr(sector, key, value)
                        sector_logger.info(f"Sector {sector_id} property {key} updated to {value}.")
                    else:
                        sector_logger.warning(f"Sector {sector_id} has no property {key}.")
                # Serialize and update the sector in the database
                point = sector.serialize_for_influxdb()
                self.db_manager.insert_data(point)
            else:
                sector_logger.warning(f"Sector {sector_id} not found.")

    def get_sector_state(self, sector_id):
        """
        Queries the database for the current state of a sector.
    
        :param sector_id: ID of the sector to query.
        :return: Sector state or None if not found.
        """
        sector_state = self.db_manager.query_sector_state(sector_id)
        if sector_state:
            sector_logger.info(f"State retrieved for sector {sector_id}.")
        else:
            sector_logger.warning(f"Sector state not found for {sector_id}.")
        return sector_state

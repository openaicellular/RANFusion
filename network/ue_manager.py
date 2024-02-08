import os
from network.ue import UE
from network.utils import allocate_ues, create_ue
from Config_files.config import Config
from logs.logger_config import ue_logger

# Get base path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = Config(base_dir)
ue_config = config.ue_config


class UEManager:

    def __init__(self, base_dir):
        self.config = Config(base_dir)
        self.ue_config = self.config.ue_config
        self.ues = []

    def initialize_ues(self, num_ues_to_launch, cells, gNodeBs, ue_config):
        """
        Initialize UEs and allocate them to sectors.
        
        :param num_ues_to_launch: Number of UEs to initialize.
        :param cells: Dictionary of cells in the network.
        :param gNodeBs: Dictionary of gNodeBs in the network.
        :param ue_config: Configuration for UEs.
        """
        # Get list of all sectors from cells
        all_sectors = []
        for cell in cells.values():
            all_sectors.extend(cell.sectors)
        
        if not all_sectors:
            print("Error: No sectors found")
            return []  # Return an empty list instead of None

        # Use the modified allocate_ues function from utils.py
        self.ues = allocate_ues(num_ues_to_launch, all_sectors, self.ue_config)
        return self.ues  # Ensure this method always returns a list
##################################################################################
    def create_ue(self, config, **kwargs):
        # Logic to create a single UE instance
        new_ue = UE(config, **kwargs)
        self.ues[new_ue.ID] = new_ue
        return new_ue
##################################################################################
    def get_ue_by_id(self, ue_id):
        """
        Retrieve a UE instance by its ID.
        
        :param ue_id: The ID of the UE to retrieve.
        :return: The UE instance with the given ID, or None if not found.
        """
        return self.ues.get(ue_id)
##################################################################################
    def update_ue(self, ue_id, **kwargs):
        """
        Update the parameters of an existing UE.
        
        :param ue_id: The ID of the UE to update.
        :param kwargs: Parameters to update.
        :return: True if the update was successful, False otherwise.
        """
        ue = self.get_ue_by_id(ue_id)
        if ue:
            ue.update_parameters(**kwargs)
            ue_logger.info(f"UE {ue_id} updated successfully.")
            return True
        else:
            ue_logger.warning(f"UE {ue_id} not found. Update failed.")
            return False
##################################################################################
    def list_all_ues(self):
        """
        List all UEs managed by this manager.
        
        :return: A list of all UE IDs.
        """
        return list(self.ues.keys())
##################################################################################

# Example usage
if __name__ == "__main__":
    ue_manager = UEManager()
    config = {}  # Assuming a valid config dictionary is provided
    new_ue = ue_manager.create_ue(config, imei="123456789012345", location="Location1")
    if new_ue:
        print(f"New UE created with ID: {new_ue.ID}")
    updated = ue_manager.update_ue(new_ue.ID, location="NewLocation")
    if updated:
        print(f"UE {new_ue.ID} updated.")
    all_ues = ue_manager.list_all_ues()
    print(f"All UEs: {all_ues}")
    removed = ue_manager.remove_ue(new_ue.ID)
    if removed:
        print(f"UE {new_ue.ID} removed.")
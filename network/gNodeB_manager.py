import os
from network.gNodeB import gNodeB, load_gNodeB_config
from database.database_manager import DatabaseManager
from logs.logger_config import cell_logger, gnodeb_logger


class gNodeBManager:

    def __init__(self, base_dir):
        self.gNodeBs = {}
        self.db_manager = DatabaseManager() 
        self.base_dir = base_dir
        self.gNodeBs_config = load_gNodeB_config()

        # Check if gNodeBs_config contains gNodeBs data
        if 'gNodeBs' not in self.gNodeBs_config or not self.gNodeBs_config['gNodeBs']:
            gnodeb_logger.error("gNodeBs configuration is missing or empty.")
            raise ValueError("gNodeBs configuration is missing or empty.")


    def initialize_gNodeBs(self):
        """
        Initialize gNodeBs based on the loaded configuration and insert them into the database.
        """
        for gNodeB_data in self.gNodeBs_config['gNodeBs']:
            if gNodeB_data['gnodeb_id'] in self.gNodeBs:
                raise ValueError(f"Duplicate gNodeB ID {gNodeB_data['gnodeb_id']} found during initialization.")
            
            gnodeb = gNodeB(**gNodeB_data)
            self.gNodeBs[gnodeb.ID] = gnodeb
            point = gnodeb.serialize_for_influxdb()  # Serialize for InfluxDB
            self.db_manager.insert_data(point)  # Insert the Point object directly
        return self.gNodeBs
    
    def list_all_gNodeBs(self):
        """List all gNodeBs managed by this manager."""
        return list(self.gNodeBs.keys())

    def add_gNodeB(self, gNodeB_data):
        """
        Add a single gNodeB instance to the manager and the database.
        
        :param gNodeB_data: Dictionary containing the data for the gNodeB to be added.
        """
        if gNodeB_data['gnodeb_id'] in self.gNodeBs:
            raise ValueError(f"Duplicate gNodeB ID {gNodeB_data['gnodeb_id']} found.")
        
        gnodeb = gNodeB(**gNodeB_data)
        self.gNodeBs[gnodeb.ID] = gnodeb
        point = gnodeb.serialize_for_influxdb()
        self.db_manager.insert_data(point)

    def remove_gNodeB(self, gnodeb_id):
        """
        Remove a gNodeB instance from the manager and the database.
        
        :param gnodeb_id: ID of the gNodeB to be removed.
        """
        if gnodeb_id in self.gNodeBs:
            del self.gNodeBs[gnodeb_id]
            # Assuming there's a method in DBManager to remove data
            self.db_manager.remove_data(gnodeb_id)
        else:
            print(f"gNodeB ID {gnodeb_id} not found.")

    def get_gNodeB(self, gnodeb_id):
        """
        Retrieve a gNodeB instance by its ID.
        
        :param gnodeb_id: ID of the gNodeB to retrieve.
        :return: The gNodeB instance, if found; None otherwise.
        """
        return self.gNodeBs.get(gnodeb_id)

# Example usage
#if __name__ == "__main__":
    #base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #gnodeb_manager = gNodeBManager(base_dir)
    #gnodeb_manager.initialize_gNodeBs()
    # Additional operations like add_gNodeB, remove_gNodeB, get_gNodeB can be performed using the manager instance.
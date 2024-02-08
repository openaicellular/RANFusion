#cell_manager.py inside the network folder
import os
# Removed the incorrect import statement
from logs.logger_config import cell_logger
import json
from database.database_manager import DatabaseManager
from network.cell import Cell  # Assuming Cell class is correctly defined in network.cell

class CellManager:
    def __init__(self, gNodeBs, db_manager: DatabaseManager):
        self.cells = {}
        self.gNodeBs = gNodeBs
        self.db_manager = db_manager

    def initialize_cells(self, cells_config):
        """
        Initialize cells based on the provided configuration and associate them with gNodeBs.
        
        :param cells_config: Configuration data for cells.
        :return: Dictionary of initialized cells.
        """
        if self.gNodeBs is None:
            cell_logger.error("gNodeBs is None. Cannot initialize cells.")
            return None  # Ensure to return None or an appropriate value indicating failure

        cell_logger.info("Initializing cells.")
        for cell_data in cells_config['cells']:
            cell_id = cell_data['cell_id']
            gNodeB_id = cell_data['gnodeb_id']
            if gNodeB_id not in self.gNodeBs:
                cell_logger.error(f"Error: gNodeB {gNodeB_id} not found for cell {cell_id}")
                continue

            new_cell = Cell(**cell_data)

            # Add the cell to the corresponding gNodeB
            if gNodeB_id in self.gNodeBs:
                self.gNodeBs[gNodeB_id].add_cell_to_gNodeB(new_cell)

            # Add the new cell to the cells dictionary
            self.cells[cell_id] = new_cell

            # Serialize for InfluxDB and insert data
            point = new_cell.serialize_for_influxdb()
            self.db_manager.insert_data(point)

        cell_logger.info("Cells initialization completed.")
        return self.cells  # Return the dictionary of initialized cells

    def add_cell(self, cell_data):
        """
        Add a single cell instance to the manager and associate it with a gNodeB.
        
        :param cell_data: Dictionary containing the data for the cell to be added.
        """
        cell_id = cell_data['cell_id']
        gNodeB_id = cell_data['gnodeb_id']
        if cell_id in self.cells:
            cell_logger.error(f"Duplicate cell ID {cell_id} found.")
            raise ValueError(f"Duplicate cell ID {cell_id} found.")
        
        if gNodeB_id not in self.gNodeBs:
            cell_logger.error(f"gNodeB {gNodeB_id} not found.")
            raise ValueError(f"gNodeB {gNodeB_id} not found.")
        
        new_cell = Cell(**cell_data)
        self.gNodeBs[gNodeB_id].add_cell_to_gNodeB(new_cell)
        self.cells[cell_id] = new_cell
        point = new_cell.serialize_for_influxdb()
        self.db_manager.insert_data(point)

    def remove_cell(self, cell_id):
        """
        Remove a cell instance from the manager.
        
        :param cell_id: ID of the cell to be removed.
        """
        if cell_id in self.cells:
            del self.cells[cell_id]
            self.db_manager.remove_data(cell_id)  # Ensure you have this method in your DBManager
            cell_logger.info(f"Cell ID {cell_id} removed.")
        else:
            cell_logger.error(f"Cell ID {cell_id} not found.")

    def get_cell(self, cell_id):
        """
        Retrieve a cell instance by its ID.
        
        :param cell_id: ID of the cell to retrieve.
        :return: The cell instance, if found; None otherwise.
        """
        return self.cells.get(cell_id)
#NetworkLoadManager.py is located in network folder to address future needs around flexibly incorporating more advanced metrics, analytics and load balancing techniques.
#cell load calulcate
# NetworkLoadManager.py
from network.cell import Cell
from network.sector import Sector
from network.cell_manager import CellManager
from network.sector_manager import SectorManager
from logs.logger_config import cell_logger

class NetworkLoadManager:
    def __init__(self, cell_manager: CellManager, sector_manager: SectorManager):
        self.cell_manager = cell_manager
        self.sector_manager = sector_manager

    def calculate_sector_load(self, sector: Sector):
        """
        Calculate the load of a sector based on the number of connected UEs, their throughput, and its capacity.
        :param sector: An instance of the Sector class.
        :return: The load of the sector as a percentage.
        """
        if sector.capacity == 0:
            return 0

        # Calculate load based on UE count
        ue_count_load = (len(sector.connected_ues) / sector.capacity) * 100

        # Calculate load based on total UE throughput
        # Assuming each UE object in sector.connected_ues has a 'throughput' attribute
        total_throughput = sum(ue.throughput for ue in sector.ues.values())
        # Assuming sector.max_throughput represents the sector's maximum data handling capacity
        throughput_load = (total_throughput / sector.max_throughput) * 100 if hasattr(sector, 'max_throughput') and sector.max_throughput else 0

        # Combine UE count load and throughput load for final calculation
        # The method of combination (e.g., average, weighted average) can be adjusted as needed
        sector_load = (ue_count_load + throughput_load) / 2

        return sector_load

    def calculate_cell_load(self, cell: Cell):
        """
        Calculate the load of a cell based on the loads of its sectors.

        :param cell: An instance of the Cell class.
        :return: The load of the cell as a percentage.
        """
        if not cell.sectors:
            return 0
        sector_loads = [self.calculate_sector_load(sector) for sector in cell.sectors]
        return sum(sector_loads) / len(sector_loads)

    def calculate_network_load(self):
        """
        Calculate the overall network load based on the loads of all cells.

        :return: The average load of the network as a percentage.
        """
        cells = self.cell_manager.cells.values()
        if not cells:
            return 0
        cell_loads = [self.calculate_cell_load(cell) for cell in cells]
        return sum(cell_loads) / len(cell_loads)

    def log_cell_loads(self):
        """
        Log the load of each cell in the network.
        """
        for cell_id, cell in self.cell_manager.cells.items():
            cell_load = self.calculate_cell_load(cell)
            cell_logger.info(f"Cell {cell_id} Load: {cell_load:.2f}%")

# Example usage
if __name__ == "__main__":
    # Assuming cell_manager and sector_manager are already initialized and populated
    cell_manager = CellManager(gNodeBs={}, db_manager=None)  # Placeholder initialization
    sector_manager = SectorManager(db_manager=None)  # Placeholder initialization
    network_load_manager = NetworkLoadManager(cell_manager, sector_manager)

    # Calculate and log the network load
    network_load = network_load_manager.calculate_network_load()
    print(f"Network Load: {network_load:.2f}%")

    # Log the load of each cell
    network_load_manager.log_cell_loads()
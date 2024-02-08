import unittest
from network.cell_manager import CellManager
from network.gNodeB import gNodeB
from database.database_manager import DatabaseManager

class TestCellManager(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager()  # Mock or actual, depending on your setup
        self.gNodeBs = {"gNodeB1": gNodeB(gnodeb_id="gNodeB1", ...)}  # Mock gNodeB initialization
        self.cell_manager = CellManager(self.gNodeBs, self.db_manager)

    def test_add_cell(self):
        cell_data = {"cell_id": "cell1", "gnodeb_id": "gNodeB1", ...}  # Add necessary cell data
        self.cell_manager.add_cell(cell_data)
        self.assertIn("cell1", self.cell_manager.cells)
        self.assertIsNotNone(self.cell_manager.get_cell("cell1"))

if __name__ == '__main__':
    unittest.main()
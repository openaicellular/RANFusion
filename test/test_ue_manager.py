import unittest
from network.ue_manager import UEManager
from network.ue import UE

class TestUEManager(unittest.TestCase):
    def setUp(self):
        self.ue_manager = UEManager(base_dir="/path/to/base_dir")

    def test_create_ue(self):
        ue_data = {"ue_id": "ue1", ...}  # Add necessary UE data
        new_ue = self.ue_manager.create_ue(ue_data)
        self.assertIsInstance(new_ue, UE)
        self.assertIn(new_ue.ID, [ue.ID for ue in self.ue_manager.ues])

if __name__ == '__main__':
    unittest.main()
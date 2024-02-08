import unittest
from unittest.mock import MagicMock
from network.gNodeB_manager import gNodeBManager

class TestGNodeBManager(unittest.TestCase):
    def setUp(self):
        self.mock_db_manager = MagicMock()
        self.gNodeB_manager = gNodeBManager(base_dir="your_base_dir_here")
        self.gNodeB_manager.db_manager = self.mock_db_manager
        self.gNodeB_manager.initialize_gNodeBs()

    def test_gNodeB_in_memory_and_db(self):
        test_gNodeB_id = "W1320"
        self.assertIn(test_gNodeB_id, self.gNodeB_manager.gNodeBs, "gNodeB not found in memory.")
        calls = self.mock_db_manager.insert_data.call_args_list
        found_insert_call = any(test_gNodeB_id in call.args[0].to_line_protocol() for call in calls)
        self.assertTrue(found_insert_call, f"insert_data was not called with gNodeB ID {test_gNodeB_id}.")

if __name__ == '__main__':
    unittest.main()
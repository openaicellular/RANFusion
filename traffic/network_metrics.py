#network_metrics.py
# network_metrics.py is in traffic directory
from math import radians, cos, sin, asin, sqrt
from utils.location_utils import calculate_distance_cached
import time
from database.database_manager import DatabaseManager
from datetime import datetime
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions

# Haversine formula to calculate the great-circle distance between two points
def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

# Calculate the signal strength between a UE and a gNodeB
def calculate_signal_strength(ue, gNodeB):
    # Calculate the distance between the UE and the gNodeB using the cached function
    distance_to_gNodeB = calculate_distance_cached(ue.Latitude, ue.Longitude, gNodeB.Latitude, gNodeB.Longitude)
    
    # Adjust the signal strength calculation to return a value between 0 and 100
    # The signal strength is 100 at the gNodeB and decreases linearly to 0 at the edge of the coverage radius
    signal_strength = max(0, 100 * (1 - (distance_to_gNodeB / gNodeB.CoverageRadius)))
    
    return signal_strength
#################################################################################################
################################################################################################
def find_cell_by_id(cell_id, gnodebs):
    # Iterate over all gNodeBs to find the cell with the given ID
    for gnodeb in gnodebs:
        for cell in gnodeb.Cells:
            if cell.ID == cell_id:
                return cell
    return None
################################################################################################


#This is database manager class database_manager.py located in datbase folder
import os
from influxdb_client import InfluxDBClient, WritePrecision, Point, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS
from logs.logger_config import database_logger  # Import the configured logger
from datetime import datetime
from influxdb_client import Point
import json

# Read from environment variables or use default values
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'your-default-token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'ranfusion')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'RAN_metrics')

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            # Initialize the instance (the part of __init__)
            cls._instance.client_init()
        return cls._instance

    def client_init(self):
        # This method replaces the original __init__ content
        print(f"InfluxDB token: {INFLUXDB_TOKEN}")  # Print the InfluxDB token for test
        print(f"Connecting to InfluxDB with URL: {INFLUXDB_URL}, Token: {INFLUXDB_TOKEN}, Org: {INFLUXDB_ORG}")
        self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = INFLUXDB_BUCKET
##################################################################################################################################
    def get_sector_by_id(self, sector_id):
        query = f'from(bucket: "{self.bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "sector_metrics" and r.sector_id == "{sector_id}")'
        result = self.query_api.query(query=query)
        for table in result:
            for record in table.records:
                if record.values.get('sector_id') == sector_id:
                    return record.values  # Adjust based on what you need
        return None
################################################################################################################################
    def insert_sector_state(self, sector):
        """Inserts the state of a sector into InfluxDB."""
        point = sector.serialize_for_influxdb()  # Assuming serialize_for_influxdb() prepares the data correctly
        self.insert_data(point)
##################################################################################################################################
    def get_sectors(self):
        try:
            query = f'from(bucket:"{self.bucket}") |> range(start: -30d) |> filter(fn:(r) => r._measurement == "sectors")'
            result = self.query_api.query(query=query)
            sectors = []
            for table in result:
                for record in table.records:
                    sector_data = json.loads(record.get_value())
                    sectors.append(sector_data)
            return sectors
        except Exception as e:
            print(f"Failed to retrieve sectors: {e}")
            return []
##################################################################################################################################
    def remove_ue_state(self, ue_id, sector_id):
        """
        Removes the state of a UE from InfluxDB within the last 24 hours.
        
        :param ue_id: The ID of the UE to remove.
        :param sector_id: The ID of the sector associated with the UE.
        """
        # Define the time range for deletion. Here, we use 24 hours as an example.
        start_time = "now() - 24h"
        stop_time = "now()"
        
        # Construct the delete predicate function
        predicate = f'_measurement="ue_metrics" AND ue_id="{ue_id}" AND sector_id="{sector_id}"'
        
        try:
            # Perform the deletion
            self.client.delete_api().delete(start_time, stop_time, predicate, bucket=self.bucket, org=INFLUXDB_ORG)
            database_logger.info(f"Successfully removed state for UE {ue_id} in sector {sector_id}.")
        except Exception as e:
            database_logger.error(f"Failed to remove state for UE {ue_id} in sector {sector_id}: {e}")
##################################################################################################################################
    def test_connection(self):
        """Test if the connection to the database is successful."""
        try:
            self.client.ping()
            database_logger.info("Database connection successful.")
            return True
        except Exception as e:
            database_logger.error(f"Database connection test failed: {e}")
            return False
##################################################################################################################################
    def insert_data_batch(self, points):
        """Inserts a batch of Point objects into InfluxDB."""
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            #database_logger.info("Batch data inserted into InfluxDB")
        except Exception as e:
            database_logger.error(f"Failed to insert batch data into InfluxDB: {e}")
##################################################################################################################################
    def insert_data(self, measurement_or_point, tags=None, fields=None, timestamp=None):
        """Inserts data into InfluxDB. Can handle both Point objects and separate parameters."""
        try:
            if isinstance(measurement_or_point, Point):
                # If a Point object is provided
                point = measurement_or_point
                if timestamp:
                    point.time(timestamp)
            else:
                # If separate parameters are provided
                measurement = measurement_or_point
                point = Point(measurement)
                for tag_key, tag_value in (tags or {}).items():
                    point.tag(tag_key, tag_value)
                for field_key, field_value in (fields or {}).items():
                    point.field(field_key, field_value)
                # Convert the timestamp to the correct format for InfluxDB
                point.time(timestamp, WritePrecision.NS)

            self.write_api.write(bucket=self.bucket, record=point)
            # Log the measurement and the tags for context
            tags_description = ", ".join([f"{k}={v}" for k, v in point._tags.items()])
            #database_logger.info(f"Data inserted for measurement {point._name} with tags {tags_description}")

        except Exception as e:
            database_logger.error(f"Failed to insert data into InfluxDB: {e}")
##################################################################################################################################
    def close_connection(self):
        """Closes the database connection."""
        self.client.close()
##################################################################################################################################
    def get_all_ue_ids(self):
        """Retrieves all UE IDs from InfluxDB."""
        try:
            query = f'from(bucket: "{self.bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "ue_metrics")'
            result = self.query_api.query(query=query, org=INFLUXDB_ORG)
            ue_ids = []
            for table in result:
                for record in table.records:
                    if 'ue_id' in record.values:
                        ue_ids.append(record.values['ue_id'])
        except Exception as e:
            database_logger.error(f"Failed to retrieve UE IDs from InfluxDB: {e}")
            return []  # Return an empty list in case of any exception
        return ue_ids
##################################################################################################################################
    def insert_log(self, log_point):
        """Inserts log data into the logs bucket in InfluxDB."""
        log_bucket = 'RAN_logs'
        try:
            self.write_api.write(bucket=log_bucket, record=log_point)
            database_logger.info(f"Log data inserted into bucket {log_bucket}")
        except Exception as e:
            database_logger.error(f"Failed to insert log data into InfluxDB: {e}")
##################################################################################################################################
    def update_ue_association(self, ue_id, new_cell_id):
        """
        Updates the association of a UE with a new cell in the database by writing a new point.
        :param ue_id: The ID of the UE to update.
        :param new_cell_id: The ID of the new cell to associate the UE with.
        """
        try:
            # Create a new Point with the measurement name you're using for UEs
            point = Point("ue_metrics")\
                .tag("ue_id", str(ue_id))\
                .tag("connected_cell_id", str(new_cell_id)) \
                .field("update_type", "cell_association_change")\
                .time(datetime.utcnow())
            # Write the point to InfluxDB
            self.write_api.write(bucket=self.bucket, record=point)
            database_logger.info(f"UE {ue_id} association updated to cell {new_cell_id}")
        except Exception as e:
            database_logger.error(f"Failed to update UE association in the database: {e}")
            raise
##################################################################################################################################
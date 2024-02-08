from influxdb_client import InfluxDBClient
import os
# Replace these variables with your actual configuration
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'your-default-token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'ranfusion')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'RAN_metrics')

def validate_access():
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    try:
        health = client.health()
        print(f"InfluxDB Health: {health.status}")
    except Exception as e:
        print(f"Failed to access InfluxDB: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    validate_access()
# This is API.py which is located in API Gateway folder to have control over all nodes
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
from network.ue import UE 
from network.sector import Sector
from flask import Flask, request, jsonify
from threading import Lock
import traceback
import threading
import json
from network.sector_manager import all_sectors
from database.database_manager import DatabaseManager
from flask import Response
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
lock = Lock()

db_manager = DatabaseManager()
all_sectors = {}

sectors_from_db = db_manager.get_sectors()
print(sectors_from_db)
for sector_data in sectors_from_db:
    sector = Sector.from_db(sector_data)  # Assuming a method to create a Sector object from db data
    all_sectors[sector.id] = sector
    
print(all_sectors)
print(f"Length of all_sectors in API: {len(all_sectors)}")

# Function to log UE updates
def log_ue_update(message):
    with open('ue_updates.log', 'a') as log_file:
        log_file.write(message + "\n")
#########################################################################################################
def collect_metrics():
    metrics = []
    # Metric: Total number of UEs
    total_ue_count = len(UE.ue_instances)
    metrics.append(f"total_ue_count value={total_ue_count}")

    # Metric: Load per sector
    for sector_id, sector in all_sectors.items():
        metrics.append(f"sector_load,sector_id={sector_id} value={sector.current_load}")
        metrics.append(f"sector_capacity,sector_id={sector_id} value={sector.capacity}")
        metrics.append(f"sector_remaining_capacity,sector_id={sector_id} value={sector.remaining_capacity}")

    # Convert list of metrics to a single string, separated by newlines
    return '\n'.join(metrics)

#########################################################################################################
@app.route('/metrics', methods=['GET'])
def metrics():
    metrics_data = collect_metrics()
    return Response(metrics_data, mimetype='text/plain')

#########################################################################################################
@app.route('/add_ue', methods=['POST'])
def add_ue():
    data = request.json
    print("Received data:", data)  # Log received data

    # Validate required fields are present
    required_fields = ['ue_id', 'service_type', 'sector_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        print(f"Missing required fields: {', '.join(missing_fields)}")  # Log missing fields
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    ue_id = data['ue_id']
    service_type = data['service_type']
    sector_id = data['sector_id']

    # Validate sector_id format (example validation, adjust as needed)
    if not isinstance(sector_id, str) or len(sector_id) < 5:  # Example validation condition
        print(f"Invalid sector_id format: {sector_id}")
        return jsonify({'error': 'Invalid sector_id format'}), 400

    # Extract ue_config from the request data, excluding known fields
    ue_config = {key: value for key, value in data.items() if key not in ['ue_id', 'service_type', 'sector_id']}
    print(f"Processing UE with ID: {ue_id} for sector: {sector_id}")  # Log UE ID and sector ID

    # Attempt to retrieve the sector and add UE
    try:
        # Use the Singleton instance of DatabaseManager for database operations
        db_manager = DatabaseManager()
        # Assuming DatabaseManager has methods like get_sector_by_id and add_ue_to_sector
        sector = db_manager.get_sector_by_id(sector_id)
        if not sector:
            print(f"Sector with ID: {sector_id} not found")  # Log sector not found
            return jsonify({'error': 'Sector not found'}), 404

        success = db_manager.add_ue_to_sector(ue_id, sector_id, ue_config)
        if success:
            print(f"UE {ue_id} added successfully to sector {sector_id}")  # Log success
            return jsonify({'message': f'UE {ue_id} added successfully to sector {sector_id}'}), 200
        else:
            print(f"Failed to add UE {ue_id} to sector {sector_id}")  # Log failure to add UE
            return jsonify({'error': 'Failed to add UE to sector'}), 500
    except Exception as e:
        print(f"Error adding UE to sector: {e}")  # Log exception when adding UE to sector
        return jsonify({'error': 'An error occurred while adding UE to sector'}), 500

#########################################################################################################
@app.route('/remove_ue', methods=['POST'])
def remove_ue():
    data = request.json
    print("Received request to remove UE:", data)
    
    required_fields = ['ue_id', 'sector_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    ue_id = data['ue_id']
    sector_id = data['sector_id']
    
    # Validate sector_id and ue_id formats (example validation, adjust as needed)
    if not isinstance(sector_id, str) or len(sector_id) < 5:
        return jsonify({'error': 'Invalid sector_id format'}), 400
    if not isinstance(ue_id, str) or len(ue_id) < 3:
        return jsonify({'error': 'Invalid ue_id format'}), 400
    
    db_manager = DatabaseManager()  # Instantiate your DatabaseManager Singleton
    
    try:
        # Ensure thread safety
        with lock:
            # Attempt to retrieve the sector and remove the UE
            # Note: You need to adjust this part according to how sectors are managed in your application
            # This example assumes there's a method to get a sector and remove a UE from it
            print(f"Attempting to find sector with ID: {sector_id} and remove UE: {ue_id}")
            
            # Assuming Sector class has a method remove_ue that returns True if removal was successful
            # And assuming there's a way to get a sector object. Adjust this logic as per your application's design
            # success = sector.remove_ue(ue_id)
            
            # For demonstration, let's assume the removal was successful and focus on removing UE state from DB
            success = True  # Placeholder for actual sector and UE removal logic
            
            if success:
                # Additionally, remove the UE's state from InfluxDB
                db_manager.remove_ue_state(ue_id, sector_id)  # Ensure this method is implemented in DatabaseManager
                # log_ue_update(f"UE ID: {ue_id} removed from Sector ID: {sector_id}")  # Adjust logging as needed
                return jsonify({'message': f'UE {ue_id} removed successfully from sector {sector_id}'}), 200
            else:
                return jsonify({'error': 'Failed to remove UE from sector'}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while removing UE'}), 500
#########################################################################################################
if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/update_ue', methods=['POST'])
def update_ue():
    data = request.json
    # Validate that ue_id is provided
    if 'ue_id' not in data:
        return jsonify({'error': 'Missing ue_id in request'}), 400

    ue_id = data['ue_id']

    # Validate that there are parameters to update
    if len(data) <= 1:  # Only ue_id is present, no parameters to update
        return jsonify({'error': 'No parameters provided for update'}), 400

    try:
        ue = UE.get_ue_instance_by_id(ue_id)
        if not ue:
            return jsonify({'error': 'UE not found'}), 404

        # Remove 'ue_id' from the data as it's not a parameter to be updated
        data.pop('ue_id', None)

        # Update UE parameters
        ue.update_parameters(**data)

        return jsonify({'message': f'UE {ue_id} updated successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while updating UE'}), 500
#########################################################################################################
if __name__ == '__main__':
    print("Starting API server...")
    print(f"Available sectors at API start: {list(all_sectors.keys())}")
    app.run(debug=True)
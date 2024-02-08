# control_app.py in root directory
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from traffic.traffic_generator import TrafficController
from logs.logger_config import setup_logger
from logs.logger_config import traffic_update,server_logger 
from multiprocessing import Queue
import traceback
from datetime import datetime
from network.ue import UE
from threading import Lock

# Global flag to indicate if an update has been received
update_received = False

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # This line allows all domains
lock = Lock()

# Assuming command_queue is made accessible here, for example, as a global variable
command_queue = Queue()

# Ensure TrafficController instance is accessible here, possibly as a global or through an application context
global traffic_controller
traffic_controller = TrafficController(command_queue)

def validate_traffic_parameters(params, param_types):
    missing_params = [param for param, param_type in param_types.items() if param not in params or not isinstance(params[param], param_type)]
    if missing_params:
        return False, f"Missing or invalid parameters: {', '.join(missing_params)}"
    return True, ""

@app.route('/', methods=['GET'])
def index():
    return 'Welcome to the 5G RAN Simulator!', 200

@app.route('/update_voice_traffic', methods=['POST'])
def update_voice_traffic():
    global update_received
    data = request.json
    expected_types = {
        'bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        return {'error': message}, 400

    try:
        success = traffic_controller.update_voice_traffic(data['bitrate_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'voice',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"Voice traffic update command sent: {command}")
            return {'message': 'Voice traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update voice traffic: {e}')
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/update_video_traffic', methods=['POST'])
def update_video_traffic():
    global update_received
    data = request.json
    expected_types = {
        'num_streams_range': list,
        'stream_bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        return {'error': message}, 400

    try:
        success = traffic_controller.update_video_traffic(data['num_streams_range'], data['stream_bitrate_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'video',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"Video traffic update command sent: {command}")
            return {'message': 'Video traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update video traffic: {e}')
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/update_gaming_traffic', methods=['POST'])
def update_gaming_traffic():
    app.logger.info('Processing request for /update_gaming_traffic')
    data = request.json
    print("Received data:", data)

    expected_types = {
        'bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        print("Validation failed:", message) 
        return {'error': message}, 400

    try:
        success = traffic_controller.update_gaming_traffic(data['bitrate_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'gaming',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"Gaming traffic update command sent: {command}")
            return {'message': 'Gaming traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update gaming traffic: {e}')
        print("Exception:", e)
        print(traceback.format_exc())
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/update_iot_traffic', methods=['POST'])
def update_iot_traffic():
    data = request.json
    expected_types = {
        'packet_size_range': list,
        'interval_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        return {'error': message}, 400

    try:
        success = traffic_controller.update_iot_traffic(data['packet_size_range'], data['interval_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'iot',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"IoT traffic update command sent: {command}")
            return {'message': 'IoT traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update IoT traffic: {e}')
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/update_data_traffic', methods=['POST'])
def update_data_traffic():
    data = request.json
    expected_types = {
        'bitrate_range': list,
        'interval_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        return {'error': message}, 400

    try:
        success = traffic_controller.update_data_traffic(data['bitrate_range'], data['interval_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'data',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"Data traffic update command sent: {command}")
            return {'message': 'Data traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update data traffic: {e}')
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'CORS Test successful'}), 200    
##############################################################################################################
@app.route('/add_ue', methods=['POST'])
def add_ue():
    data = request.json
    try:
        ue_data = {'ues': [data]}
        ue = UE.from_json(ue_data)[0]
        with lock:  # Ensure thread safety
            success = .add_ue(ue)
        if success:
            server_logger.info(f'UE {ue.ue_id} added successfully')
            return jsonify({'message': 'UE added successfully'}), 200
        else:
            server_logger.error(f'Failed to add UE: {data}')
            return jsonify({'error': 'Failed to add UE'}), 409
    except Exception as e:
        server_logger.exception('Failed to add UE')
        return jsonify({'error': str(e)}), 500
##############################################################################################################
@app.route('/remove_ue/<ue_id>', methods=['DELETE'])
def remove_ue(ue_id):
    try:
        with lock:  # Ensure thread safety
            success = .remove_ue(ue_id)
        if success:
            server_logger.info(f'UE {ue_id} removed successfully')
            return jsonify({'message': 'UE removed successfully'}), 200
        else:
            server_logger.error(f'Failed to remove UE: {ue_id}')
            return jsonify({'error': 'Failed to remove UE'}), 500
    except Exception as e:
        server_logger.exception('Failed to remove UE')
        return jsonify({'error': str(e)}), 500
##############################################################################################################
@app.route('/update_ue/<ue_id>', methods=['PATCH'])
def update_ue(ue_id):
    data = request.json
    try:
        with lock:  # Ensure thread safety
            success = .update_ue(ue_id, data)
        if success:
            server_logger.info(f'UE {ue_id} updated successfully')
            return jsonify({'message': 'UE updated successfully'}), 200
        else:
            server_logger.error(f'Failed to update UE: {ue_id}')
            return jsonify({'error': 'Failed to update UE'}), 400  # Use 400 for client-side errors
    except Exception as e:
        server_logger.exception(f'Exception occurred while updating UE: {ue_id}')
        return jsonify({'error': str(e)}), 500
##############################################################################################################

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from Cerebellum.Wings import Wings

# Initializing a drone instance
drone = Drone()

app = Flask(__name__)
# Enabling CORS for the Flask app
CORS(app)

@app.route('/api/command', methods=['POST'])
def handle_command():
    """
    Handle POST request to the /api/command route. 
    Process the 'command' provided in the request data 
    and update the drone state accordingly.

    Returns:
    - 400 status and an error message if no data is provided,
    or if 'command' is not in the provided data, or if the command is not recognized.
    - 200 status and a success message if the command is processed successfully.
    """
    data = request.get_json()

    # If no data is provided, return an error
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    # If there's no command in the data, return an error
    if 'command' not in data:
        return jsonify({"message": "No 'command' in input data"}), 400

    command = data['command']
    print(f"[API] Received command: {command}")

    # Process the command and change the drone state accordingly
    if command == 'startDrone':
        drone.set_state(Drone.READY)
    elif command == 'riseUp':
        drone.set_state(Drone.RISING)
    elif command == 'fallDown':
        drone.set_state(Drone.FALLING)
    elif command == 'spinRight':
        drone.set_state(Drone.MOVING_RIGHT)
    elif command == 'spinLeft':
        drone.set_state(Drone.MOVING_LEFT)
    elif command == 'floating':
        drone.set_state(Drone.KEEPING)
    elif command == 'stopDrone':
        drone.set_state(Drone.SHUTTING_DOWN)
    else:
        return jsonify({"message": "Command not recognized"}), 400

    return jsonify({"message": "Command received and processed"}), 200

if __name__ == '__main__':
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)

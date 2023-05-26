from flask import Flask, request, jsonify
from flask_cors import CORS
# from Drone import Drone

# drone = Drone()

app = Flask(__name__)
CORS(app)

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No input data provided"}), 400

    if 'command' not in data:
        return jsonify({"message": "No 'command' in input data"}), 400

    command = data['command']

    # Aqui é onde você processaria o comando e enviaria para o dispositivo RC.
    # Agora estamos também atualizando o estado do drone com base no comando recebido.
    print(f"Received command: {command}")

    if command == 'throttle_up':
        print("Going UP!")
        # drone.set_state(Drone.STARTING)
    elif command == 'throttle_down':
        print("Going DOWN!")
        # drone.set_state(Drone.SHUTTING_DOWN)
    if command == 'turn_left':
        print("Wow, turning left!")
        # drone.set_state(Drone.STARTING)
    elif command == 'turn_right':
        print("Wow, turning right!")
        # drone.set_state(Drone.SHUTTING_DOWN)
    if command == 'stop_all':
        print("Stop it all!!!")
        # drone.set_state(Drone.STARTING)
    elif command == 'start':
        print("Let's start this flight!")
        # drone.set_state(Drone.SHUTTING_DOWN)
    if command == 'auth':
        print("Check this guy!!")
        # drone.set_state(Drone.STARTING)
    else:
        return jsonify({"message": "Command not recognized"}), 400

    return jsonify({"message": "Command received and processed"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


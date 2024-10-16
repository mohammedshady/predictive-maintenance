import json
import joblib
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from machine import Machine
from helpers import read_machine_data
from threading import Thread, Lock
import os

async_mode = None

app = Flask(__name__, static_folder='../client/dist', static_url_path='/')
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")
thread = None
machine_failure = False
machine_mode =  False
thread_lock = Lock()
model_path = './model/model(all)(d=4).pkl'
machine = Machine("A")


def background_thread():
    while machine_mode:
        socketio.sleep(3)
        machine.generate_machine_data()
        machine.log_data_to_csv()
        machine_status = machine.get_machine_status()
        socketio.emit('machine_status', json.dumps(machine_status))

@socketio.on('connect')
def handle_connect():
    file_path = './machine_data.csv'
    if not os.path.exists(file_path): return
    print("Client connected Sending File Data ...")
    machine_data = read_machine_data()
    socketio.emit('machine_data', json.dumps(machine_data))

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@app.route('/api/machine-mode', methods=['POST'])
def set_machine_mode():
    if machine_mode == False : return jsonify({"status": "error", "message": "Machine is turned off turn it on first"}),403
    global machine_failure
    machine_failure = not machine_failure
    if machine_failure:
        machine.set_machine_mode(mode="fail")
        return jsonify({"status": "success", "message": "Machine Simulating failure"}), 200
    else:
        machine.set_machine_mode(mode="normal")
        return jsonify({"status": "success", "message": "Machine set to Normal"}), 200
    
@app.route('/api/clear-data', methods=['POST'])
def clear_machine_data():
   file_path = './machine_data.csv'
   if machine_mode == True : return jsonify({"status": "error", "message": "Machine is turned on turn it off first"}),403
   if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({"status": "success", "message": f"File '{file_path}' deleted"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
   else:
        return jsonify({"status": "error", "message": "File not found"}), 404
    
@app.route('/api/machine-toggle', methods=['POST'])
def set_machine_toggle():
    global machine_mode 
    machine_mode = not machine_mode
    if machine_mode:
        start_background_task()  
        return jsonify({"status": "success", "message": "Machine turned on"}), 200
    else:
        stop_background_task()
        return jsonify({"status": "success", "message": "Machine turned off"}), 200


def start_background_task():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

def stop_background_task():
    global machine_mode, thread
    machine_mode = False
    if thread is not None:
        thread.join()
        thread = None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    PORT = 5000
    socketio.run(app, port=PORT)

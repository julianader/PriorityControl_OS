from flask import Flask, jsonify, request, render_template, send_from_directory
import psutil
import os

app = Flask(__name__)

# Serve CSS file from css folder
@app.route('/css/<path:filename>')
def custom_static(filename):
    return send_from_directory('css', filename)

# Function to get the list of processes
def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'nice', 'cpu_percent']):
        processes.append(proc.info)
    return processes

# Function to set priority
def set_priority(pid, priority):
    try:
        process = psutil.Process(pid)
        process.nice(priority)
        return True, f"Priority of process with PID {pid} has been changed to {priority}."
    except psutil.AccessDenied:
        return False, "Access denied. You don't have permission to modify the priority of this process."
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processes', methods=['GET'])
def processes():
    return jsonify(get_processes())

@app.route('/set_priority', methods=['POST'])
def change_priority():
    data = request.json
    pid = data['pid']
    priority = data['priority']
    success, message = set_priority(pid, priority)
    return jsonify({"success": success, "message": message})

if __name__ == '__main__':
    app.run(debug=True)

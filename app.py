import requests
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import json

app = Flask(__name__)
socketio = SocketIO(app)

class Servicio:
    def __init__(self, name, url, status, retries):
        self.name = name
        self.url = url
        self.status = status
        self.retries = retries

services = []

def check_service(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return "up"
    except requests.exceptions.RequestException:
        return "down"

def update_service_status():
    for service in services:
        service["status"] = check_service(service["url"])
        socketio.emit("service_status", json.dumps(service), namespace="/")

def background_update():
    while True:
        update_service_status()
        time.sleep(1)

@app.route("/monitor", methods=["POST"])
def update_server_info():
    data = requests.get_json()
    puerto_disponible = data["puerto"]
    url = data["ip"]+":"+puerto_disponible
    name = "service"+puerto_disponible
    status = "down"
    retries = 0
    services.append(Servicio(name, url, status, retries))
    
    socketio.emit("new_server", json.dumps({"name": name, "status": status}), namespace="/")
    return jsonify({"success": True})

# Llamamos a la función para actualizar los estados inicialmente
update_service_status()

# Creamos un thread para ejecutar la actualización en segundo plano
update_thread = threading.Thread(target=background_update, daemon=True)
update_thread.start()

@app.route('/')
def index():
    return render_template('index.html', services=services)

@socketio.on('connect', namespace="/")
def on_connect():
    print("Cliente conectado")

@socketio.on('disconnect', namespace="/")
def on_disconnect():
    print("Cliente desconectado")

if __name__ == '__main__':
    socketio.run(app, debug=True)

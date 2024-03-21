import requests
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import json

app = Flask(__name__)
socketio = SocketIO(app)

services = {
    "Service 1": {"name": "a", "url": "http://localhost:3400/status", "status": "down"},
    "Service 2": {"name": "b", "url": "http://localhost:3500/status", "status": "down"},
    "Service 3": {"name": "c", "url": "http://localhost:3600/status", "status": "down"},
}

def check_service(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return "up"
    except requests.exceptions.RequestException:
        return "down"

def update_service_status():
    for service in services.values():
        service["status"] = check_service(service["url"])
        socketio.emit("service_status", json.dumps(service), namespace="/")

def background_update():
    while True:
        update_service_status()
        time.sleep(1)

# Llamamos a la función para actualizar los estados inicialmente
update_service_status()

# Creamos un thread para ejecutar la actualización en segundo plano
update_thread = threading.Thread(target=background_update, daemon=True)
update_thread.start()

@app.route('/')
def index():
    return render_template('index.html', services=services.values())

@socketio.on('connect', namespace="/")
def on_connect():
    print("Cliente conectado")

@socketio.on('disconnect', namespace="/")
def on_disconnect():
    print("Cliente desconectado")

if __name__ == '__main__':
    socketio.run(app, debug=True)

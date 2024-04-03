import requests
from flask import request, Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import json
import subprocess
from datetime import datetime
import time

app = Flask(__name__)
socketio = SocketIO(app)

class Pila:
    def __init__(self, tamanio):
        self.items = [0] * tamanio
        self.tamanio = tamanio

    def push(self, item):
        self.items.append(item)
        if len(self.items) > self.tamanio:
            self.items.pop(0)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        else:
            raise IndexError("La pila está vacía")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def to_list(self):
        return self.items

class Servicio:
    def __init__(self, name, url, status, latency):
        self.name = name
        self.url = url
        self.status = status
        self.latency = latency

    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'status': self.status,
            'latency': self.latency.to_list()
        }

services = []

ruta_script = "./scripts.sh"

def log(accion_str):
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"{hora_actual} - {accion_str}")

def murder_container(ip, puerto):
    log("Ejecutando script de matar contendor")
    parametros = [ip, puerto]
    subprocess.run(["bash", ruta_script] + parametros)

def check_service(url):
    log("Checking service status")

    try:
        start_time = time.monotonic()  # Iniciar tiempo
        response = requests.get(url)
        response.raise_for_status()
        end_time = time.monotonic()  # Finalizar tiempo

        latency = (end_time - start_time) * 1000  # Calcular latencia en milisegundos


        log(f"Service: {url} status up. Latency: {latency:.2f}ms")
        return ["up", latency]

    except requests.exceptions.RequestException:
        log("Service: " + url + "status down")
        return "down"

def update_service_status():
    for service in services:
        url = service.url
        result = check_service(url)
        service.status = result[0]
        service.latency.push(result[1])
        socketio.emit("service_status", json.dumps(service.to_dict()), namespace="/")
        if service.status == "down":
            ip = url.split(":")[1][2:]
            port = url.split(":")[2][:4]
            murder_container(ip ,port)


def background_update():
    while True:
        update_service_status()
        time.sleep(1)

@app.route("/monitor", methods=["POST"])
def update_server_info():
    data = request.json
    puerto_disponible = data["port"]
    url = data["ip"]+":"+puerto_disponible+"/status"
    name = "service"+puerto_disponible
    log(f"trying to add server port: {puerto_disponible} ip: {url}")
    status = "down"
    latency = Pila(5)
    servicionew = Servicio(name, url, status, latency)
    services.append(servicionew)
    socketio.emit("new_server", json.dumps(servicionew.to_dict()), namespace="/")
    log(f"server ip: {url} added!")
    return jsonify({"success": True})

def init_temp(puerto, ip):
    puerto_disponible = puerto
    url = ip+":"+str(puerto_disponible)+"/status"
    name = "service"+str(puerto_disponible)
    status = "down"
    latency = Pila(5)
    print(latency.to_list())
    servicionew = Servicio(name, url, status, latency)
    services.append(servicionew)
    socketio.emit("new_server", json.dumps(servicionew.to_dict()), namespace="/")
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
    #init_temp(3400, 'http://localhost')
    #init_temp(3500, 'http://localhost')
    #init_temp(3600, 'http://localhost')
    print("Cliente conectado")

@socketio.on('disconnect', namespace="/")
def on_disconnect():
    print("Cliente desconectado")



if __name__ == '__main__':
    socketio.run(app, debug=True)

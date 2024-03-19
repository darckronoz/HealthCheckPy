from flask import Flask, render_template
import requests
import json
import time

app = Flask(__name__)

@app.route('/')
def index():
    # Realizar peticiones de health checks a los servidores
    servers = [
        {'name': 'Server1', 'url': 'http://server1/health'},
        {'name': 'Server2', 'url': 'http://server2/health'}
    ]
    statuses = {}
    for server in servers:
        try:
            response = requests.get(server['url'])
            status = response.status_code
        except requests.exceptions.RequestException:
            status = 500
        statuses[server['name']] = 'OK' if status == 200 else 'ERROR'

    # Renderizar la plantilla HTML con los datos de los servidores
    return render_template('index.html', statuses=statuses)

if __name__ == '__main__':
    app.run(debug=True)
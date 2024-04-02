#!/bin/bash

# Puerto base
puerto_base=5100

# Función para verificar si un puerto está en uso
puerto_en_uso() {
    local puerto=$1
    if lsof -Pi :$puerto -sTCP:LISTEN -t >/dev/null; then
        return 0 # El puerto está en uso
    else
        return 1 # El puerto no está en uso
    fi
}

# Encontrar el primer puerto disponible dentro del rango
puerto_disponible=$puerto_base
while puerto_en_uso $puerto_disponible; do
    puerto_disponible=$((puerto_disponible + 1))
    if [ $puerto_disponible -gt 5200 ]; then
        echo "No hay puertos disponibles en el rango especificado."
        exit 1
    fi
done


$ip_servidor = (Get-NetAdapter -InterfaceAlias "Ethernet" | Select-Object -ExpandProperty IPv4Address).IpAddress


monitor_url="http://localhost:3000/monitor"
loadBalancer_url="http://192.168.128.3:8888/loadBalancer"

# Crear y ejecutar el contenedor
docker run -d -p $puerto_disponible:3001 --name "server$puerto_disponible" lonyonserver

# Enviar la información del servidor al monitor.js
curl -X POST "$monitor_url" -H "Content-Type: application/json" -d "{ \"ip\": \"$ip_servidor\", \"puerto\": \"$puerto_disponible\" }"

# Enviar la información del servidor al loadBalancer.js
curl -X POST "$loadBalancer_url" -H "Content-Type: application/json" -d "{ \"ip\": \"$ip_servidor\", \"puerto\": \"$puerto_disponible\" }"

# Mostrar mensaje informativo
echo "Servidor creado en la IP $ip_servidor y puerto $puerto_disponible, con el nombre 'server$puerto_disponible'."
echo "Información del servidor enviada al monitor.js en $monitor_url."
echo "Información del servidor enviada al loadBalancer.js en $loadBalancer_url."

# Función para obtener el ID del contenedor a partir de la IP y el puerto
get_container_id() {
    local ip=$1
    local puerto=$2

    local container_id=$(docker ps -a | grep -E "($ip|$puerto)" | awk '{print $1}')

    if [ -z "$container_id" ]; then
        echo "No se encontró un contenedor con la IP $ip y el puerto $puerto."
        exit 1
    fi

    echo "$container_id"
}

# Función para eliminar un contenedor
delete_container() {
    local container_id=$1

    echo "Eliminando el contenedor $container_id..."
    docker rm -f $container_id

    if [ $? -eq 0 ]; then
        echo "Contenedor $container_id eliminado correctamente."
    else
        echo "Error al eliminar el contenedor $container_id."
        exit 1
    fi
}

# Obtener la IP y el puerto del contenedor
ip_contenedor=$1
puerto_contenedor=$2

# Obtener el ID del contenedor
container_id=$(get_container_id $ip_contenedor $puerto_contenedor)

# Eliminar el contenedor
delete_container $container_id

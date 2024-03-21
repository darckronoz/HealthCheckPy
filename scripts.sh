# Puerto base
$puerto_base = 5100

# Función para verificar si un puerto está en uso
function puerto_en_uso($puerto) {
  if (lsof -Pi :$puerto -sTCP:LISTEN -t) {
    return 0 # El puerto está en uso
  } else {
    return 1 # El puerto no está en uso
  }
}

# Encontrar el primer puerto disponible dentro del rango
$puerto_disponible = $puerto_base
while (puerto_en_uso $puerto_disponible) {
  $puerto_disponible++
  if ($puerto_disponible -gt 5200) {
    echo "No hay puertos disponibles en el rango especificado."
    exit 1
  }
}

# Obtener la dirección IP del host
$ip_servidor = (Get-NetAdapter -IncludeHidden).IpAddress | Where-Object {$_.AddressFamily -eq "InterNetwork"} | Select-Object -First 1 -ExpandProperty IPAddress

# URLs del monitor y load balancer
$monitor_url = "http://localhost:3000/monitor"
$loadBalancer_url = "http://localhost:3000/loadBalancer"

# Crear y ejecutar el contenedor
docker run -d -p $puerto_disponible:3001 --name "server$puerto_disponible" lonyonserver

# Enviar información del servidor al monitor.js
curl -X POST -H "Content-Type: application/json" -d "{ \"ip\": \"$ip_servidor\", \"puerto\": \"$puerto_disponible\" }" ^$monitor_url

# Enviar información del servidor al loadBalancer.js
curl -X POST -H "Content-Type: application/json" -d "{ \"ip\": \"$ip_servidor\", \"puerto\": \"$puerto_disponible\" }" ^$loadBalancer_url

# Mostrar mensaje informativo
echo "Servidor creado en la IP $ip_servidor y puerto $puerto_disponible, con el nombre 'server$puerto_disponible'."
echo "Información del servidor enviada al monitor.js en $monitor_url."
echo "Información del servidor enviada al loadBalancer.js en $loadBalancer_url."

# Función para obtener el ID del contenedor
function get_container_id($ip, $puerto) {
  $container_id = docker ps -a | findstr /i /c:"($ip|$puerto)" | select-object -First 1 | select-object -ExpandProperty ID

  if (-z $container_id) {
    echo "No se encontró un contenedor con la IP $ip y el puerto $puerto."
    exit 1
  }

  return $container_id
}

# Función para eliminar un contenedor
function delete_container($container_id) {
  echo "Eliminando el contenedor $container_id..."
  docker rm -f <span class="math-inline">container\_id
if \(</span>?) -eq 0 {
    echo "Contenedor $container_id eliminado correctamente."
  } else

import socket
import threading
import secrets
import time

kms = {"kms totales": 0}

HOST = '127.0.0.1' 
PORT = 8080

# Función para simular las actualizaciones de kilómetros
def simular_actualizacion_camionero(camionero_id):
    try:
        # Simula una actualización de kilómetros
        km_actualizados = 10000 + secrets.SystemRandom().randint(-10000, 6000)
        kms["kms totales"] += km_actualizados
        mensaje = f"{km_actualizados}"
        
        # Se conecta al servidor y envía los datos
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.sendall(mensaje.encode('utf-8'))

        print(f"Enviada actualización para camionero {camionero_id}: {km_actualizados} km")

    except Exception as e:
        print(f"Error en la conexión con el servidor: {e}")

# Iniciar múltiples clientes para simular varios camioneros
for i in [0, 1]:  # Ajusta el número según lo necesites
    for j in range (0, 3999):
        cliente_thread = threading.Thread(target=simular_actualizacion_camionero, args=(i*4+j,))
        cliente_thread.start()
    time.sleep(1)
    
print("kilómetros totales actualizados:", kms["kms totales"])

import socket
import time
import threading
import random
import os

kms = {"kms totales": 0}
# Configuración del cliente
HOST = '127.0.0.1' 
PORT = 8080
# Función para simular las actualizaciones de kilómetros
def simular_actualizacion_camionero(camionero_id):
    try:
        # Simula una actualización de kilómetros
        km_actualizados = 10000 + random.randint(-100, 100)
        kms["kms totales"] += km_actualizados
        mensaje = f"{km_actualizados}"
        
        # Se conecta al servidor y envía los datos
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.sendall(mensaje.encode('utf-8'))

        print(f"Enviada actualización para camionero {camionero_id}: {km_actualizados} km")
        print(f"Actualización de kilómetros {kms["kms totales"]} km")

        client_socket.close()
    except Exception as e:
        print(f"Error en la conexión con el servidor: {e}")

# Puedes iniciar múltiples clientes para simular varios camioneros
for i in range(1, 10000):  # Por ejemplo, para 500 camioneros
    cliente_thread = threading.Thread(target=simular_actualizacion_camionero, args=(i,))
    cliente_thread.start()

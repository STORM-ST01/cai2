import socket
import time
import threading
import random
import os

kms = {"kms totales": 0}
# Configuración del cliente
HOST = '127.0.0.1'  # Cambia esto a la dirección IP del servidor
PORT = 8080 # Cambia esto al puerto del servidor
# Función para simular las actualizaciones de kilómetros
def simular_actualizacion_camionero(camionero_id):
    while True:
        # Simula una actualización de kilómetros
        km_actualizados = 1
        kms["kms totales"] += km_actualizados
        mensaje = f"{km_actualizados}"
        
        # Se conecta al servidor y envía los datos
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.sendall(mensaje.encode('utf-8'))

        print(f"Enviada actualización para camionero {camionero_id}: {km_actualizados} km")
        print(f"Actualización de kilómetros {kms["kms totales"]} km")
        # Espera un tiempo antes de la próxima actualización
        time.sleep(random.uniform(10, 15))
        

# Puedes iniciar múltiples clientes para simular varios camioneros
for i in range(1, 501):  # Por ejemplo, para 500 camioneros
    cliente_thread = threading.Thread(target=simular_actualizacion_camionero, args=(i,))
    cliente_thread.start()

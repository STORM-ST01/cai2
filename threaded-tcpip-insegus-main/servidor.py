import socket
import threading
import os

# Configuración del servidor
HOST = '127.0.0.1'
PORT = 8080

kms = {"kms totales": 0}
# Función para manejar las conexiones de los clientes
def handle_client(client_socket, address):
    print(f"Conexión establecida desde {address}")
    
    while True:
        # Recibe los datos del cliente
        data = client_socket.recv(1024)
        
        if not data:
            break
        
        # Decodifica los datos y actualiza los kilómetros
        mensaje = data.decode('utf-8')
        try:
            km = int(mensaje)
            # Puedes realizar aquí cualquier otra comprobación necesaria
        except ValueError:
            print(f"Error: el mensaje no es un número: {mensaje}")
            break

        kms["kms totales"] += km
        print(f"Actualización de kilómetros {kms["kms totales"]} km")
        # Puedes realizar aquí cualquier otro procesamiento o almacenamiento necesario
        

    # Cierra la conexión con el cliente
    client_socket.close()

# Configuración del socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

os.system('cls')
print(f"Servidor escuchando en {HOST}:{PORT}")

# Acepta conexiones de clientes y maneja cada una en un hilo separado
while True:
    client_socket, address = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
    client_handler.start()

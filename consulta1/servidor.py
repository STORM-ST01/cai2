import socket
import threading

# Configuración del servidor
HOST = '127.0.0.1'
PORT = 8080

kms = {"kms totales": 0}

# Función para manejar las conexiones de los clientes
def handle_client(client_socket, address):
    print(f"Conexión establecida desde {address}")
    
    # Recibe los datos del cliente
    data = client_socket.recv(1024)
    
    if not data:
        print("Error: no se recibieron datos")
        return 
    
    # Decodifica los datos y actualiza los kilómetros
    mensaje = data.decode('utf-8')
    try:
        km = int(mensaje) # Verifica que el mensaje sea un número
        if km > 16000:
            print(f"Error: el mensaje excede el límite de kilómetros: {km}")
            return
        else:
            kms["kms totales"] += km
            print(f"Actualización de kilómetros {kms["kms totales"]} km")
    except ValueError:
        print(f"Error: el mensaje no es un número: {mensaje}")
        return
    finally: 
        client_socket.close()
    

# Configuración del socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Servidor escuchando en {HOST}:{PORT}")

# Acepta conexiones de clientes y maneja cada una en un hilo separado
while True:
    client_socket, address = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
    client_handler.start()






import requests

def peticion_camionero(ruta):

    url = 'http://localhost:8766/enviar_ruta'   #URL del servidor del camión para enviar la ruta
    
    response = requests.post(url, json={'ruta': ruta})  
    
    if response.status_code == 200:
        print(response.json().get('estado')+": "+ response.json().get('ruta'))
    else:
        print("Error al cambiar el destino:", response.status_code)


ruta = input("Por favor, introduce la ruta: ")
peticion_camionero(ruta)
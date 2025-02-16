import requests

def actualizacion_externa(ruta):
    
    url = 'http://localhost:8765/actualizar_bloqueos'   #URL del servidor de la empresa
                                                        #  para actualizar los bloqueos de rutas.
    response = requests.post(url, json={'ruta': ruta})
    
    if response.status_code == 200:
        print("Ruta " + response.json().get('ruta') + " añadida a los bloqueos.")
    else:
        print("Error al actualizar bloqueos en rutas:", response.status_code)

ruta = input("Por favor, introduce la ruta que ha sido cortada: ")
actualizacion_externa(ruta)

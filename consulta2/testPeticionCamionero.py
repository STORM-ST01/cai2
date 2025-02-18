import requests

def peticion_camionero(ruta_id):
    # Hacer la petición al servidor de la empresa con el número de la ruta
    url = 'http://localhost:8766/enviar_ruta'  # URL del servidor del camión

    response = requests.post(url, json={'ruta': ruta_id})  # Enviar solo el id de la ruta

    if response.status_code == 200:
        tramos_cortados = response.json().get('tramos_cortados')
        ruta_alternativa = response.json().get('ruta_alternativa')
        print(f"Tramos cortados: {tramos_cortados}")
        print(f"Tu ruta es: {ruta_alternativa}")
    else:
        print("Error al cambiar el destino:", response.status_code)

# Solicitar número de ruta al usuario (del 1 al 50)
ruta_id = int(input("Por favor, introduce un número de ruta: "))
peticion_camionero(ruta_id)


import requests

def actualizacion_externa(tramo):
    url = 'http://localhost:8765/actualizar_bloqueos'  # URL del servidor de la empresa
    response = requests.post(url, json={'tramo': tramo})

    if response.status_code == 200:
        print(f"Tramo {tramo} añadido a los bloqueos.")
    else:
        print("Error al actualizar bloqueos en tramos:", response.status_code)

# Solicitar tramo a bloquear (entre 1 y 100)
tramo = int(input("Por favor, introduce un número de tramo entre 1 y 100 para bloquear: "))
actualizacion_externa(f"TRAMO{str(tramo).zfill(3)}")

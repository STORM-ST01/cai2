from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# CONFIGURACIONES
HOST_camiones = '127.0.0.1'
PORT_camion = 8766  # Este puerto se usa también como id_camion

HOST_empresa = '127.0.0.1'
PORT_empresa = 8765

id_camion = PORT_camion  # Usamos el puerto como identificador único del camión

@app.route('/enviar_ruta', methods=['POST'])
def enviar_ruta():
    # Recibir la notificación con la clave 'ruta' (que contiene el id de la ruta actual o solicitada)
    ruta = request.json.get('ruta')
    
    # El camión consulta al servidor de la empresa para obtener la (nueva) ruta, enviando su id y la ruta
    webhook_url = f'http://{HOST_empresa}:{PORT_empresa}/verificar_ruta'
    response = requests.post(webhook_url, json={'id': id_camion, 'ruta': ruta})
    
    if response.status_code == 200:
        data = response.json()
        print(f"Tramos cortados: {data.get('tramos_cortados')}")
        print(f"Tu ruta es: {data.get('ruta_alternativa')}")
        return jsonify(data)
    else:
        return jsonify({'error': 'Error al obtener información sobre el bloqueo de tramo'}), 500

if __name__ == '__main__':
    app.run(host=HOST_camiones, port=PORT_camion)



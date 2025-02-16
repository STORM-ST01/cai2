from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

#CONFIGURACIONES
HOST_camiones = '127.0.0.1' #Host del servidor de los camiones
PORT_camion =  8766

HOST_empresa = '127.0.0.1'  #Host del servidor de la empresa
PORT_empresa = 8765         #Puerto del servidor de la empresa

id_camion = 8766    #id del camion que hacemos coincidir (para el caso practico)
                    #   con el puerto del camion (seria interesante implementarlo tambien)

@app.route('/enviar_ruta', methods=['POST'])
def enviar_ruta():  #Función que recibe la ruta del camión y verifica si la ruta esta bloqueada
                    #   mandándola a la empresa.
    
    ruta = request.json.get('ruta')

    webhook_url = 'http://'+str(HOST_empresa)+':'+str(PORT_empresa)+'/verificar_ruta' 
    
    response = requests.post(webhook_url, json={'id': id_camion, 'ruta': ruta}) #Enviar la ruta a la empresa
    
    if response.status_code == 200:
        estado = response.json().get('estado')
        nueva_ruta = response.json().get('ruta')
        print(estado+": Usar ", nueva_ruta)
        return response.json()
    else:
        return jsonify({'error': 'Error al obtener información sobre el bloqueo de carretera'}), 500
    

if __name__ == '__main__':
    app.run(host=HOST_camiones,port=PORT_camion)

from flask import Flask, request, jsonify

import requests

#CONFIGURACIONES
HOST_camiones = '127.0.0.1' #Host del servidor de los camiones

HOST_empresa = '127.0.0.1'  #Host del servidor de la empresa
PORT_empresa = 8765         #Puerto del servidor de la empresa

app = Flask(__name__)

#La forma de almacenar los datos es solo para efectos de la simulación, en un 
#   entorno real se pueden usar alternativas: base de datos, archivos, etc.

rutas_bloqueadas = ['Carretera X', 'Carretera Y', 'Carretera Z'] #Rutas bloqueadas
camiones_en_ruta = {}   #Camiones en ruta, Como clave la ruta y como valor una lista 
                        #   de ids (puertos) de los camiones en esa ruta.


@app.route('/verificar_ruta', methods=['POST'])
def calc_ruta():    #Función que verifica la ruta y si esta bloqueada, devuelve una ruta 
                    #   alternativa.
    
    id = request.json.get('id') #Puerto del camión
    ruta = request.json.get('ruta') #Ruta que el camión quiere tomar


    if ruta in rutas_bloqueadas:
        ruta_alternativa = 'Carretera A'
        info_ruta = {
            'id': id,
            'ruta': ruta_alternativa,
            'estado': 'Corte de carretera',
        }
        if ruta_alternativa in camiones_en_ruta:    #Si la ruta alternativa ya tiene camiones
            camiones_en_ruta[ruta_alternativa].append(id)
        else:
            camiones_en_ruta[ruta_alternativa] = [id]

    else:
        info_ruta = {
            'id': id, 
            'ruta': ruta,
            'estado': 'Ruta correcta',
        }   
        if ruta in camiones_en_ruta:    #Si la ruta ya tiene camiones
            camiones_en_ruta[ruta].append(id)
        else:
            camiones_en_ruta[ruta] = [id]

    return jsonify(info_ruta)   #Devuelve la información de la ruta y el estado de la carretera.


@app.route('/actualizar_bloqueos', methods=['POST'])
def actualizar_bloqueos(): #Función que actualiza las rutas bloqueadas y notifica a los camiones en esa ruta.
    
    ruta = request.json.get('ruta') 

    rutas_bloqueadas.append(ruta)

    if ruta in camiones_en_ruta: #Si hay camiones en la ruta bloqueada
        for id in camiones_en_ruta[ruta]: #Todos los camiones en esa ruta
                url = 'http://'+str(HOST_camiones)+':'+str(id)+'/enviar_ruta'
                requests.post(url, json={'ruta': ruta}) #Notificar al camion

    info_ruta = {
        'ruta': ruta,
        'estado': 'Corte de carretera',
    }   

    return jsonify(info_ruta)

if __name__ == '__main__':
    app.run(host=HOST_empresa, port=PORT_empresa)

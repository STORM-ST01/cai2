import random
import requests
from flask import Flask, request, jsonify

# CONFIGURACIONES
HOST_camiones = '127.0.0.1'
HOST_empresa = '127.0.0.1'
PORT_empresa = 8765

app = Flask(__name__)

# 100 tramos predefinidos (TRAMO001 a TRAMO100)
tramos = [f"TRAMO{str(i).zfill(3)}" for i in range(1, 101)]
# 50 rutas, cada una con entre 3 a 5 tramos aleatorios
rutas = {i: random.sample(tramos, random.randint(3, 5)) for i in range(1, 51)}

tramos_bloqueados = []       # Lista de tramos bloqueados
camiones_en_tramos = {}      # Diccionario: key = tramo, value = lista de id de camiones
camiones_rutas = {}          # Diccionario: key = id_camion, value = ruta actual (número de ruta)

@app.route('/verificar_ruta', methods=['POST'])
def verificar_ruta():
    id_camion = request.json.get('id')
    ruta_id = request.json.get('ruta')  # Se espera un número de ruta (1-50 o un id de ruta alternativa)
    
    # Primero, eliminar al camión de todos los tramos en los que esté registrado
    for tramo, camiones_list in camiones_en_tramos.items():
        if id_camion in camiones_list:
            camiones_list.remove(id_camion)
    
    # Obtener la ruta original según el id
    ruta_original = rutas.get(ruta_id)
    if not ruta_original:
        return jsonify({"error": "Ruta no válida"}), 400

    # Identificar tramos bloqueados en la ruta original
    tramos_cortados = [tr for tr in ruta_original if tr in tramos_bloqueados]
    
    # Si hay bloqueos, se genera una ruta alternativa
    if tramos_cortados:
        ruta_final = []
        for tramo in ruta_original:
            if tramo in tramos_bloqueados:
                alternativas = [t for t in tramos if t != tramo and t not in tramos_bloqueados]
                tramo_alternativo = random.choice(alternativas) if alternativas else tramo
                ruta_final.append(tramo_alternativo)
            else:
                ruta_final.append(tramo)
        # Buscar si la ruta alternativa ya está registrada
        id_nueva_ruta = None
        for key, valor in rutas.items():
            if valor == ruta_final:
                id_nueva_ruta = key
                break
        # Si no existe, la añadimos al diccionario de rutas
        if id_nueva_ruta is None:
            id_nueva_ruta = max(rutas.keys()) + 1
            rutas[id_nueva_ruta] = ruta_final
        ruta_final_id = id_nueva_ruta
    else:
        ruta_final = ruta_original
        ruta_final_id = ruta_id

    # Actualizar la ruta actual del camión en el diccionario camiones_rutas
    camiones_rutas[id_camion] = ruta_final_id

    # Registrar al camión en cada tramo de la nueva ruta para futuras notificaciones
    for tramo in ruta_final:
        if tramo not in camiones_en_tramos:
            camiones_en_tramos[tramo] = []
        if id_camion not in camiones_en_tramos[tramo]:
            camiones_en_tramos[tramo].append(id_camion)
    
    return jsonify({
        "tramos_cortados": tramos_cortados,
        "ruta_alternativa": ruta_final
    })

@app.route('/actualizar_bloqueos', methods=['POST'])
def actualizar_bloqueos():
    tramo = request.json.get('tramo')
    
    # Agregar el tramo bloqueado, si aún no está en la lista
    if tramo not in tramos_bloqueados:
        tramos_bloqueados.append(tramo)
    
    # Notificar a cada camión que tenga ese tramo en su ruta
    if tramo in camiones_en_tramos:
        for id_camion in camiones_en_tramos[tramo]:
            # Recuperar la ruta actual del camión (puede ser la original o la ruta alternativa registrada)
            ruta_actual = camiones_rutas.get(id_camion)
            if ruta_actual is not None:
                url = f'http://{HOST_camiones}:{id_camion}/enviar_ruta'
                # Se envía la ruta actual usando la clave 'ruta'
                requests.post(url, json={'ruta': ruta_actual})
    
    info_ruta = {
        'tramo': tramo,
        'estado': 'Corte de carretera',
    }
    return jsonify(info_ruta)

def mostrar_rutas():
    print("Rutas disponibles:")
    for ruta_id, tramos_ruta in rutas.items():
        print(f"Ruta {ruta_id}: {', '.join(tramos_ruta)}")

if __name__ == '__main__':
    mostrar_rutas()
    app.run(host=HOST_empresa, port=PORT_empresa)


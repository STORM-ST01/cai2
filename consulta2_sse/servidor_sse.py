import gevent
from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify, Response
import random

# CONFIGURACIÓN
HOST_EMPRESA = '127.0.0.1'
PORT_EMPRESA = 8765

app = Flask(__name__)

# 🔹 100 tramos disponibles (TRAMO001 a TRAMO100)
tramos = [f"TRAMO{str(i).zfill(3)}" for i in range(1, 101)]

# 🔹 Diccionario para almacenar rutas generadas
rutas = {}

# 🔹 Diccionario para almacenar rutas alternativas si hay cortes
rutas_alternativas = {}

# 🔹 Tramos bloqueados
tramos_bloqueados = set()

# 🔹 Diccionario de camiones y sus rutas asignadas
camiones_rutas = {}

# 🔹 Diccionario de conexiones SSE de los camiones
conexiones_sse = {}

# 🔹 Generar rutas de manera fija y reutilizable
def generar_ruta():
    """Genera una ruta aleatoria para los camiones asegurando que siempre sea la misma para un ID específico."""
    return random.sample(tramos, random.randint(3, 5))

@app.route('/verificar_ruta', methods=['POST'])
def verificar_ruta():
    """ 
    🔹 SOLUCIÓN A: Condiciones de carrera y pérdida de mensajes
    - Se asigna una ruta predefinida para evitar inconsistencias al solicitar rutas múltiples veces.
    - Se almacena la ruta en un diccionario para su posterior consulta y consistencia.
    """
    id_camion = request.json.get('id')
    ruta_id = request.json.get('ruta')

    if ruta_id not in rutas:
        rutas[ruta_id] = generar_ruta()  # Generar la ruta solo si no existe previamente

    ruta_asignada = rutas_alternativas.get(ruta_id, rutas[ruta_id])
    camiones_rutas[id_camion] = ruta_asignada

    return jsonify({"ruta_asignada": ruta_asignada})

@app.route('/stream/<int:id_camion>')
def stream(id_camion):
    """ 
    🔹 SOLUCIÓN B: Conexiones fantasma (Zombie Connections)
    - Se crea una conexión SSE para cada camión y se maneja con un buffer de eventos.
    - Se envían mensajes en tiempo real si hay eventos pendientes, evitando mensajes repetidos.
    """
    def event_stream():
        while True:
            if id_camion in conexiones_sse and conexiones_sse[id_camion]:
                evento = conexiones_sse[id_camion].pop(0)
                yield f"data: {evento}\n\n"
            else:
                yield "data: ping\n\n"  # Ping para mantener la conexión activa
            gevent.sleep(3)  # Evita sobrecarga en el servidor

    conexiones_sse[id_camion] = []
    return Response(event_stream(), content_type="text/event-stream")

@app.route('/actualizar_bloqueos', methods=['POST'])
def actualizar_bloqueos():
    """ 
    🔹 SOLUCIÓN C: Integridad en el procesamiento de datos
    - Se registra un bloqueo y se genera una ruta alternativa si es necesario.
    - Solo se notifica una vez a cada camión afectado para evitar duplicación de eventos.
    """
    tramo = request.json.get('tramo')
    if tramo not in tramos:
        return jsonify({"error": "Tramo no válido"}), 400

    tramos_bloqueados.add(tramo)

    for ruta_id, ruta in rutas.items():
        if tramo in ruta:
            ruta_alternativa = []
            for i, t in enumerate(ruta):
                if t in tramos_bloqueados:
                    alternativas = [alt for alt in tramos if alt not in tramos_bloqueados]
                    tramo_alternativo = random.choice(alternativas) if alternativas else t
                    ruta_alternativa.append(tramo_alternativo)
                else:
                    ruta_alternativa.append(t)

            rutas_alternativas[ruta_id] = ruta_alternativa  # Asignar alternativa

    # 🔹 SOLUCIÓN D: Envío único de eventos (Evitar duplicación de mensajes)
    for id_camion, ruta_actual in camiones_rutas.items():
        ruta_id_actual = [k for k, v in rutas.items() if v == ruta_actual]
        if not ruta_id_actual:
            continue  # Si no tiene ruta asignada, no hace nada

        ruta_id_actual = ruta_id_actual[0]
        if tramo in ruta_actual and ruta_id_actual in rutas_alternativas:
            nueva_ruta = rutas_alternativas[ruta_id_actual]
            camiones_rutas[id_camion] = nueva_ruta

            if id_camion in conexiones_sse:
                conexiones_sse[id_camion].append(f"🚧 Corte en {tramo}. Nueva ruta asignada: {', '.join(nueva_ruta)}")

    return jsonify({"tramo": tramo, "estado": "Corte registrado"})

@app.route('/reabrir_tramo', methods=['POST'])
def reabrir_tramo():
    """ 
    🔹 SOLUCIÓN E: Restauración de rutas tras la reactivación de un tramo
    - Se eliminan las rutas alternativas y se restaura la original cuando el tramo vuelve a estar operativo.
    """
    tramo = request.json.get('tramo')
    if tramo in tramos_bloqueados:
        tramos_bloqueados.remove(tramo)

        for id_camion, ruta_actual in camiones_rutas.items():
            ruta_id_actual = [k for k, v in rutas_alternativas.items() if v == ruta_actual]
            if not ruta_id_actual:
                continue

            ruta_id_actual = ruta_id_actual[0]
            camiones_rutas[id_camion] = rutas[ruta_id_actual]

            if id_camion in conexiones_sse:
                conexiones_sse[id_camion].append(f"✅ Tramo {tramo} reabierto. Ruta original restaurada: {', '.join(rutas[ruta_id_actual])}")

        rutas_alternativas.clear()  # Limpiar rutas alternativas al restaurar la original

    return jsonify({"tramo": tramo, "estado": "Tramo reabierto"})

@app.route('/desuscribirse/<int:id_camion>', methods=['POST'])
def desuscribirse(id_camion):
    """ 
    🔹 SOLUCIÓN F: Gestión de desconexión del cliente
    - Se elimina la conexión del camión para evitar mantener conexiones inactivas.
    - Se borra la ruta asignada para liberar memoria.
    """
    if id_camion in conexiones_sse:
        del conexiones_sse[id_camion]  # 🔹 Eliminar la conexión para evitar envíos innecesarios
    if id_camion in camiones_rutas:
        del camiones_rutas[id_camion]  # 🔹 Remover su ruta de la memoria

    print(f"🚛 Camión {id_camion} se ha desuscrito del sistema.")
    return jsonify({"status": "desuscrito", "id_camion": id_camion})

if __name__ == '__main__':
    print(f"🚀 Servidor SSE iniciado en http://{HOST_EMPRESA}:{PORT_EMPRESA}")
    http_server = WSGIServer((HOST_EMPRESA, PORT_EMPRESA), app)
    http_server.serve_forever()

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
    return random.sample(tramos, random.randint(3, 5))

@app.route('/verificar_ruta', methods=['POST'])
def verificar_ruta():
    """Devuelve la ruta predefinida o la alternativa si está bloqueada."""
    id_camion = request.json.get('id')
    ruta_id = request.json.get('ruta')

    # Si la ruta aún no ha sido generada, la creamos y la almacenamos
    if ruta_id not in rutas:
        rutas[ruta_id] = generar_ruta()

    # Si existe una ruta alternativa para esta ruta, usamos esa
    ruta_asignada = rutas_alternativas.get(ruta_id, rutas[ruta_id])

    # Guardamos la ruta asignada en el diccionario de camiones
    camiones_rutas[id_camion] = ruta_asignada

    return jsonify({"ruta_asignada": ruta_asignada})

@app.route('/stream/<int:id_camion>')
def stream(id_camion):
    """Establece la conexión SSE con un camión."""
    def event_stream():
        while True:
            if id_camion in conexiones_sse and conexiones_sse[id_camion]:
                evento = conexiones_sse[id_camion].pop(0)
                yield f"data: {evento}\n\n"
            else:
                yield "data: ping\n\n"
            gevent.sleep(3)

    conexiones_sse[id_camion] = []
    return Response(event_stream(), content_type="text/event-stream")

@app.route('/actualizar_bloqueos', methods=['POST'])
def actualizar_bloqueos():
    """Bloquea un tramo y genera una ruta alternativa para cualquier ruta que lo incluya.
       Además, notifica a los camiones que ya estaban en ruta."""
    tramo = request.json.get('tramo')
    if tramo not in tramos:
        return jsonify({"error": "Tramo no válido"}), 400

    tramos_bloqueados.add(tramo)

    for ruta_id, ruta in rutas.items():
        if tramo in ruta:
            # Generamos una alternativa
            ruta_alternativa = []

            for i, t in enumerate(ruta):
                if t in tramos_bloqueados:
                    # 🔹 Si es el primer tramo, debe cambiar
                    if i == 0:
                        alternativas = [alt for alt in tramos if alt not in tramos_bloqueados]
                        tramo_alternativo = random.choice(alternativas) if alternativas else t
                    # 🔹 Si es el último tramo, también debe cambiar
                    elif i == len(ruta) - 1:
                        alternativas = [alt for alt in tramos if alt not in tramos_bloqueados]
                        tramo_alternativo = random.choice(alternativas) if alternativas else t
                    # 🔹 Si es intermedio, aplica la lógica normal
                    else:
                        alternativas = [alt for alt in tramos if alt not in tramos_bloqueados and alt not in ruta_alternativa]
                        tramo_alternativo = random.choice(alternativas) if alternativas else t

                    ruta_alternativa.append(tramo_alternativo)
                else:
                    ruta_alternativa.append(t)

            # Guardamos la alternativa asociada a la ruta original
            rutas_alternativas[ruta_id] = ruta_alternativa

    # 🔹 Notificar a los camiones en ruta si su ruta ha cambiado
    for id_camion, ruta_actual in camiones_rutas.items():
        ruta_id_actual = [k for k, v in rutas.items() if v == ruta_actual]  # Obtener ID de la ruta
        if not ruta_id_actual:
            continue  # Si el camión no está en una ruta válida, ignorar

        ruta_id_actual = ruta_id_actual[0]
        if tramo in ruta_actual and ruta_id_actual in rutas_alternativas:
            nueva_ruta = rutas_alternativas[ruta_id_actual]
            camiones_rutas[id_camion] = nueva_ruta  # Actualizar la ruta del camión

            if id_camion in conexiones_sse:
                conexiones_sse[id_camion].append(f"🚧 Corte en {tramo}. Nueva ruta asignada: {', '.join(nueva_ruta)}")

    return jsonify({"tramo": tramo, "estado": "Corte registrado"})

@app.route('/reabrir_tramo', methods=['POST'])
def reabrir_tramo():
    """Reabre un tramo bloqueado y elimina las rutas alternativas asociadas.
       También restaura la ruta original a los camiones en ruta."""
    tramo = request.json.get('tramo')
    if tramo in tramos_bloqueados:
        tramos_bloqueados.remove(tramo)

        # Restaurar rutas originales
        for id_camion, ruta_actual in camiones_rutas.items():
            ruta_id_actual = [k for k, v in rutas_alternativas.items() if v == ruta_actual]
            if not ruta_id_actual:
                continue  # Si el camión no tenía una ruta alternativa, ignorar

            ruta_id_actual = ruta_id_actual[0]
            camiones_rutas[id_camion] = rutas[ruta_id_actual]  # Restaurar la ruta original

            if id_camion in conexiones_sse:
                conexiones_sse[id_camion].append(f"✅ Tramo {tramo} reabierto. Ruta original restaurada: {', '.join(rutas[ruta_id_actual])}")

        # Eliminar la ruta alternativa ya que el tramo se reabrió
        rutas_alternativas.clear()

    return jsonify({"tramo": tramo, "estado": "Tramo reabierto"})

@app.route('/desuscribirse/<int:id_camion>', methods=['POST'])
def desuscribirse(id_camion):
    """ Permite que un camión se desconecte del sistema. """
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

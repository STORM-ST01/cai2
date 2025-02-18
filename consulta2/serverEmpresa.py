import random
import gevent
from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify, Response

# CONFIGURACIÓN
HOST_EMPRESA = '127.0.0.1'
PORT_EMPRESA = 8765

app = Flask(__name__)

# 100 tramos predefinidos (TRAMO001 a TRAMO100)
tramos = [f"TRAMO{str(i).zfill(3)}" for i in range(1, 101)]
# 50 rutas, cada una con entre 3 a 5 tramos aleatorios
rutas = {i: random.sample(tramos, random.randint(3, 5)) for i in range(1, 51)}

tramos_bloqueados = set()  # Tramos bloqueados
camiones_rutas = {}        # Diccionario: {id_camion: [tramos de su ruta]}
rutas_originales = {}      # Diccionario: {ruta_id: copia de la ruta original antes de ser modificada}
conexiones_sse = {}        # Diccionario: {id_camion: eventos SSE pendientes}


def calcular_ruta_alternativa(ruta_original):
    """Genera una ruta alternativa evitando los tramos bloqueados."""
    ruta_alternativa = []
    for tramo in ruta_original:
        if tramo in tramos_bloqueados:
            alternativas = [t for t in tramos if t not in tramos_bloqueados and t not in ruta_alternativa]
            tramo_alternativo = random.choice(alternativas) if alternativas else None
            if tramo_alternativo:
                ruta_alternativa.append(tramo_alternativo)
            else:
                return None  # No hay ruta alternativa disponible
        else:
            ruta_alternativa.append(tramo)
    return ruta_alternativa


@app.route('/verificar_ruta', methods=['POST'])
def verificar_ruta():
    """Devuelve la ruta actualizada del camión, asegurándose de que no tenga tramos bloqueados."""
    id_camion = request.json.get('id')
    ruta_id = request.json.get('ruta')

    if ruta_id not in rutas:
        return jsonify({"error": "Ruta no válida"}), 400

    ruta_asignada = rutas[ruta_id]  # La ruta ya está corregida
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
    """Bloquea un tramo y modifica las rutas activas para evitarlo."""
    tramo = request.json.get('tramo')
    if tramo not in tramos:
        return jsonify({"error": "Tramo no válido"}), 400

    tramos_bloqueados.add(tramo)

    # 🔹 Hacemos una copia de las claves antes de iterar
    rutas_a_corregir = list(rutas.keys())

    for ruta_id in rutas_a_corregir:
        ruta = rutas[ruta_id]
        if tramo in ruta:
            # Guardamos la versión original antes de modificarla
            if ruta_id not in rutas_originales:
                rutas_originales[ruta_id] = ruta.copy()

            nueva_ruta = calcular_ruta_alternativa(ruta)
            if nueva_ruta:
                rutas[ruta_id] = nueva_ruta  # 🔹 Modificamos la ruta directamente

    # Notificar a los camiones en SSE
    for id_camion, ruta in camiones_rutas.items():
        if any(t in tramos_bloqueados for t in ruta) and id_camion in conexiones_sse:
            conexiones_sse[id_camion].append(f"🚧 Corte en {tramo}. Nueva ruta asignada: {', '.join(rutas[ruta_id])}")

    return jsonify({"tramo": tramo, "estado": "Corte registrado"})


@app.route('/reabrir_tramo', methods=['POST'])
def reabrir_tramo():
    """Reabre un tramo bloqueado y restaura las rutas originales si estaban afectadas."""
    tramo = request.json.get('tramo')
    if tramo in tramos_bloqueados:
        tramos_bloqueados.remove(tramo)

        # Restauramos las rutas originales si el tramo ya no está bloqueado
        for ruta_id in list(rutas_originales.keys()):
            rutas[ruta_id] = rutas_originales.pop(ruta_id)  # 🔹 Restauramos la ruta original

    return jsonify({"tramo": tramo, "estado": "Tramo reabierto"})


if __name__ == '__main__':
    print(f"🚀 Servidor SSE iniciado en http://{HOST_EMPRESA}:{PORT_EMPRESA}")
    http_server = WSGIServer((HOST_EMPRESA, PORT_EMPRESA), app)
    http_server.serve_forever()

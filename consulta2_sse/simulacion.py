import requests
import time

# CONFIGURACIÓN
HOST_EMPRESA = "127.0.0.1"
PORT_EMPRESA = 8765
RUTA_ID = 1  # ID de la ruta a probar
TRAMO_CORTADO = "TRAMO028"

def solicitar_ruta(id_camion):
    """Solicita una ruta para un camión."""
    response = requests.post(
        f"http://{HOST_EMPRESA}:{PORT_EMPRESA}/verificar_ruta",
        json={"id": id_camion, "ruta": RUTA_ID}
    )
    
    if response.status_code == 200:
        ruta_asignada = response.json().get("ruta_asignada")
        print(f"🚚 Camión {id_camion} recibió la ruta: {ruta_asignada}")
        return ruta_asignada
    else:
        print(f"❌ Error al solicitar ruta para camión {id_camion}: {response.json()}")
        return None

def bloquear_tramo():
    """Bloquea un tramo en la empresa."""
    print(f"⚠️ Simulando bloqueo en {TRAMO_CORTADO}...")
    response = requests.post(
        f"http://{HOST_EMPRESA}:{PORT_EMPRESA}/actualizar_bloqueos",
        json={"tramo": TRAMO_CORTADO}
    )
    
    if response.status_code == 200:
        print(f"✅ Bloqueo registrado: {response.json()}")
    else:
        print(f"❌ Error al bloquear {TRAMO_CORTADO}")

def reabrir_tramo():
    """Reabre el tramo bloqueado."""
    print(f"🔄 Reabriendo tramo {TRAMO_CORTADO}...")
    response = requests.post(
        f"http://{HOST_EMPRESA}:{PORT_EMPRESA}/reabrir_tramo",
        json={"tramo": TRAMO_CORTADO}
    )
    
    if response.status_code == 200:
        print(f"✅ Tramo reabierto: {response.json()}")
    else:
        print(f"❌ Error al reabrir {TRAMO_CORTADO}")

# 🚀 Fase 1: Solicitar ruta inicial
print("\n🔹 SOLICITANDO RUTA INICIAL...")
ruta_original = solicitar_ruta(8766)
time.sleep(2)

# 🚧 Fase 2: Bloquear TRAMO028 y verificar cambio
print("\n🔹 BLOQUEANDO TRAMO028 Y VERIFICANDO CAMBIO...")
bloquear_tramo()
time.sleep(2)
ruta_despues_bloqueo = solicitar_ruta(8766)
time.sleep(2)

# 🔄 Fase 3: Reabrir TRAMO028 y verificar restauración
print("\n🔹 REABRIENDO TRAMO028 Y VERIFICANDO RESTAURACIÓN...")
reabrir_tramo()
time.sleep(2)
ruta_final = solicitar_ruta(8766)

# 📌 Verificar si la ruta volvió a la original
if ruta_original == ruta_final:
    print("\n✅ RUTA RESTAURADA CORRECTAMENTE TRAS REAPERTURA.")
else:
    print("\n❌ ERROR: La ruta no volvió a la original después de reabrir el tramo.")

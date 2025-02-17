import requests

# CONFIGURACIÓN
HOST_EMPRESA = '127.0.0.1'
PORT_EMPRESA = 8765
TRAMO_REABIERTO = "TRAMO067"

print(f"🔄 Reabriendo tramo {TRAMO_REABIERTO}...")
response = requests.post(f'http://{HOST_EMPRESA}:{PORT_EMPRESA}/reabrir_tramo', json={'tramo': TRAMO_REABIERTO})

if response.status_code == 200:
    print(f"✅ Tramo reabierto: {response.json()}")
else:
    print("❌ Error al reabrir tramo")

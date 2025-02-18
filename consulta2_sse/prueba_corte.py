import requests

# CONFIGURACIÓN
HOST_EMPRESA = '127.0.0.1'
PORT_EMPRESA = 8765
TRAMO_BLOQUEADO = "TRAMO055"

print(f"⚠️ Simulando bloqueo en {TRAMO_BLOQUEADO}...")
response = requests.post(f'http://{HOST_EMPRESA}:{PORT_EMPRESA}/actualizar_bloqueos', json={'tramo': TRAMO_BLOQUEADO})

if response.status_code == 200:
    print(f"✅ Corte registrado: {response.json()}")
else:
    print("❌ Error al actualizar bloqueos")

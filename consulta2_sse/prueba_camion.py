import requests

# CONFIGURACIÓN
HOST_EMPRESA = '127.0.0.1'
PORT_EMPRESA = 8765
ID_CAMION = 8760
RUTA_ID = 2  # Ruta específica para este camión

print(f"🚚 Camión {ID_CAMION} enviando su ruta al servidor...")
response = requests.post(f'http://{HOST_EMPRESA}:{PORT_EMPRESA}/verificar_ruta', json={'id': ID_CAMION, 'ruta': RUTA_ID})

if response.status_code == 200:
    data = response.json()
    print(f"📍 Ruta asignada: {data.get('ruta_asignada')}")
else:
    print("❌ Error al registrar la ruta")
    exit()

print("📡 Conectando a SSE para recibir alertas en tiempo real...")
url = f'http://{HOST_EMPRESA}:{PORT_EMPRESA}/stream/{ID_CAMION}'

try:
    with requests.get(url, stream=True) as response:
        if response.status_code == 200:
            print("🛑 Esperando alertas de cortes de carretera...")
            for line in response.iter_lines():
                if line and "data:" in line.decode("utf-8"):
                    message = line.decode("utf-8").replace("data: ", "").strip()
                    if message != "ping":
                        print(f"🚧 ALARMA: {message}")
        else:
            print(f"❌ Error en la conexión SSE: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ Error en la conexión SSE: {e}")

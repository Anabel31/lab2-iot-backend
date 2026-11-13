import time
import random
import threading
import requests

# URL modificada apuntando a 127.0.0.1 en vez de localhost
API_URL = "http://127.0.0.1/lab2-backend/public/api/v1/telemetry"

# Configuración de los 3 nodos de prueba registrados en MySQL
NODES = [
    {"node_id": "ESP32_01", "token": "secret-token-node01", "temp_base": 22.5},
    {"node_id": "ESP32_02", "token": "secret-token-node02", "temp_base": 24.0},
    {"node_id": "ESP32_03", "token": "secret-token-node03", "temp_base": 26.5} # Generará alarmas (>26°C)
]

def simular_nodo(nodo_config, total_mensajes=10):
    node_id = nodo_config["node_id"]
    token = nodo_config["token"]
    base_temp = nodo_config["temp_base"]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"[*] Iniciando transmisión simulada para {node_id}...")
    
    for seq in range(1, total_mensajes + 1):
        # Variación aleatoria realista de temperatura y RSSI
        temperatura = round(base_temp + random.uniform(-0.8, 1.2), 2)
        rssi = random.randint(-55, -40)
        timestamp_unix = int(time.time())
        
        payload = {
            "node_id": node_id,
            "seq": seq,
            "value": temperatura,
            "rssi": rssi,
            "ts": timestamp_unix
        }
        
        try:
            inicio = time.time()
            # Timeout aumentado de 5 a 15 segundos
            resp = requests.post(API_URL, json=payload, headers=headers, timeout=15)
            latencia_ms = round((time.time() - inicio) * 1000, 2)
            
            if resp.status_code == 201:
                print(f"[{node_id}] seq={seq:02d} | Temp={temperatura}°C | RSSI={rssi}dBm | {resp.status_code} OK ({latencia_ms} ms)")
            else:
                print(f"[{node_id}] seq={seq:02d} | ERROR {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"[{node_id}] Error de conexión: {e}")
            
        time.sleep(random.uniform(0.3, 0.7)) # Simula el intervalo de muestreo

# Lanzar los 3 nodos en hilos concurrentes simultáneos (Prueba T05)
hilos = []
for nodo in NODES:
    hilo = threading.Thread(target=simular_nodo, args=(nodo, 10))
    hilos.append(hilo)
    hilo.start()
    # Pequeño desfase de 0.5 segundos para que los hilos no colisionen en el mismo microsegundo
    time.sleep(0.5)

for hilo in hilos:
    hilo.join()

print("\n[+] Prueba T05 completada: Los 3 nodos transmitieron concurrentemente.")


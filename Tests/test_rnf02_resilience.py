import time
import json
from collections import deque
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
USER = "esp32_01"
PASS = "secret-node01"
TOPIC = "telecom/ESP32_01/telemetry"

local_buffer = deque()
connected = False

def on_connect(c, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"\n[{time.strftime('%X')}] [RECONEXION] Enlace MQTT restablecido.")
        # Vaciar y transmitir el buffer acumulado
        if local_buffer:
            print(f"[{time.strftime('%X')}] [BUFFER DRAIN] Reenviando {len(local_buffer)} paquetes encolados...")
            while local_buffer:
                p = local_buffer.popleft()
                c.publish(TOPIC, json.dumps(p), qos=1)
                print(f"   -> [BUFFER FLUSH] Reenviado seq={p['seq']}")
                time.sleep(0.05)
            print(f"[{time.strftime('%X')}] [BUFFER VACIO] Todos los mensajes acumulados fueron transmitidos.\n")
    else:
        connected = False

def on_disconnect(c, userdata, flags, rc, properties=None):
    global connected
    connected = False
    print(f"\n[{time.strftime('%X')}] [CORTE DETECTADO] Se perdio conexion con el Broker Mosquitto.")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASS)
client.on_connect = on_connect
client.on_disconnect = on_disconnect

print("[*] Iniciando prueba RNF-02: Buffer Local y Reconexion Automatica...")
print("[!] Apaga Mosquitto cuando se indique, espera 30s y vuelve a encenderlo.\n")

client.connect_async(BROKER, PORT, keepalive=5)
client.loop_start()

base_seq = int(time.time()) % 1000000 + 50000

for i in range(50):
    seq_num = base_seq + i
    payload = {
        "node_id": "ESP32_01",
        "seq": seq_num,
        "value": 24.5,
        "rssi": -50,
        "ts": int(time.time())
    }
    
    if connected:
        client.publish(TOPIC, json.dumps(payload), qos=1)
        print(f"[{time.strftime('%X')}] seq={seq_num} -> ENVIADO (Broker Online)")
    else:
        local_buffer.append(payload)
        print(f"[{time.strftime('%X')}] seq={seq_num} -> BROKER CAIDO: Guardado en buffer local (En cola: {len(local_buffer)})")
        
    time.sleep(1)

client.loop_stop()
client.disconnect()
print("[+] Prueba completada.")

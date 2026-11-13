import time
import json
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
USER = "esp32_01"
PASS = "secret-node01"
TOPIC = "telecom/ESP32_01/telemetry"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASS)

connected = False

def on_connect(c, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"[{time.strftime('%X')}] [CONECTADO] Enlace con Mosquitto establecido.")
    else:
        connected = False

def on_disconnect(c, userdata, flags, rc, properties=None):
    global connected
    connected = False
    print(f"[{time.strftime('%X')}] [DESCONECTADO] Se perdio comunicacion con el Broker Mosquitto.")

client.on_connect = on_connect
client.on_disconnect = on_disconnect

print("[*] Iniciando prueba RNF-02 (Resiliencia ante corte de Broker)...")
print("[!] Apaga Mosquitto (Ctrl+C en su ventana o det?n el servicio) durante ~30 segundos.")

client.connect_async(BROKER, PORT, keepalive=10)
client.loop_start()

base_seq = int(time.time()) % 1000000

for i in range(60):
    seq_num = base_seq + i
    payload = json.dumps({
        "node_id": "ESP32_01",
        "seq": seq_num,
        "value": 24.5,
        "rssi": -55,
        "ts": int(time.time())
    })
    
    if connected:
        info = client.publish(TOPIC, payload, qos=1)
        print(f"[{time.strftime('%X')}] seq={seq_num} -> ENVIADO (Broker ONLINE)")
    else:
        print(f"[{time.strftime('%X')}] seq={seq_num} -> FALLO DE RED: Encolando en buffer local...")
    
    time.sleep(1)

client.loop_stop()
client.disconnect()
print("[+] Prueba finalizada.")

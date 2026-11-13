import paho.mqtt.client as mqtt
import subprocess
import os
import json

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "telecom/+/telemetry"

PHP_EXE = r"C:\xampp\php\php.exe"
PHP_SUBSCRIBER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "subscriber.php")
)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[*] Conectado y autenticado en Mosquitto {BROKER}:{PORT}")
        client.subscribe(TOPIC)
        print(f"[*] Suscrito a: {TOPIC}")
    else:
        print(f"[!] Error de conexion MQTT. Codigo: {rc}")

def on_message(client, userdata, msg):
    payload_str = msg.payload.decode("utf-8", errors="ignore")
    topic = msg.topic

    # Invocar subscriber.php pasando el topic como argumento y el payload por stdin
    proceso = subprocess.run(
        [PHP_EXE, PHP_SUBSCRIBER, topic],
        input=payload_str,
        capture_output=True,
        text=True
    )

    if proceso.stdout:
        print(proceso.stdout.strip())
    if proceso.stderr:
        print("[PHP Error]", proceso.stderr.strip())

    # Enviar confirmacion (ACK) al nodo
    try:
        d = json.loads(payload_str)
        if "node_id" in d and "seq" in d:
            ack = json.dumps({"seq": d["seq"]})
            client.publish(f"telecom/{d['node_id']}/ack", ack)
    except Exception:
        pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# Credenciales del listener
client.username_pw_set("backend_listener", "listener-pass")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
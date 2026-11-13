"""
T14 - Idempotencia por MQTT: publica el MISMO mensaje dos veces.
Esperado: el listener responde 201 al primero y 409 al segundo,
y telemetry.log muestra ambas lineas con "source":"mqtt".

Requisitos: pip install paho-mqtt
Uso (con Mosquitto y el listener corriendo):
    python tests/prueba_mqtt_duplicado.py
"""
import json, time, random, os
import paho.mqtt.client as mqtt

BROKER  = "localhost"
PORT    = 1883
NODE_ID = "ESP32_01"
TOPIC   = f"telecom/{NODE_ID}/telemetry"
ACK     = f"telecom/{NODE_ID}/ack"
LOG     = "telemetry.log"   # ruta relativa a la carpeta lab2-backend

acks = []

def on_message(client, userdata, msg, *args):
    acks.append(msg.payload.decode(errors="replace"))
    print(f"  ACK recibido: {acks[-1]}")

try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)   # paho-mqtt 2.x
except AttributeError:
    client = mqtt.Client()                                   # paho-mqtt 1.x
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(ACK, qos=1)
client.loop_start()
time.sleep(0.5)

seq = 2_000_000 + int(time.time()) % 1_000_000   # seq nueva en cada ejecucion
payload = json.dumps({
    "node_id": NODE_ID, "seq": seq,
    "value": round(random.uniform(21, 25), 2),
    "rssi": random.randint(-60, -40), "ts": int(time.time()),
})

print(f"Topic: {TOPIC}\nPayload: {payload}\n")
for intento in (1, 2):
    print(f"[{intento}] Publicando seq={seq} ...")
    client.publish(TOPIC, payload, qos=1).wait_for_publish()
    time.sleep(1.5)

client.loop_stop(); client.disconnect()

print(f"\nACKs recibidos: {len(acks)} (esperado: 2 -> 201 y 409)")
if os.path.exists(LOG):
    print(f"\nUltimas lineas de {LOG} con seq {seq}:")
    with open(LOG, encoding="utf-8", errors="replace") as f:
        for linea in f.readlines()[-20:]:
            if str(seq) in linea:
                print("  " + linea.strip())
else:
    print(f"\n(No se encontro {LOG}; ejecuten:  Get-Content -Tail 2 telemetry.log)")

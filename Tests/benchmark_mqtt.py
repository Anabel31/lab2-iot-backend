import time
import json
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
USER = "esp32_01"
PASS = "secret-node01"
TOPIC = "telecom/ESP32_01/telemetry"
MENSAJES = 100

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASS)
client.connect(BROKER, PORT, 60)

t0 = time.perf_counter()
base_seq = int(time.time())

for i in range(MENSAJES):
    payload = json.dumps({
        "node_id": "ESP32_01",
        "seq": base_seq + i,
        "value": 24.0 + (i % 5),
        "rssi": -50,
        "ts": int(time.time())
    })
    client.publish(TOPIC, payload, qos=1)

t_total = time.perf_counter() - t0
rate = MENSAJES / t_total

print(f"=== BENCHMARK MQTT (100 MENSAJES) ===")
print(f"Total mensajes: {MENSAJES}")
print(f"Tiempo total:   {t_total:.3f} s")
print(f"Throughput:     {rate:.2f} msg/s")
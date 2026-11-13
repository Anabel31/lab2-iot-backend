import time
import json
import pymysql
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
USER = "esp32_01"
PASS = "secret-node01"
TOPIC = "telecom/ESP32_01/telemetry"
TOTAL_MSG = 100

db = pymysql.connect(
    host="127.0.0.1", 
    user="root", 
    password="", 
    database="iot_platform_db", 
    autocommit=True
)
cursor = db.cursor()

cursor.execute("SELECT COUNT(*) FROM telemetry WHERE device_id = 1")
conteo_inicial = cursor.fetchone()[0]

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASS)
client.connect(BROKER, PORT, 60)
client.loop_start()

base_seq = int(time.time()) % 1000000 + 30000

print(f"[*] Conteo inicial en BD: {conteo_inicial}")
print(f"[*] Publicando {TOTAL_MSG} mensajes por MQTT...")

t0 = time.perf_counter()

for i in range(TOTAL_MSG):
    payload = json.dumps({
        "node_id": "ESP32_01",
        "seq": base_seq + i,
        "value": 22.0 + (i % 5),
        "rssi": -55,
        "ts": int(time.time())
    })
    client.publish(TOPIC, payload, qos=1)

print("[*] Mensajes encolados. Esperando confirmacion en base de datos...")

while True:
    db.commit()
    cursor.execute("SELECT COUNT(*) FROM telemetry WHERE device_id = 1")
    conteo_actual = cursor.fetchone()[0]
    insertados = conteo_actual - conteo_inicial
    
    if insertados >= TOTAL_MSG:
        break
    time.sleep(0.02)

t_total = time.perf_counter() - t0
throughput = TOTAL_MSG / t_total

print("\n=== BENCHMARK MQTT: INGESTA Y PERSISTENCIA REAL ===")
print(f"Mensajes enviados y persistidos: {TOTAL_MSG}")
print(f"Tiempo total medido (E2E):      {t_total:.3f} s")
print(f"Throughput efectivo:            {throughput:.2f} msg/s (persistencia en MySQL)")

client.loop_stop()
client.disconnect()
db.close()

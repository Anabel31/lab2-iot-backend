"""
Benchmark MQTT con throughput y latencias p50/p95.

Publica N mensajes SIN pausa en telecom/{node}/telemetry y mide, por mensaje,
el tiempo desde la publicacion hasta que llega su ACK en telecom/{node}/ack.
Como el listener publica el ACK despues de llamar a TelemetryService
(validacion + INSERT en MySQL), la latencia incluye la persistencia.
>> Confirmen en el codigo del listener que el ACK se publica DESPUES de guardar.

Requisitos: pip install paho-mqtt
Uso: python tests/benchmark_mqtt_lat.py
"""
import json, time, random, os, csv, threading
import paho.mqtt.client as mqtt

BROKER, PORT = "localhost", 1883
NODE_ID = "ESP32_01"
N       = 100
TIMEOUT = 30          # segundos maximos esperando ACKs
TOPIC   = f"telecom/{NODE_ID}/telemetry"
ACK     = f"telecom/{NODE_ID}/ack"

enviados = {}          # seq -> t_envio
latencias = {}         # seq -> ms
codigos = {}
orden_envio = []
lock = threading.Lock()
t_ultimo_ack = None

def on_message(client, userdata, msg, *args):
    global t_ultimo_ack
    t = time.perf_counter()
    try:
        data = json.loads(msg.payload.decode())
    except Exception:
        data = {}
    # Busca seq en el ACK (en la raiz o dentro de "data"); si no viene, usa orden FIFO
    seq = data.get("seq") if isinstance(data, dict) else None
    if seq is None and isinstance(data.get("data"), dict):
        seq = data["data"].get("seq")
    with lock:
        if seq is None:
            pendientes = [s for s in orden_envio if s not in latencias]
            if not pendientes:
                return
            seq = pendientes[0]
        seq = int(seq)
        if seq in enviados and seq not in latencias:
            latencias[seq] = (t - enviados[seq]) * 1000
            codigos[seq] = data.get("status", data.get("code", "?"))
            t_ultimo_ack = t

def percentil(valores, p):
    v = sorted(valores)
    k = (len(v) - 1) * p
    f = int(k); c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)

try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(ACK, qos=1)
client.loop_start()
time.sleep(0.5)

base = 3_000_000 + (int(time.time()) % 100_000) * 10
print(f"Publicando {N} mensajes en {TOPIC} (sin pausa)...")
t0 = time.perf_counter()
for i in range(N):
    seq = base + i
    payload = json.dumps({"node_id": NODE_ID, "seq": seq,
                          "value": round(random.uniform(20, 25), 2),
                          "rssi": random.randint(-60, -40), "ts": int(time.time())})
    with lock:
        enviados[seq] = time.perf_counter()
        orden_envio.append(seq)
    client.publish(TOPIC, payload, qos=1)

limite = time.time() + TIMEOUT
while len(latencias) < N and time.time() < limite:
    time.sleep(0.05)
client.loop_stop(); client.disconnect()

recibidos = len(latencias)
if recibidos == 0:
    print("No llego ningun ACK. Revisen que el listener este corriendo y que publique en", ACK)
    raise SystemExit(1)

lat = list(latencias.values())
dt = t_ultimo_ack - t0
p50, p95 = percentil(lat, 0.50), percentil(lat, 0.95)
thr = recibidos / dt

print("-" * 70)
print(f"{'Mensajes':<10}{'ACKs':<8}{'Tiempo [s]':<13}{'Throughput [msg/s]':<21}{'p50 [ms]':<11}{'p95 [ms]'}")
print("-" * 70)
print(f"{N:<10}{recibidos:<8}{dt:<13.3f}{thr:<21.2f}{p50:<11.2f}{p95:.2f}")
print("-" * 70)
print(f"Perdidos/sin ACK: {N - recibidos}")

os.makedirs("docs", exist_ok=True)
with open("docs/benchmark_mqtt_resultados.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mensajes", "acks", "tiempo_s", "throughput_msg_s", "p50_ms", "p95_ms"])
    w.writerow([N, recibidos, f"{dt:.3f}", f"{thr:.2f}", f"{p50:.2f}", f"{p95:.2f}"])
print("[OK] Datos guardados en: docs/benchmark_mqtt_resultados.csv")

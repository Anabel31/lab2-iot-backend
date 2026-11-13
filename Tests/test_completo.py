import requests
import json
import time
import mysql.connector

BASE_URL = "http://localhost/lab2-backend/public/api/v1"
HEADERS_AUTH = {
    "Content-Type": "application/json",
    "Authorization": "Bearer secret-token-node01"
}

def get_telemetry_count():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="iot_platform_db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM telemetry")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        return f"Error BD: {e}"

def test_api():
    print("=" * 65)
    print("   BATERIA DE PRUEBAS AUTOMATIZADA - LABORATORIO 2 IoT")
    print("=" * 65)

    # 1. T01: Inserción Exitosa (201)
    seq_t01 = int(time.time()) % 100000
    payload_t01 = {"node_id": "ESP32_01", "seq": seq_t01, "value": 24.5, "rssi": -45, "ts": int(time.time())}
    r = requests.post(f"{BASE_URL}/telemetry", json=payload_t01, headers=HEADERS_AUTH)
    print(f"\n[T01] POST /telemetry (Valido)\nStatus: {r.status_code}\nRespuesta: {r.text}")

    # 2. T02: Token Invalido (401) + Verificación de No Inserción
    c_antes = get_telemetry_count()
    r = requests.post(f"{BASE_URL}/telemetry", json=payload_t01, headers={"Authorization": "Bearer token-falso"})
    c_despues = get_telemetry_count()
    print(f"\n[T02] POST /telemetry (Token invalido)\nStatus: {r.status_code} | Filas antes: {c_antes}, despues: {c_despues}\nRespuesta: {r.text}")

    # 3. T03: JSON Incompleto (422) + Verificación de No Inserción
    payload_incompleto = {"node_id": "ESP32_01", "seq": seq_t01 + 1, "rssi": -45, "ts": int(time.time())} # Falta 'value'
    c_antes = get_telemetry_count()
    r = requests.post(f"{BASE_URL}/telemetry", json=payload_incompleto, headers=HEADERS_AUTH)
    c_despues = get_telemetry_count()
    print(f"\n[T03] POST /telemetry (JSON incompleto, falta 'value')\nStatus: {r.status_code} | Filas antes: {c_antes}, despues: {c_despues}\nRespuesta: {r.text}")

    # 4. T04: Idempotencia (409)
    r = requests.post(f"{BASE_URL}/telemetry", json=payload_t01, headers=HEADERS_AUTH)
    print(f"\n[T04] POST /telemetry (Secuencia duplicada)\nStatus: {r.status_code}\nRespuesta: {r.text}")

    # 5. Demostración de Endpoints Adicionales (GET / PUT)
    print("\n" + "-" * 65)
    print("   VERIFICACION DE ENDPOINTS ADICIONALES (GET / PUT)")
    print("-" * 65)

    # GET /devices
    r = requests.get(f"{BASE_URL}/devices", headers=HEADERS_AUTH)
    print(f"[GET] /api/v1/devices -> Status: {r.status_code}\n{r.text[:200]}...")

    # GET /devices/1/telemetry
    r = requests.get(f"{BASE_URL}/devices/1/telemetry", headers=HEADERS_AUTH)
    print(f"\n[GET] /api/v1/devices/1/telemetry -> Status: {r.status_code}\n{r.text[:200]}...")

    # PUT /devices/1/config
    payload_config = {"config_key": "sampling_interval", "config_value": "10"}
    r = requests.put(f"{BASE_URL}/devices/1/config", json=payload_config, headers=HEADERS_AUTH)
    print(f"\n[PUT] /api/v1/devices/1/config -> Status: {r.status_code}\nRespuesta: {r.text}")

    # GET /events
    r = requests.get(f"{BASE_URL}/events", headers=HEADERS_AUTH)
    print(f"\n[GET] /api/v1/events -> Status: {r.status_code}\n{r.text[:200]}...")
    print("\n" + "=" * 65)

if __name__ == "__main__":
    test_api()
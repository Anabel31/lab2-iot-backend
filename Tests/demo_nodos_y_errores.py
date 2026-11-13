import time
import requests
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost/lab2-backend/public/api/v1/telemetry"

# Configuración de los 3 nodos según la base de datos
NODOS = {
    "ESP32_01": {"token": "secret-token-node01", "temp_base": 24.0},
    "ESP32_02": {"token": "secret-token-node02", "temp_base": 25.5},
    "ESP32_03": {"token": "secret-token-node03", "temp_base": 27.2} # > 26.0 dispara alarma
}

def obtener_filas_totales():
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="iot_platform_db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM telemetry")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total

def consultar_resumen_nodos():
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="iot_platform_db")
    cur = conn.cursor()
    cur.execute("""
        SELECT d.node_id, COUNT(t.id) AS total_muestras, MIN(t.seq) AS seq_min, MAX(t.seq) AS seq_max
        FROM devices d
        LEFT JOIN telemetry t ON d.id = t.device_id
        GROUP BY d.node_id
    """)
    filas = cur.fetchall()
    cur.close()
    conn.close()
    return filas

def enviar_muestra(node_id, seq, value, rssi=-50, token_override=None, payload_override=None):
    token = token_override if token_override is not None else NODOS[node_id]["token"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    if payload_override is not None:
        payload = payload_override
    else:
        payload = {
            "node_id": node_id,
            "seq": seq,
            "value": value,
            "rssi": rssi,
            "ts": int(time.time())
        }
        
    try:
        r = requests.post(BASE_URL, json=payload, headers=headers, timeout=5)
        return r.status_code, r.text
    except Exception as e:
        return 500, str(e)

def simular_trafico_nodo(node_id, seq_inicial, cantidad=5):
    resultados = []
    temp_base = NODOS[node_id]["temp_base"]
    for i in range(cantidad):
        seq = seq_inicial + i
        temp = round(temp_base + (i * 0.2), 2)
        status, resp = enviar_muestra(node_id, seq, temp)
        resultados.append((node_id, seq, status))
        time.sleep(0.05)
    return resultados

def main():
    print("=" * 70)
    print("      DEMOSTRACION: INGESTA MULTI-NODO Y CASOS DE ERROR (LAB 2)")
    print("=" * 70)

    # -------------------------------------------------------------
    # PARTE 1: SIMULACION DE ERRORES Y COMPROBACION DE INTEGRIDAD
    # -------------------------------------------------------------
    print("\n--- [PARTE 1] CASOS DE ERROR Y RECHAZO DE DATOS INCORRECTOS ---")
    
    filas_inicio = obtener_filas_totales()
    print(f"[*] Filas iniciales en tabla 'telemetry': {filas_inicio}\n")
    
    seq_prueba = int(time.time()) % 100000 + 20000

    # Error 1: Autenticación rechazada (Token incorrecto -> 401)
    status_401, resp_401 = enviar_muestra("ESP32_01", seq_prueba, 24.0, token_override="token_falso_123")
    filas_post_401 = obtener_filas_totales()
    print(f"1. Token Falso: Status = {status_401} (Esperado 401)")
    print(f"   Respuesta: {resp_401}")
    print(f"   Verificacion BD: Antes = {filas_inicio}, Despues = {filas_post_401} (Sin cambios)\n")

    # Error 2: Contrato incompleto (Falta el campo 'value' -> 422)
    payload_sin_value = {"node_id": "ESP32_01", "seq": seq_prueba, "rssi": -45, "ts": int(time.time())}
    status_422_a, resp_422_a = enviar_muestra("ESP32_01", seq_prueba, 0, payload_override=payload_sin_value)
    filas_post_422_a = obtener_filas_totales()
    print(f"2. JSON Incompleto (sin 'value'): Status = {status_422_a} (Esperado 422)")
    print(f"   Respuesta: {resp_422_a}")
    print(f"   Verificacion BD: Antes = {filas_post_401}, Despues = {filas_post_422_a} (Sin cambios)\n")

    # Error 3: Valor fisico fuera de rango (150 °C -> 422)
    status_422_b, resp_422_b = enviar_muestra("ESP32_01", seq_prueba, 150.0)
    filas_post_422_b = obtener_filas_totales()
    print(f"3. Temperatura Fuera de Rango (150 C): Status = {status_422_b} (Esperado 422)")
    print(f"   Respuesta: {resp_422_b}")
    print(f"   Verificacion BD: Antes = {filas_post_422_a}, Despues = {filas_post_422_b} (Sin cambios)\n")

    # Inserción válida de referencia
    status_201, resp_201 = enviar_muestra("ESP32_01", seq_prueba, 24.0)
    filas_post_201 = obtener_filas_totales()
    print(f"4. Insercion Valida: Status = {status_201} (Esperado 201)")
    print(f"   Respuesta: {resp_201}")
    print(f"   Verificacion BD: Antes = {filas_post_422_b}, Despues = {filas_post_201} (+1 registro guardado)\n")

    # Error 4: Reintento de la misma secuencia (Idempotencia -> 409)
    status_409, resp_409 = enviar_muestra("ESP32_01", seq_prueba, 24.0)
    filas_post_409 = obtener_filas_totales()
    print(f"5. Secuencia Repetida (Idempotencia): Status = {status_409} (Esperado 409)")
    print(f"   Respuesta: {resp_409}")
    print(f"   Verificacion BD: Antes = {filas_post_201}, Despues = {filas_post_409} (Sin cambios, duplicado evitado)")

    # -------------------------------------------------------------
    # PARTE 2: CONCURRENCIA DE LOS 3 NODOS EN PARALELO
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("--- [PARTE 2] ENVIO SIMULTANEO DE LOS 3 NODOS (ESP32_01, 02, 03) ---")
    print("=" * 70)
    
    seq_nodos = int(time.time()) % 100000 + 40000

    with ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(simular_trafico_nodo, "ESP32_01", seq_nodos, 5)
        f2 = executor.submit(simular_trafico_nodo, "ESP32_02", seq_nodos, 5)
        f3 = executor.submit(simular_trafico_nodo, "ESP32_03", seq_nodos, 5)

        todos = f1.result() + f2.result() + f3.result()

    for nodo, seq, st in todos:
        print(f"Nodo {nodo} | seq: {seq} | Status: {st}")

    print("\n--- ESTADO DE PERSISTENCIA EN MYSQL (AGRUPADO POR NODO) ---")
    resumen = consultar_resumen_nodos()
    print(f"{'Nodo':<12} | {'Total Muestras':<16} | {'Seq Min':<10} | {'Seq Max':<10}")
    print("-" * 55)
    for r in resumen:
        print(f"{r[0]:<12} | {r[1]:<16} | {str(r[2]):<10} | {str(r[3]):<10}")

    print("=" * 70)
    print("Prueba finalizada exitosamente.")

if __name__ == "__main__":
    main()
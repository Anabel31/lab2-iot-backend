import concurrent.futures
import time
import csv
import os
import requests
import numpy as np
import matplotlib.pyplot as plt

URL = "http://localhost/lab2-backend/public/api/v1/telemetry"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer secret-token-node01"
}

CONCURRENCIAS = [1, 5, 10, 20]
MUESTRAS_POR_NIVEL = 100
BASE_SEQ = 200000

csv_rows = [["concurrencia", "throughput_req_s", "latencia_p50_ms", "latencia_p95_ms", "errores"]]
res_lambda = []
res_p50 = []
res_p95 = []

def enviar_muestra(seq):
    payload = {
        "node_id": "ESP32_01",
        "seq": seq,
        "value": 24.5,
        "rssi": -55,
        "ts": int(time.time())
    }
    t_start = time.perf_counter()
    try:
        r = requests.post(URL, json=payload, headers=HEADERS, timeout=5)
        duracion = (time.perf_counter() - t_start) * 1000
        return (r.status_code == 201, duracion)
    except Exception:
        return (False, 0)

print(f"{'Concurrencia':<15}{'Throughput (req/s)':<22}{'Latencia p50 (ms)':<20}{'Latencia p95 (ms)':<20}{'Errores':<10}")
print("-" * 87)

secuencia_actual = BASE_SEQ

for c in CONCURRENCIAS:
    seqs = list(range(secuencia_actual, secuencia_actual + MUESTRAS_POR_NIVEL))
    secuencia_actual += MUESTRAS_POR_NIVEL

    tiempos = []
    errores = 0
    t0 = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=c) as executor:
        futuros = [executor.submit(enviar_muestra, s) for s in seqs]
        for f in concurrent.futures.as_completed(futuros):
            ok, duracion = f.result()
            if ok:
                tiempos.append(duracion)
            else:
                errores += 1

    t_total = time.perf_counter() - t0
    throughput = len(tiempos) / t_total if t_total > 0 else 0
    p50 = float(np.percentile(tiempos, 50)) if tiempos else 0.0
    p95 = float(np.percentile(tiempos, 95)) if tiempos else 0.0

    res_lambda.append(throughput)
    res_p50.append(p50)
    res_p95.append(p95)

    csv_rows.append([c, round(throughput, 2), round(p50, 2), round(p95, 2), errores])
    print(f"{c:<15}{throughput:<22.2f}{p50:<20.2f}{p95:<20.2f}{errores:<10}")

# 1. Guardar CSV
os.makedirs("docs", exist_ok=True)
csv_path = "docs/benchmark_resultados.csv"
with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(csv_rows)
print(f"\n[OK] Datos guardados en: {csv_path}")

# 2. Generar Gráfica
fig, ax1 = plt.subplots(figsize=(9, 5))

color = "tab:blue"
ax1.set_xlabel("Nivel de Concurrencia (Hilos)")
ax1.set_ylabel("Throughput (req/s)", color=color)
ax1.plot(CONCURRENCIAS, res_lambda, color=color, marker="o", linewidth=2, label="Throughput (λ)")
ax1.tick_params(axis="y", labelcolor=color)
ax1.grid(True, linestyle="--", alpha=0.5)

ax2 = ax1.twinx()
color = "tab:red"
ax2.set_ylabel("Latencia (ms)", color=color)
ax2.plot(CONCURRENCIAS, res_p50, color="tab:green", marker="s", linestyle="--", label="p50")
ax2.plot(CONCURRENCIAS, res_p95, color=color, marker="^", linestyle="--", label="p95")
ax2.tick_params(axis="y", labelcolor=color)

fig.suptitle("Evaluacion de Carga Concurrente (Lab 2 Backend IoT)")
fig.tight_layout()

img_path = "docs/grafica_benchmark.png"
plt.savefig(img_path, dpi=300)
print(f"[OK] Grafica guardada en: {img_path}")
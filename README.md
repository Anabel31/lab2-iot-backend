# Plataforma Backend IoT (REST + MQTT) - Laboratorio 2

Backend modular con arquitectura desacoplada sobre **PHP 8**, **MySQL**, **Apache** y **MQTT Mosquitto**.

## Arquitectura
- `public/index.php`: Enrutador frontal REST (`/api/v1`) libre de SQL directo.
- `src/Controllers/`: Controladores HTTP (`Telemetry`, `Device`, `Config`, `Command`, `Event`).
- `src/Services/`: Validacion fisica (-40 a 85 C), idempotencia (HTTP 409) y alertas.
- `src/Repositories/`: Persistencia mediante PDO y sentencias preparadas.
- `mqtt/listener.py`: Suscriptor MQTT que invoca ``php.exe subscriber.php`` por mensaje llamando directamente a ``TelemetryService``, publicando el ACK tras confirmar la persistencia en MySQL.
- `tests/`: Suite de pruebas (`pruebas_extra.ps1`, `prueba_mqtt_duplicado.py`, `benchmark_mqtt_lat.py`).

## Resultados Benchmark MQTT (100 mensajes)
- **Tasa de entrega:** 100 / 100 ACKs (0% perdida)
- **Throughput:** 13.71 msg/s (7.292 s total)
- **Latencia p50:** 3880.50 ms
- **Latencia p95:** 6939.57 ms

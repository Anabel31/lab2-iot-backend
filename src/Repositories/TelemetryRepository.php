<?php
// src/Repositories/TelemetryRepository.php

namespace Repositories;

use Database\Connection;
use PDO;

class TelemetryRepository {
    private PDO $db;

    public function __construct() {
        $this->db = Connection::getInstance();
    }

    // Verificar si ya existe un registro con el mismo device_id y seq (idempotencia)
    public function exists(int $deviceId, int $seq): bool {
        $stmt = $this->db->prepare(
            "SELECT 1 FROM telemetry WHERE device_id = :device_id AND seq = :seq LIMIT 1"
        );
        $stmt->execute([
            'device_id' => $deviceId,
            'seq' => $seq
        ]);
        return (bool) $stmt->fetchColumn();
    }

    // Inserción flexible: acepta 5 argumentos posicionales o un array asociativo
    public function insert($deviceIdOrPayload, ?int $seq = null, ?float $value = null, ?int $rssi = null, ?int $ts = null): int {
        if (is_array($deviceIdOrPayload)) {
            $deviceId = $deviceIdOrPayload['device_id'];
            $seq      = $deviceIdOrPayload['seq'];
            $value    = $deviceIdOrPayload['value'];
            $rssi     = $deviceIdOrPayload['rssi'];
            $ts       = $deviceIdOrPayload['ts'];
        } else {
            $deviceId = $deviceIdOrPayload;
        }

        $stmt = $this->db->prepare(
            "INSERT INTO telemetry (device_id, seq, value, rssi, ts)
             VALUES (?, ?, ?, ?, ?)"
        );
        $stmt->execute([$deviceId, $seq, $value, $rssi, $ts]);

        return (int) $this->db->lastInsertId();
    }

    // Obtener histórico de telemetría de un dispositivo (para GET /api/v1/devices/{id}/telemetry)
    public function getHistoryByDeviceId(int $deviceId, int $limit = 50): array {
        $stmt = $this->db->prepare(
            "SELECT id, device_id, ts, value, rssi, seq, created_at 
             FROM telemetry 
             WHERE device_id = :device_id 
             ORDER BY ts DESC 
             LIMIT :limit"
        );
        $stmt->bindValue(':device_id', $deviceId, PDO::PARAM_INT);
        $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
        $stmt->execute();

        return $stmt->fetchAll();
    }

    // Registrar un evento o alarma cuando la temperatura supera el umbral
    public function insertEvent(int $deviceId, string $type, string $severity, int $ts): void {
        $stmt = $this->db->prepare(
            "INSERT INTO events (device_id, type, severity, ts)
             VALUES (:device_id, :type, :severity, :ts)"
        );
        $stmt->execute([
            'device_id' => $deviceId,
            'type'      => $type,
            'severity'  => $severity,
            'ts'        => $ts
        ]);
    }
}
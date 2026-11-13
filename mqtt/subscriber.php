<?php
// mqtt/subscriber.php

require_once __DIR__ . '/../src/Database/Connection.php';
require_once __DIR__ . '/../src/Repositories/DeviceRepository.php';
require_once __DIR__ . '/../src/Repositories/TelemetryRepository.php';
require_once __DIR__ . '/../src/Repositories/EventRepository.php';
require_once __DIR__ . '/../src/Repositories/ConfigRepository.php';
require_once __DIR__ . '/../src/Services/TelemetryService.php';

use Services\TelemetryService;

$topic = $argv[1] ?? '';
$payloadJson = file_get_contents('php://stdin');

if (empty($payloadJson)) {
    fwrite(STDERR, "[ERROR] Payload vacio recibido\n");
    exit(1);
}

$data = json_decode($payloadJson, true);
if (!$data || !is_array($data)) {
    fwrite(STDERR, "[ERROR] JSON invalido recibido: " . $payloadJson . "\n");
    exit(1);
}

// Validar que el topic coincida con el node_id del payload (prevención de spoofing)
if (!empty($topic)) {
    $expectedTopic = "telecom/{$data['node_id']}/telemetry";
    if ($topic !== $expectedTopic) {
        fwrite(STDERR, "[ERROR 403] Topic '{$topic}' no coincide con el nodo '{$data['node_id']}'\n");
        exit(1);
    }
}

$service = new TelemetryService();
$result = $service->recordTelemetry($data, 'mqtt');

if ($result['status'] === 201) {
    echo "[OK 201] Telemetria registrada por MQTT. ID: " . $result['response']['data']['telemetry_id'] . PHP_EOL;
} elseif ($result['status'] === 409) {
    echo "[WARN 409] Idempotencia MQTT: " . $result['response']['error'] . PHP_EOL;
} else {
    echo "[ERROR {$result['status']}] " . json_encode($result['response']) . PHP_EOL;
}
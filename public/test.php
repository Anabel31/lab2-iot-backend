<?php
// public/test.php

require_once __DIR__ . '/../src/Database/Connection.php';
require_once __DIR__ . '/../src/Repositories/DeviceRepository.php';
require_once __DIR__ . '/../src/Repositories/TelemetryRepository.php';
require_once __DIR__ . '/../src/Services/TelemetryService.php';

$service = new Services\TelemetryService();

// Simulación de un paquete recibido del ESP32_01 con secuencia 50
$paquetePrueba = [
    'node_id' => 'ESP32_01',
    'seq'     => 50,
    'value'   => 24.5,
    'rssi'    => -45,
    'ts'      => time()
];

$resultado = $service->recordTelemetry($paquetePrueba);

http_response_code($resultado['status']);
header('Content-Type: application/json');
echo json_encode($resultado, JSON_PRETTY_PRINT);
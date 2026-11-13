<?php
namespace Controllers;

require_once __DIR__ . '/../Repositories/DeviceRepository.php';
require_once __DIR__ . '/../Repositories/TelemetryRepository.php';

use Repositories\DeviceRepository;
use Repositories\TelemetryRepository;

class DeviceController {
    private DeviceRepository $devices;
    private TelemetryRepository $telemetry;

    public function __construct() {
        $this->devices = new DeviceRepository();
        $this->telemetry = new TelemetryRepository();
    }

    public function index(): void {
        $data = $this->devices->getAll();
        http_response_code(200);
        echo json_encode([
            'ok'   => true,
            'data' => $data,
            'meta' => ['api_version' => 'v1']
        ]);
    }

    public function telemetry(int $deviceId): void {
        $device = $this->devices->findById($deviceId);
        if (!$device) {
            http_response_code(404);
            echo json_encode([
                'ok'    => false,
                'error' => "Dispositivo con ID {$deviceId} no encontrado",
                'meta'  => ['api_version' => 'v1']
            ]);
            return;
        }

        $limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 50;
        $data = $this->telemetry->getByDeviceId($deviceId, $limit);

        http_response_code(200);
        echo json_encode([
            'ok'   => true,
            'data' => $data,
            'meta' => ['api_version' => 'v1']
        ]);
    }
}

<?php
namespace Controllers;

require_once __DIR__ . '/../Database/Connection.php';
require_once __DIR__ . '/../Repositories/DeviceRepository.php';
require_once __DIR__ . '/../Repositories/TelemetryRepository.php';
require_once __DIR__ . '/../Repositories/EventRepository.php';
require_once __DIR__ . '/../Repositories/ConfigRepository.php';
require_once __DIR__ . '/../Services/TelemetryService.php';

use Repositories\DeviceRepository;
use Services\TelemetryService;

class TelemetryController {
    private DeviceRepository $devices;
    private TelemetryService $service;

    public function __construct() {
        $this->devices = new DeviceRepository();
        $this->service = new TelemetryService();
    }

    public function store(): void {
        $authHeader = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
        if (empty($authHeader) && function_exists('apache_request_headers')) {
            $headers = apache_request_headers();
            $authHeader = $headers['Authorization'] ?? $headers['authorization'] ?? '';
        }

        if (!preg_match('/Bearer\s+(\S+)/', $authHeader, $matches)) {
            http_response_code(401);
            echo json_encode(['ok' => false, 'error' => 'Token no proporcionado o invalido', 'meta' => ['api_version' => 'v1']]);
            return;
        }

        $rawToken = $matches[1];
        $tokenHash = hash('sha256', $rawToken);
        $device = $this->devices->findByTokenHash($tokenHash);

        if (!$device) {
            http_response_code(401);
            echo json_encode(['ok' => false, 'error' => 'Token invalido o no reconocido', 'meta' => ['api_version' => 'v1']]);
            return;
        }

        $input = file_get_contents('php://input');
        $data = json_decode($input, true);

        if (!$data || !is_array($data)) {
            http_response_code(422);
            echo json_encode(['ok' => false, 'error' => 'Cuerpo JSON invalido', 'meta' => ['api_version' => 'v1']]);
            return;
        }

        if (isset($data['node_id']) && $data['node_id'] !== $device['node_id']) {
            http_response_code(403);
            echo json_encode(['ok' => false, 'error' => 'Token no autorizado para el nodo indicado', 'meta' => ['api_version' => 'v1']]);
            return;
        }

        $result = $this->service->recordTelemetry($data, 'rest');
        
        // Forzar expl?citamente el c?digo de respuesta devuelto por el servicio
        http_response_code((int)$result['status']);
        echo json_encode($result['response']);
    }
}

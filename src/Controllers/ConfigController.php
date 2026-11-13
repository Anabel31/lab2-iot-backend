<?php
namespace Controllers;

require_once __DIR__ . '/../Repositories/ConfigRepository.php';

use Repositories\ConfigRepository;

class ConfigController {
    private ConfigRepository $config;

    public function __construct() {
        $this->config = new ConfigRepository();
    }

    public function update(int $deviceId, array $payload, string $authHeader): array {
        if (!preg_match('/Bearer\s+(\S+)/', $authHeader, $matches)) {
            return ['status' => 401, 'response' => ['ok' => false, 'error' => 'Token no proporcionado', 'meta' => ['api_version' => 'v1']]];
        }

        $token = $matches[1];
        if ($token !== 'admin-token-lab2') {
            return ['status' => 401, 'response' => ['ok' => false, 'error' => 'Token no autorizado para configuracion', 'meta' => ['api_version' => 'v1']]];
        }

        if (!isset($payload['sample_interval']) || !isset($payload['threshold'])) {
            return ['status' => 422, 'response' => ['ok' => false, 'error' => 'Parametros requeridos: sample_interval y threshold', 'meta' => ['api_version' => 'v1']]];
        }

        $this->config->upsert($deviceId, (int)$payload['sample_interval'], (float)$payload['threshold']);

        return [
            'status' => 200,
            'response' => [
                'ok' => true,
                'data' => [
                    'device_id' => $deviceId,
                    'sample_interval' => (int)$payload['sample_interval'],
                    'threshold' => (float)$payload['threshold']
                ],
                'meta' => ['api_version' => 'v1']
            ]
        ];
    }
}

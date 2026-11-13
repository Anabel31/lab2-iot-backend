<?php
namespace Controllers;

require_once __DIR__ . '/../Repositories/CommandRepository.php';

use Repositories\CommandRepository;

class CommandController {
    private CommandRepository $commands;

    public function __construct() {
        $this->commands = new CommandRepository();
    }

    public function create(int $deviceId, array $payload): array {
        $authHeader = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
        if (empty($authHeader) && function_exists('apache_request_headers')) {
            $headers = apache_request_headers();
            $authHeader = $headers['Authorization'] ?? $headers['authorization'] ?? '';
        }

        if (!preg_match('/Bearer\s+(\S+)/', $authHeader, $matches) || $matches[1] !== 'admin-token-lab2') {
            return [
                'status' => 401,
                'response' => ['ok' => false, 'error' => 'Token de administrador invalido o no proporcionado', 'meta' => ['api_version' => 'v1']]
            ];
        }

        if (empty($payload['command'])) {
            return [
                'status' => 422,
                'response' => ['ok' => false, 'error' => 'El campo command es obligatorio', 'meta' => ['api_version' => 'v1']]
            ];
        }

        $cmdId = $this->commands->create($deviceId, $payload['command']);

        return [
            'status' => 201,
            'response' => [
                'ok' => true,
                'data' => [
                    'command_id' => $cmdId,
                    'device_id'  => $deviceId,
                    'command'    => $payload['command'],
                    'status'     => 'pending'
                ],
                'meta' => ['api_version' => 'v1']
            ]
        ];
    }
}

<?php
// src/Middleware/AuthMiddleware.php

namespace Middleware;

use Repositories\DeviceRepository;

class AuthMiddleware {
    private DeviceRepository $deviceRepo;

    public function __construct() {
        $this->deviceRepo = new DeviceRepository();
    }

    /**
     * Valida el token enviado en la cabecera 'Authorization: Bearer <token>'
     * o en el cuerpo JSON mediante el campo 'token'.
     */
    public function authenticate(?string $nodeId = null): ?array {
        $token = null;

        // 1. Buscar en la cabecera HTTP Authorization
        $headers = getallheaders();
        if (isset($headers['Authorization'])) {
            if (preg_match('/Bearer\s(\S+)/', $headers['Authorization'], $matches)) {
                $token = $matches[1];
            }
        } elseif (isset($headers['authorization'])) {
            if (preg_match('/Bearer\s(\S+)/', $headers['authorization'], $matches)) {
                $token = $matches[1];
            }
        }

        // 2. Si no viene en cabecera, revisar si viene en JSON body
        if (!$token) {
            $input = json_decode(file_get_contents('php://input'), true);
            if (isset($input['token'])) {
                $token = $input['token'];
            }
        }

        if (!$token) {
            $this->unauthorized('Token de autenticación no proporcionado');
        }

        // Si se especificó el nodeId, validamos directamente contra ese nodo
        if ($nodeId) {
            $device = $this->deviceRepo->findByNodeId($nodeId);
            if (!$device || hash('sha256', $token) !== $device['token_hash']) {
                $this->unauthorized('Token inválido para el nodo especificado');
            }
            return $device;
        }

        return ['token' => $token];
    }

    private function unauthorized(string $message): void {
        http_response_code(401);
        header('Content-Type: application/json');
        echo json_encode([
            'ok' => false,
            'error' => $message
        ]);
        exit;
    }
}
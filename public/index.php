<?php
declare(strict_types=1);

date_default_timezone_set('America/Lima');

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

header("Content-Type: application/json; charset=UTF-8");

require_once __DIR__ . '/../src/Database/Connection.php';
require_once __DIR__ . '/../src/Repositories/DeviceRepository.php';
require_once __DIR__ . '/../src/Repositories/TelemetryRepository.php';
require_once __DIR__ . '/../src/Repositories/EventRepository.php';
require_once __DIR__ . '/../src/Repositories/ConfigRepository.php';
require_once __DIR__ . '/../src/Repositories/CommandRepository.php';
require_once __DIR__ . '/../src/Services/TelemetryService.php';
require_once __DIR__ . '/../src/Controllers/TelemetryController.php';
require_once __DIR__ . '/../src/Controllers/DeviceController.php';
require_once __DIR__ . '/../src/Controllers/EventController.php';
require_once __DIR__ . '/../src/Controllers/ConfigController.php';
require_once __DIR__ . '/../src/Controllers/CommandController.php';

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

$prefix = '/lab2-backend/public/api/v1';
if (strpos($uri, $prefix) === 0) {
    $path = substr($uri, strlen($prefix));
} else {
    $path = $uri;
}
$path = '/' . trim($path, '/');

if ($method === 'POST' && $path === '/telemetry') {
    $controller = new \Controllers\TelemetryController();
    $controller->store();
    exit;
} elseif ($method === 'GET' && $path === '/devices') {
    $controller = new \Controllers\DeviceController();
    $controller->index();
    exit;
} elseif ($method === 'GET' && preg_match('#^/devices/(\d+)/telemetry$#', $path, $m)) {
    $controller = new \Controllers\DeviceController();
    $controller->telemetry((int)$m[1]);
    exit;
} elseif ($method === 'PUT' && preg_match('#^/devices/(\d+)/config$#', $path, $m)) {
    $controller = new \Controllers\ConfigController();
    $raw = json_decode(file_get_contents('php://input'), true) ?? [];
    $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if (empty($auth) && function_exists('apache_request_headers')) {
        $h = apache_request_headers();
        $auth = $h['Authorization'] ?? $h['authorization'] ?? '';
    }
    $res = $controller->update((int)$m[1], $raw, $auth);
    http_response_code($res['status']);
    echo json_encode($res['response']);
    exit;
} elseif ($method === 'GET' && $path === '/events') {
    $controller = new \Controllers\EventController();
    $controller->index();
    exit;
} elseif ($method === 'POST' && preg_match('#^/devices/(\d+)/commands$#', $path, $m)) {
    $controller = new \Controllers\CommandController();
    $raw = json_decode(file_get_contents('php://input'), true) ?? [];
    $res = $controller->create((int)$m[1], $raw);
    http_response_code($res['status']);
    echo json_encode($res['response']);
    exit;
} else {
    http_response_code(404);
    echo json_encode(['ok' => false, 'error' => 'Endpoint no encontrado', 'meta' => ['api_version' => 'v1']]);
    exit;
}

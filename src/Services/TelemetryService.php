<?php
namespace Services;

require_once __DIR__ . '/../Repositories/DeviceRepository.php';
require_once __DIR__ . '/../Repositories/TelemetryRepository.php';
require_once __DIR__ . '/../Repositories/EventRepository.php';
require_once __DIR__ . '/../Repositories/ConfigRepository.php';

use Repositories\DeviceRepository;
use Repositories\TelemetryRepository;
use Repositories\EventRepository;
use Repositories\ConfigRepository;
use PDOException;

class TelemetryService {
    private DeviceRepository $devices;
    private TelemetryRepository $telemetry;
    private EventRepository $events;
    private ConfigRepository $config;

    public function __construct() {
        $this->devices = new DeviceRepository();
        $this->telemetry = new TelemetryRepository();
        $this->events = new EventRepository();
        $this->config = new ConfigRepository();
    }

    public function recordTelemetry(array $data, string $source = 'rest'): array {
        date_default_timezone_set('America/Lima');

        if (!isset($data['ts']) && isset($data['timestamp'])) {
            $data['ts'] = $data['timestamp'];
        }

        $required = ['node_id', 'seq', 'value', 'rssi', 'ts'];
        foreach ($required as $field) {
            if (!isset($data[$field])) {
                return [
                    'status' => 422,
                    'response' => ['ok' => false, 'error' => "Campo obligatorio faltante: {$field}", 'meta' => ['api_version' => 'v1']]
                ];
            }
        }

        $val = (float)$data['value'];
        if ($val < -40.0 || $val > 85.0) {
            return [
                'status' => 422,
                'response' => ['ok' => false, 'error' => "Valor fuera de rango fisico (-40 a 85 C): {$val}", 'meta' => ['api_version' => 'v1']]
            ];
        }

        $device = $this->devices->findByNodeId($data['node_id']);
        if (!$device) {
            return [
                'status' => 404,
                'response' => ['ok' => false, 'error' => "Dispositivo '{$data['node_id']}' no registrado", 'meta' => ['api_version' => 'v1']]
            ];
        }

        $deviceId = (int)$device['id'];

        if ($this->telemetry->exists($deviceId, (int)$data['seq'])) {
            return [
                'status' => 409,
                'response' => ['ok' => false, 'error' => 'Mensaje duplicado: secuencia ya registrada para este nodo', 'meta' => ['api_version' => 'v1']]
            ];
        }

        try {
            $telemetryId = $this->telemetry->insert($deviceId, (int)$data['seq'], $val, (int)$data['rssi'], (int)$data['ts']);
            $this->devices->touchLastSeen($deviceId);

            $cfg = $this->config->getByDeviceId($deviceId);
            $threshold = ($cfg && isset($cfg['threshold'])) ? (float)$cfg['threshold'] : 26.0;
            $triggered = false;

            if ($val > $threshold) {
                $this->events->insert($deviceId, 'temp_high', 'warning', (int)$data['ts']);
                $triggered = true;
            }

            $logEntry = json_encode([
                'timestamp' => date('c'),
                'source'    => $source,
                'node_id'   => $data['node_id'],
                'seq'       => (int)$data['seq'],
                'value'     => $val,
                'status'    => 201
            ]) . PHP_EOL;
            file_put_contents(__DIR__ . '/../../telemetry.log', $logEntry, FILE_APPEND | LOCK_EX);

            return [
                'status' => 201,
                'response' => [
                    'ok'   => true,
                    'data' => ['telemetry_id' => $telemetryId, 'event_triggered' => $triggered],
                    'meta' => ['api_version' => 'v1']
                ]
            ];
        } catch (PDOException $e) {
            if ($e->getCode() === '23000' || strpos($e->getMessage(), '1062') !== false) {
                return [
                    'status' => 409,
                    'response' => ['ok' => false, 'error' => 'Mensaje duplicado: secuencia ya registrada para este nodo', 'meta' => ['api_version' => 'v1']]
                ];
            }

            $traceId = bin2hex(random_bytes(8));
            $sqlErrorLog = json_encode([
                'trace_id'  => $traceId,
                'timestamp' => date('c'),
                'error_sql' => $e->getMessage(),
                'source'    => $source
            ]) . PHP_EOL;
            file_put_contents(__DIR__ . '/../../telemetry.log', $sqlErrorLog, FILE_APPEND | LOCK_EX);

            return [
                'status' => 500,
                'response' => [
                    'ok'       => false,
                    'error'    => 'Error interno de base de datos',
                    'trace_id' => $traceId,
                    'meta'     => ['api_version' => 'v1']
                ]
            ];
        }
    }
}

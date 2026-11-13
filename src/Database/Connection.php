<?php
namespace Database;

use PDO;
use PDOException;

class Connection {
    private static ?PDO $instance = null;

    public static function getInstance(): PDO {
        if (self::$instance === null) {
            $host = '127.0.0.1';
            $db   = 'iot_platform_db';
            $user = 'root';
            $pass = '';
            $charset = 'utf8mb4';

            $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
            $options = [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES   => false,
            ];

            try {
                self::$instance = new PDO($dsn, $user, $pass, $options);
            } catch (PDOException $e) {
                // RNF-04: Generar trace_id y registrar el fallo SQL internamente
                $traceId = bin2hex(random_bytes(8));
                date_default_timezone_set('UTC');

                $logEntry = json_encode([
                    'trace_id'  => $traceId,
                    'timestamp' => date('c'),
                    'error_sql' => $e->getMessage(),
                    'source'    => 'database_connection'
                ]) . PHP_EOL;

                file_put_contents(__DIR__ . '/../../telemetry.log', $logEntry, FILE_APPEND | LOCK_EX);

                // Responder con 500 sin exponer detalles de la infraestructura
                http_response_code(500);
                header('Content-Type: application/json; charset=UTF-8');
                echo json_encode([
                    'ok'       => false,
                    'error'    => 'Error interno de base de datos',
                    'trace_id' => $traceId,
                    'meta'     => ['api_version' => 'v1']
                ]);
                exit;
            }
        }

        return self::$instance;
    }
}

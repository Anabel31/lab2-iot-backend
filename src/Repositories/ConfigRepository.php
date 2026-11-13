<?php
namespace Repositories;

require_once __DIR__ . '/../Database/Connection.php';

use Database\Connection;
use PDO;

class ConfigRepository {
    private PDO $db;

    public function __construct() {
        $this->db = Connection::getInstance();
    }

    public function getByDeviceId(int $deviceId): ?array {
        $stmt = $this->db->prepare("SELECT * FROM configurations WHERE device_id = ? LIMIT 1");
        $stmt->execute([$deviceId]);
        $cfg = $stmt->fetch(PDO::FETCH_ASSOC);
        return $cfg ?: null;
    }

    public function upsert(int $deviceId, int $interval, float $threshold): void {
        $sql = "INSERT INTO configurations (device_id, sample_interval, threshold) 
                VALUES (?, ?, ?) 
                ON DUPLICATE KEY UPDATE 
                    sample_interval = VALUES(sample_interval), 
                    threshold = VALUES(threshold)";
        $stmt = $this->db->prepare($sql);
        $stmt->execute([$deviceId, $interval, $threshold]);
    }
}

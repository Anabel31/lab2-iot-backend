<?php
// src/Repositories/CommandRepository.php
namespace Repositories;

use Database\Connection;
use PDO;

class CommandRepository {
    private PDO $db;

    public function __construct() {
        $this->db = Connection::getInstance();
    }

    public function create(int $deviceId, string $command): int {
        $stmt = $this->db->prepare("INSERT INTO commands (device_id, command) VALUES (?, ?)");
        $stmt->execute([$deviceId, $command]);
        return (int)$this->db->lastInsertId();
    }

    public function getPending(int $deviceId): array {
        $stmt = $this->db->prepare("SELECT * FROM commands WHERE device_id = ? AND status = 'pending' ORDER BY id ASC");
        $stmt->execute([$deviceId]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}
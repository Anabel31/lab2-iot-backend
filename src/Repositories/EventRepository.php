<?php
namespace Repositories;

use Database\Connection;
use PDO;

class EventRepository {
    private PDO $pdo;

    public function __construct() {
        $this->pdo = Connection::getInstance();
    }

    public function insert(int $deviceId, string $type, string $severity, int $ts): int {
        $stmt = $this->pdo->prepare("
            INSERT INTO events (device_id, type, severity, ts)
            VALUES (?, ?, ?, ?)
        ");
        $stmt->execute([$deviceId, $type, $severity, $ts]);
        return (int)$this->pdo->lastInsertId();
    }

    public function getAll(int $limit = 50): array {
        $stmt = $this->pdo->prepare("SELECT * FROM events ORDER BY created_at DESC LIMIT ?");
        $stmt->bindValue(1, $limit, PDO::PARAM_INT);
        $stmt->execute();
        return $stmt->fetchAll();
    }
}
<?php
namespace Repositories;

require_once __DIR__ . '/../Database/Connection.php';

use Database\Connection;
use PDO;

class DeviceRepository {
    private PDO $db;

    public function __construct() {
        $this->db = Connection::getInstance();
    }

    public function findByTokenHash(string $tokenHash): ?array {
        $stmt = $this->db->prepare("SELECT * FROM devices WHERE token_hash = ? LIMIT 1");
        $stmt->execute([$tokenHash]);
        $device = $stmt->fetch(PDO::FETCH_ASSOC);
        return $device ?: null;
    }

    public function findByNodeId(string $nodeId): ?array {
        $stmt = $this->db->prepare("SELECT * FROM devices WHERE node_id = ? LIMIT 1");
        $stmt->execute([$nodeId]);
        $device = $stmt->fetch(PDO::FETCH_ASSOC);
        return $device ?: null;
    }

    public function findById(int $id): ?array {
        $stmt = $this->db->prepare("SELECT * FROM devices WHERE id = ? LIMIT 1");
        $stmt->execute([$id]);
        $device = $stmt->fetch(PDO::FETCH_ASSOC);
        return $device ?: null;
    }

    public function touchLastSeen(int $id): void {
        $stmt = $this->db->prepare("UPDATE devices SET last_seen = NOW() WHERE id = ?");
        $stmt->execute([$id]);
    }

    public function getAll(): array {
        $stmt = $this->db->query("SELECT id, node_id, last_seen, created_at FROM devices ORDER BY id ASC");
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

CREATE DATABASE IF NOT EXISTS lab2_iot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lab2_iot;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS commands;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS telemetry;
DROP TABLE IF EXISTS configurations;
DROP TABLE IF EXISTS devices;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Tabla de Dispositivos (Manejo de Tokens Hasheados SHA-256)
CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id VARCHAR(50) NOT NULL UNIQUE,
    token_hash CHAR(64) NOT NULL,
    last_seen DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_devices_node (node_id),
    INDEX idx_devices_token (token_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Tabla de Configuraciones Dinámicas (UPSERT)
CREATE TABLE configurations (
    device_id INT PRIMARY KEY,
    sample_interval INT NOT NULL DEFAULT 5,
    threshold DECIMAL(5,2) NOT NULL DEFAULT 26.00,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Tabla de Telemetría (Idempotencia estricta por nodo y secuencia)
CREATE TABLE telemetry (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    seq INT NOT NULL,
    value DECIMAL(6,2) NOT NULL,
    rssi INT NOT NULL,
    ts BIGINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_device_seq UNIQUE KEY (device_id, seq),
    INDEX idx_telemetry_device_ts (device_id, ts),
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Tabla de Eventos y Alarmas
CREATE TABLE events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    severity ENUM('info', 'warning', 'critical') NOT NULL DEFAULT 'warning',
    ts BIGINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_events_device (device_id),
    INDEX idx_events_type_ts (type, ts),
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Sexto Endpoint: Comandos hacia Actuadores / Dispositivos
CREATE TABLE commands (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    command VARCHAR(100) NOT NULL,
    status ENUM('pending', 'sent', 'acknowledged') NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Datos Semilla (Tokens: secret-token-node01, secret-token-node02, secret-token-node03)
INSERT INTO devices (id, node_id, token_hash) VALUES
(1, 'ESP32_01', 'e22e9e68cbb0b81c4e9d6d5ef6383637e1df2ef22d194cf3f1e944b0559ebfd0'),
(2, 'ESP32_02', '52f8be0f9cb41a4a49c4f74d081f215f9b4fb797dc69a08e1a1cc0a66d8f8a18'),
(3, 'ESP32_03', '4e58f001efcf1de03bcfce91230bbd7a31ee44243e8bb51d1872df0d9fec9044');

INSERT INTO configurations (device_id, sample_interval, threshold) VALUES
(1, 5, 26.00),
(2, 5, 26.00),
(3, 5, 26.00);

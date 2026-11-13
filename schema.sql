-- =============================================================
-- Lab 2 - Backend IoT multi-nodo (repositorio lab2-iot-backend)
-- Esquema completo + carga inicial de datos de prueba
-- Motor: MariaDB 10.4 / MySQL 8 (InnoDB, utf8mb4)
-- Tablas identicas a SHOW CREATE TABLE de iot_platform_db (13/11/2026)
-- Uso: C:\xampp\mysql\bin\mysql.exe -u root < schema.sql   (o importar en phpMyAdmin)
-- =============================================================

-- Seguro de ejecutar sobre una base existente: no borra nada
-- (CREATE ... IF NOT EXISTS e INSERT IGNORE).
CREATE DATABASE IF NOT EXISTS iot_platform_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE iot_platform_db;

-- -------------------------------------------------------------
-- Dispositivos (un registro por nodo)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS devices (
  id int(11) NOT NULL AUTO_INCREMENT,
  node_id varchar(50) NOT NULL,
  token_hash varchar(64) NOT NULL,
  status enum('online','offline','unknown') DEFAULT 'offline',
  last_seen datetime DEFAULT NULL,
  created_at datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  UNIQUE KEY node_id (node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- -------------------------------------------------------------
-- Telemetria (idempotencia por device_id + seq; indice para historico)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS telemetry (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  device_id int(11) NOT NULL,
  seq int(11) NOT NULL,
  value decimal(6,2) NOT NULL,
  rssi int(11) DEFAULT NULL,
  ts int(11) NOT NULL,
  created_at datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  UNIQUE KEY uq_device_seq (device_id, seq),
  KEY idx_telemetry_device_ts (device_id, ts),
  CONSTRAINT fk_telemetry_device FOREIGN KEY (device_id)
    REFERENCES devices (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- -------------------------------------------------------------
-- Eventos / alarmas
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS events (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  device_id int(11) NOT NULL,
  type varchar(50) NOT NULL,
  severity enum('info','warning','critical') NOT NULL,
  ts int(11) NOT NULL,
  created_at datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  KEY fk_events_device (device_id),
  CONSTRAINT fk_events_device FOREIGN KEY (device_id)
    REFERENCES devices (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- -------------------------------------------------------------
-- Configuracion por dispositivo
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS configurations (
  id int(11) NOT NULL AUTO_INCREMENT,
  device_id int(11) NOT NULL,
  threshold decimal(5,2) NOT NULL DEFAULT 26.00,
  sample_interval int(11) NOT NULL DEFAULT 10,
  created_at datetime NOT NULL DEFAULT current_timestamp(),
  updated_at datetime NOT NULL DEFAULT current_timestamp()
    ON UPDATE current_timestamp(),
  PRIMARY KEY (id),
  UNIQUE KEY device_id (device_id),
  CONSTRAINT fk_configurations_device FOREIGN KEY (device_id)
    REFERENCES devices (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- -------------------------------------------------------------
-- Comandos a actuadores
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS commands (
  id bigint(20) NOT NULL AUTO_INCREMENT,
  device_id int(11) NOT NULL,
  command varchar(100) NOT NULL,
  status enum('pending','sent','acknowledged') NOT NULL DEFAULT 'pending',
  created_at datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  KEY fk_commands_device (device_id),
  CONSTRAINT fk_commands_device FOREIGN KEY (device_id)
    REFERENCES devices (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- =============================================================
-- CARGA INICIAL (datos de prueba)
-- =============================================================
-- token_hash = SHA-256 del token que usan las pruebas:
--   ESP32_01 -> secret-token-node01, ESP32_02 -> secret-token-node02, ESP32_03 -> secret-token-node03
INSERT IGNORE INTO devices (id, node_id, token_hash, status) VALUES
  (1, 'ESP32_01', 'cf178ac8be1e1278ddb679d3927481baad5c3c5a8d8b26bf1192b98751b43226', 'offline'),
  (2, 'ESP32_02', 'cda30091c50e8fc5e1d9cd63f5920c235dec43e18aacaedff58d80b710750ad6', 'offline'),
  (3, 'ESP32_03', 'aa6780df39005da233514aeb7e152ee3c643d83b5000ef266be8b462b720352d', 'offline');

INSERT IGNORE INTO configurations (device_id, threshold, sample_interval) VALUES
  (1, 26.00, 10),
  (2, 26.00, 10),
  (3, 26.00, 10);

-- Unas lecturas de ejemplo (ts en epoch; seq por nodo)
INSERT IGNORE INTO telemetry (device_id, ts, value, rssi, seq) VALUES
  (1, 1793980000, 22.85, -46, 1),
  (1, 1793980010, 23.10, -48, 2),
  (2, 1793980000, 24.41, -55, 1),
  (2, 1793980010, 24.96, -45, 2),
  (3, 1793980000, 26.40, -41, 1),
  (3, 1793980010, 27.13, -49, 2);

-- Eventos coherentes con las lecturas > 26.00 de ESP32_03
-- (events no tiene clave unica: si se ejecuta dos veces, estos 2 eventos se repiten)
INSERT IGNORE INTO events (device_id, type, severity, ts) VALUES
  (3, 'temp_high', 'warning', 1793980000),
  (3, 'temp_high', 'warning', 1793980010);

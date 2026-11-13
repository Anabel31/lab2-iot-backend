-- =============================================================
-- Lab 2 - Backend IoT multi-nodo
-- Esquema completo + carga inicial de datos de prueba
-- Motor: MariaDB 10.4 / MySQL 8 (InnoDB, utf8mb4)
-- Uso: mysql -u root < database/schema.sql   (o importar en phpMyAdmin)
-- =============================================================

DROP DATABASE IF EXISTS lab2_iot;
CREATE DATABASE lab2_iot CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE lab2_iot;

-- -------------------------------------------------------------
-- Dispositivos (un registro por nodo)
-- -------------------------------------------------------------
CREATE TABLE devices (
  id         INT(11)      NOT NULL AUTO_INCREMENT,
  node_id    VARCHAR(50)  NOT NULL,
  token      VARCHAR(64)  NOT NULL,
  status     ENUM('online','offline','unknown') DEFAULT 'offline',
  last_seen  DATETIME     DEFAULT NULL,
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY node_id (node_id)
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- Telemetria (idempotencia por device_id + seq)
-- -------------------------------------------------------------
CREATE TABLE telemetry (
  id         BIGINT       NOT NULL AUTO_INCREMENT,
  device_id  INT          NOT NULL,
  ts         BIGINT       NOT NULL,
  value      DECIMAL(5,2) NOT NULL,
  rssi       INT          NOT NULL,
  seq        INT          NOT NULL,
  created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_device_seq (device_id, seq),
  KEY idx_telemetry_device_ts (device_id, ts),
  CONSTRAINT fk_telemetry_device FOREIGN KEY (device_id)
    REFERENCES devices (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- Eventos / alarmas
-- -------------------------------------------------------------
CREATE TABLE events (
  id         BIGINT(20)   NOT NULL AUTO_INCREMENT,
  device_id  INT(11)      NOT NULL,
  event_type VARCHAR(50)  NOT NULL,
  severity   ENUM('info','warning','critical') NOT NULL,
  ts         INT(11)      NOT NULL,
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY device_id (device_id),
  CONSTRAINT fk_events_device FOREIGN KEY (device_id)
    REFERENCES devices (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- Configuracion por dispositivo
-- -------------------------------------------------------------
CREATE TABLE configurations (
  id                INT(11)      NOT NULL AUTO_INCREMENT,
  device_id         INT(11)      NOT NULL,
  threshold         DECIMAL(5,2) NOT NULL DEFAULT 26.00,
  sampling_interval INT(11)      NOT NULL DEFAULT 10,
  created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                 ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY device_id (device_id),
  CONSTRAINT fk_configurations_device FOREIGN KEY (device_id)
    REFERENCES devices (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------------
-- Comandos a actuadores
-- -------------------------------------------------------------
CREATE TABLE commands (
  id         BIGINT(20)   NOT NULL AUTO_INCREMENT,
  device_id  INT(11)      NOT NULL,
  command    VARCHAR(100) NOT NULL,
  status     ENUM('pending','sent','acknowledged') NOT NULL DEFAULT 'pending',
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY device_id (device_id),
  CONSTRAINT fk_commands_device FOREIGN KEY (device_id)
    REFERENCES devices (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================
-- CARGA INICIAL (datos de prueba)
-- IMPORTANTE: reemplacen los tokens por los que usan sus scripts
-- (run_tests.ps1, simulador_nodos.py) para que las pruebas sigan pasando.
-- =============================================================
INSERT INTO devices (id, node_id, token, status) VALUES
  (1, 'ESP32_01', 'TOKEN_ESP32_01', 'offline'),
  (2, 'ESP32_02', 'TOKEN_ESP32_02', 'offline'),
  (3, 'ESP32_03', 'TOKEN_ESP32_03', 'offline');

INSERT INTO configurations (device_id, threshold, sampling_interval) VALUES
  (1, 26.00, 10),
  (2, 26.00, 10),
  (3, 26.00, 10);

-- Unas lecturas de ejemplo (ts en epoch; seq por nodo)
INSERT INTO telemetry (device_id, ts, value, rssi, seq) VALUES
  (1, 1793980000, 22.85, -46, 1),
  (1, 1793980010, 23.10, -48, 2),
  (2, 1793980000, 24.41, -55, 1),
  (2, 1793980010, 24.96, -45, 2),
  (3, 1793980000, 26.40, -41, 1),
  (3, 1793980010, 27.13, -49, 2);

-- Eventos coherentes con las lecturas > 26.00 de ESP32_03
INSERT INTO events (device_id, event_type, severity, ts) VALUES
  (3, 'temp_high', 'warning', 1793980000),
  (3, 'temp_high', 'warning', 1793980010);

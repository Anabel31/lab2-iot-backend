-- Exportacion tablas Lab 2: devices, events, configurations, commands
SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_id` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `token_hash` varchar(255) NOT NULL,
  `last_seen` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `node_id` (`node_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `devices` (`id`, `node_id`, `name`, `token_hash`, `last_seen`, `created_at`) VALUES ('1', 'ESP32_01', 'Nodo Laboratorio 101', 'cf178ac8be1e1278ddb679d3927481baad5c3c5a8d8b26bf1192b98751b43226', '2026-11-06 12:32:41', '2026-10-16 20:11:17');
INSERT INTO `devices` (`id`, `node_id`, `name`, `token_hash`, `last_seen`, `created_at`) VALUES ('2', 'ESP32_02', 'Nodo Laboratorio 102', 'cda30091c50e8fc5e1d9cd63f5920c235dec43e18aacaedff58d80b710750ad6', '2026-11-06 11:19:46', '2026-10-16 20:11:17');
INSERT INTO `devices` (`id`, `node_id`, `name`, `token_hash`, `last_seen`, `created_at`) VALUES ('3', 'ESP32_03', 'Nodo Pasillo Central', 'aa6780df39005da233514aeb7e152ee3c643d83b5000ef266be8b462b720352d', '2026-11-06 11:19:47', '2026-10-16 20:11:17');

DROP TABLE IF EXISTS `events`;
CREATE TABLE `events` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `type` varchar(50) NOT NULL,
  `severity` enum('info','warning','critical') DEFAULT 'info',
  `ts` bigint(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_events_device` (`device_id`),
  CONSTRAINT `fk_events_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `events` (`id`, `device_id`, `type`, `severity`, `ts`, `created_at`) VALUES ('1', '3', 'temp_high', 'warning', '1793981982', '2026-11-06 11:19:42');
INSERT INTO `events` (`id`, `device_id`, `type`, `severity`, `ts`, `created_at`) VALUES ('2', '3', 'temp_high', 'warning', '1793981982', '2026-11-06 11:19:43');
INSERT INTO `events` (`id`, `device_id`, `type`, `severity`, `ts`, `created_at`) VALUES ('3', '3', 'temp_high', 'warning', '1793981983', '2026-11-06 11:19:43');
INSERT INTO `events` (`id`, `device_id`, `type`, `severity`, `ts`, `created_at`) VALUES ('4', '3', 'temp_high', 'warning', '1793981984', '2026-11-06 11:19:44');
INSERT INTO `events` (`id`, `device_id`, `type`, `severity`, `ts`, `created_at`) VALUES ('5', '3', 'temp_high', 'warning', '1793981986', '2026-11-06 11:19:46');
INSERT INTO `events` (`id`, `device_id`, `type`, `severity`, `ts`, `created_at`) VALUES ('6', '3', 'temp_high', 'warning', '1793981987', '2026-11-06 11:19:47');

DROP TABLE IF EXISTS `configurations`;
CREATE TABLE `configurations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `key` varchar(50) NOT NULL,
  `value` varchar(100) NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_device_key` (`device_id`,`key`),
  CONSTRAINT `fk_configurations_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `configurations` (`id`, `device_id`, `key`, `value`, `updated_at`) VALUES ('1', '1', 'temp_threshold', '22.0', '2026-10-16 20:11:17');
INSERT INTO `configurations` (`id`, `device_id`, `key`, `value`, `updated_at`) VALUES ('2', '1', 'sample_interval_s', '10', '2026-10-16 20:11:17');
INSERT INTO `configurations` (`id`, `device_id`, `key`, `value`, `updated_at`) VALUES ('3', '2', 'temp_threshold', '24.0', '2026-10-16 20:11:17');
INSERT INTO `configurations` (`id`, `device_id`, `key`, `value`, `updated_at`) VALUES ('4', '2', 'sample_interval_s', '10', '2026-10-16 20:11:17');
INSERT INTO `configurations` (`id`, `device_id`, `key`, `value`, `updated_at`) VALUES ('5', '3', 'temp_threshold', '25.0', '2026-10-16 20:11:17');
INSERT INTO `configurations` (`id`, `device_id`, `key`, `value`, `updated_at`) VALUES ('6', '3', 'sample_interval_s', '5', '2026-10-16 20:11:17');
INSERT INTO `configurations` (`id`, `device_id`, `key`, `value`, `updated_at`) VALUES ('7', '1', 'sample_interval', '5', '2026-10-30 15:44:59');
INSERT INTO `configurations` (`id`, `device_id`, `key`, `value`, `updated_at`) VALUES ('8', '1', 'threshold', '26', '2026-10-30 15:44:59');

DROP TABLE IF EXISTS `commands`;
CREATE TABLE `commands` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `command` varchar(100) NOT NULL,
  `status` enum('pending','sent','acknowledged') NOT NULL DEFAULT 'pending',
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `device_id` (`device_id`),
  CONSTRAINT `commands_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `commands` (`id`, `device_id`, `command`, `status`, `created_at`) VALUES ('1', '1', 'SET_RELAY_ON', 'pending', '2026-11-06 11:07:50');
INSERT INTO `commands` (`id`, `device_id`, `command`, `status`, `created_at`) VALUES ('2', '1', 'SET_RELAY_ON', 'pending', '2026-11-06 11:23:04');
INSERT INTO `commands` (`id`, `device_id`, `command`, `status`, `created_at`) VALUES ('3', '1', 'SET_RELAY_ON', 'pending', '2026-11-06 12:31:29');

SET FOREIGN_KEY_CHECKS=1;

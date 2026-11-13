<?php
// config/app.php

return [
    'db' => [
        'host' => '127.0.0.1',
        'port' => 3306,
        'database' => 'iot_platform_db',
        'username' => 'root',
        'password' => '', // En XAMPP la contraseña por defecto siempre está vacía
        'charset' => 'utf8mb4'
    ],
    'api' => [
        'version' => 'v1'
    ]
];
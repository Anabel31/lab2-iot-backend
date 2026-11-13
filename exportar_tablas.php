<?php
$host = '127.0.0.1';
$db   = 'iot_platform_db';
$user = 'root';
$pass = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
} catch (Exception $e) {
    die("Error conectando a MySQL: " . $e->getMessage() . "\n");
}

$tables = ['devices', 'events', 'configurations', 'commands'];
$sqlDump = "-- Exportacion tablas Lab 2: devices, events, configurations, commands\n";
$sqlDump .= "SET FOREIGN_KEY_CHECKS=0;\n\n";

foreach ($tables as $table) {
    echo "Exportando tabla: $table ...\n";
    
    // Obtener estructura CREATE TABLE
    $stmt = $pdo->query("SHOW CREATE TABLE `$table`");
    $row = $stmt->fetch();
    $sqlDump .= "DROP TABLE IF EXISTS `$table`;\n";
    $sqlDump .= $row['Create Table'] . ";\n\n";
    
    // Obtener datos
    $stmtData = $pdo->query("SELECT * FROM `$table`");
    $rows = $stmtData->fetchAll();
    
    if (count($rows) > 0) {
        $cols = array_keys($rows[0]);
        $colNames = implode('`, `', $cols);
        
        foreach ($rows as $r) {
            $vals = array_map(function($v) use ($pdo) {
                if ($v === null) return 'NULL';
                return $pdo->quote($v);
            }, array_values($r));
            
            $valList = implode(', ', $vals);
            $sqlDump .= "INSERT INTO `$table` (`$colNames`) VALUES ($valList);\n";
        }
        $sqlDump .= "\n";
    }
}

$sqlDump .= "SET FOREIGN_KEY_CHECKS=1;\n";

$outFile = __DIR__ . '/export_tablas_lab2.sql';
file_put_contents($outFile, $sqlDump);
echo "[+] Exportacion completada con exito en: $outFile\n";

$base = "http://localhost/lab2-backend/public/api/v1"
$seq  = [int][DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

function Post($token, $obj) {
    $f = New-TemporaryFile
    ($obj | ConvertTo-Json -Compress) | Set-Content -Path $f -Encoding ascii
    $code = curl.exe -s -o NUL -w "%{http_code}" -X POST "$base/telemetry" `
        -H "Content-Type: application/json" -H "Authorization: Bearer $token" --data-binary "@$f"
    Remove-Item $f
    return $code
}
function Get-Code($path) { curl.exe -s -o NUL -w "%{http_code}" "$base$path" }
function Check($name, $expected, $got) {
    if ("$got" -eq "$expected") { Write-Host "OK     $name ($got)" -ForegroundColor Green }
    else { Write-Host "FALLO  $name (esperado $expected, obtenido $got)" -ForegroundColor Red }
}

$ok = @{node_id="ESP32_01"; seq=$seq; value=24.2; rssi=-45; ts=1791480000}
Check "T01 POST valido"          201 (Post "secret-token-node01" $ok)
Check "T04 duplicado"            409 (Post "secret-token-node01" $ok)
Check "T02 token invalido"       401 (Post "token-falso" @{node_id="ESP32_01"; seq=$seq+1; value=24.2; rssi=-45; ts=1791480000})
Check "T03 falta value"          422 (Post "secret-token-node01" @{node_id="ESP32_01"; seq=$seq+2; rssi=-45; ts=1791480000})
Check "403 token de otro nodo"   403 (Post "secret-token-node01" @{node_id="ESP32_02"; seq=$seq+3; value=24.2; rssi=-45; ts=1791480000})
Check "GET /devices"             200 (Get-Code "/devices")
Check "GET telemetry"            200 (Get-Code "/devices/1/telemetry?limit=5")
Check "GET telemetry inexistente" 404 (Get-Code "/devices/999/telemetry")
Check "GET /events"              200 (Get-Code "/events")
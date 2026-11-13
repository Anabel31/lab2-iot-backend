$BASE  = "http://127.0.0.1:8080/lab2-backend/public/api/v1"
$ADMIN = "admin-token-lab2"

function Probar($nombre, $metodo, $url, $json, $token, $esperado) {
    $tmp = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($tmp, $json)
    
    $argsCurl = @("-s", "-w", "%{http_code}", "-o", "$tmp.out", "-X", $metodo, $url, "-H", "Content-Type: application/json", "--data-binary", "@$tmp")
    if ($token) { $argsCurl += @("-H", "Authorization: Bearer $token") }
    
    $codigo = & curl.exe @argsCurl
    $cuerpo = if (Test-Path "$tmp.out") { Get-Content "$tmp.out" -Raw } else { "" }
    Remove-Item $tmp, "$tmp.out" -ErrorAction SilentlyContinue

    $estado = if ("$codigo" -eq "$esperado") { "OK  " } else { "FALLA" }
    $color  = if ($estado -eq "OK  ") { "Green" } else { "Red" }
    Write-Host ("{0}  {1,-48} esperado {2} -> obtenido {3}" -f $estado, $nombre, $esperado, $codigo) -ForegroundColor $color
    Write-Host ("      " + $cuerpo) -ForegroundColor DarkGray
}

Write-Host "`n=== Modularidad: SQL dentro de public/index.php (no deberia salir nada) ===" -ForegroundColor Cyan
Select-String -Path ".\public\index.php" -Pattern "\b(SELECT|INSERT|DELETE|FROM|WHERE)\b"

Write-Host "`n=== T13: PUT /devices/1/config ===" -ForegroundColor Cyan
Probar "T13a PUT config con token admin" "PUT" "$BASE/devices/1/config" '{"threshold":27.5,"sample_interval":15}' $ADMIN 200
Probar "T13b PUT config sin token" "PUT" "$BASE/devices/1/config" '{"threshold":27.5,"sample_interval":15}' "" 401

Write-Host "`n=== T15: POST /devices/1/commands ===" -ForegroundColor Cyan
Probar "T15a POST commands sin token" "POST" "$BASE/devices/1/commands" '{"command":"SET_RELAY_ON"}' "" 401
Probar "T15b POST commands con token admin" "POST" "$BASE/devices/1/commands" '{"command":"SET_RELAY_ON"}' $ADMIN 201

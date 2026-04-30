
# scan_utf8.ps1 — Encontra e corrige arquivos com encoding invalido (nao-UTF-8)

$root = "H:\SISTEMA JUVIX SERVER - Copia\SISTEMA LIMPO - ESTAVEL"
$extensions = @("*.py", "*.json", "*.html", "*.txt", "*.key", "*.cfg", "*.ini", "*.bat")
$enc1252 = [System.Text.Encoding]::GetEncoding('windows-1252')
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

$found = 0

foreach ($ext in $extensions) {
    $files = Get-ChildItem -Path $root -Recurse -Include $ext -ErrorAction SilentlyContinue |
             Where-Object { $_.FullName -notlike "*\venv\*" -and $_.FullName -notlike "*\__pycache__\*" }

    foreach ($file in $files) {
        try {
            $bytes = [System.IO.File]::ReadAllBytes($file.FullName)

            # Tenta decodificar como UTF-8 estrito
            $isValid = $true
            try {
                $decoder = [System.Text.Encoding]::UTF8.GetDecoder()
                $decoder.Fallback = [System.Text.DecoderExceptionFallback]::new()
                $chars = New-Object char[] ($bytes.Length)
                $null = $decoder.GetChars($bytes, 0, $bytes.Length, $chars, 0)
            } catch {
                $isValid = $false
            }

            if (-not $isValid) {
                $found++
                Write-Host ""
                Write-Host ">>> INVALIDO: $($file.FullName)" -ForegroundColor Red

                # Converte de Windows-1252 para UTF-8 sem BOM
                $text = $enc1252.GetString($bytes)
                [System.IO.File]::WriteAllText($file.FullName, $text, $utf8NoBom)
                Write-Host "    -> CONVERTIDO para UTF-8!" -ForegroundColor Green
            }
        } catch {
            Write-Host "ERRO ao processar $($file.FullName): $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
if ($found -eq 0) {
    Write-Host "=== Nenhum arquivo invalido encontrado. Todos sao UTF-8 valido! ===" -ForegroundColor Cyan
} else {
    Write-Host "=== $found arquivo(s) corrigido(s)! ===" -ForegroundColor Green
}

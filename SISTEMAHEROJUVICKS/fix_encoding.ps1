
# fix_encoding.ps1 — Converte arquivos py/json/html para UTF-8 sem BOM
$root = $PSScriptRoot
$extensions = @("*.py", "*.json", "*.html")
$enc1252 = [System.Text.Encoding]::GetEncoding('windows-1252')
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

foreach ($ext in $extensions) {
    $files = Get-ChildItem -Path $root -Recurse -Include $ext
    foreach ($file in $files) {
        try {
            $bytes = [System.IO.File]::ReadAllBytes($file.FullName)

            # Detecta se já é UTF-8 (BOM ou ASCII puro)
            $isUtf8BOM = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)

            # Tenta decodificar como UTF-8 estrito
            $utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)
            $isValidUtf8 = $true
            try {
                $null = $utf8Strict.GetString($bytes)
            } catch {
                $isValidUtf8 = $false
            }

            if (-not $isValidUtf8) {
                # Arquivo tem bytes inválidos para UTF-8 → relê como cp1252 e salva UTF-8
                $text = $enc1252.GetString($bytes)
                [System.IO.File]::WriteAllText($file.FullName, $text, $utf8NoBom)
                Write-Host "CONVERTIDO: $($file.FullName)" -ForegroundColor Green
            } elseif ($isUtf8BOM) {
                # Remove BOM desnecessário
                $text = [System.Text.Encoding]::UTF8.GetString($bytes)
                [System.IO.File]::WriteAllText($file.FullName, $text, $utf8NoBom)
                Write-Host "BOM removido: $($file.FullName)" -ForegroundColor Yellow
            } else {
                Write-Host "OK (UTF-8): $($file.FullName)" -ForegroundColor DarkGray
            }
        } catch {
            Write-Host "ERRO em $($file.FullName): $_" -ForegroundColor Red
        }
    }
}

Write-Host "`n=== Conversao concluida! ===" -ForegroundColor Cyan

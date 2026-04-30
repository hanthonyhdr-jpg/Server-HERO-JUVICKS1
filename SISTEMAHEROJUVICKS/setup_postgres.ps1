
# setup_postgres.ps1
# Configura o banco de dados PostgreSQL para o JUVIKS HERO SaaS

$pgBin = "C:\Program Files\PostgreSQL\18\bin"
$psql = "$pgBin\psql.exe"
$pgPass = $env:PGPASSWORD

# Detecta a senha do postgres — tenta variável de ambiente, senão usa senhas comuns
$senhasComuns = @("postgres", "admin", "1234", "root", "postgres123", "")

function Try-Connect($senha) {
    $env:PGPASSWORD = $senha
    $result = & $psql -U postgres -h localhost -p 5432 -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) { return $true }
    return $false
}

Write-Host "=== JUVIKS: Testando acesso ao PostgreSQL ===" -ForegroundColor Cyan

$senhaPostgres = $null
foreach ($s in $senhasComuns) {
    Write-Host "Testando senha: '$s' ..." -ForegroundColor DarkGray
    if (Try-Connect $s) {
        $senhaPostgres = $s
        Write-Host "Senha do superusuario postgres encontrada: '$s'" -ForegroundColor Green
        break
    }
}

if ($null -eq $senhaPostgres) {
    Write-Host ""
    Write-Host "ATENCAO: Nenhuma senha automatica funcionou." -ForegroundColor Red
    Write-Host "Por favor, informe a senha do usuario 'postgres' do PostgreSQL:" -ForegroundColor Yellow
    $senhaPostgres = Read-Host -Prompt "Senha do postgres"
    $env:PGPASSWORD = $senhaPostgres
    if (-not (Try-Connect $senhaPostgres)) {
        Write-Host "Senha incorreta. Abortando." -ForegroundColor Red
        exit 1
    }
}

$env:PGPASSWORD = $senhaPostgres

Write-Host ""
Write-Host "=== Criando usuario juviks_admin e banco juviks_saas ===" -ForegroundColor Cyan

# SQL para criar usuario e banco
$sql = @"
DO `$`$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'juviks_admin') THEN
        CREATE USER juviks_admin WITH PASSWORD 'JuviksHero2026';
        RAISE NOTICE 'Usuario juviks_admin criado.';
    ELSE
        ALTER USER juviks_admin WITH PASSWORD 'JuviksHero2026';
        RAISE NOTICE 'Senha do usuario juviks_admin atualizada.';
    END IF;
END
`$`$;
"@

& $psql -U postgres -h localhost -p 5432 -c $sql
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao criar usuario." -ForegroundColor Red
    exit 1
}

# Criar banco
& $psql -U postgres -h localhost -p 5432 -c "SELECT 1 FROM pg_database WHERE datname = 'juviks_saas';" | Out-Null
$dbExists = & $psql -U postgres -h localhost -p 5432 -t -c "SELECT COUNT(*) FROM pg_database WHERE datname = 'juviks_saas';"
if ($dbExists.Trim() -eq "0") {
    & $psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE juviks_saas OWNER juviks_admin ENCODING 'UTF8' LC_COLLATE 'Portuguese_Brazil.1252' LC_CTYPE 'Portuguese_Brazil.1252' TEMPLATE template0;"
    if ($LASTEXITCODE -ne 0) {
        # Tenta sem locale especifico
        & $psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE juviks_saas OWNER juviks_admin ENCODING 'UTF8';"
    }
    Write-Host "Banco juviks_saas criado!" -ForegroundColor Green
} else {
    Write-Host "Banco juviks_saas ja existe." -ForegroundColor Yellow
}

# Dar privilegios
& $psql -U postgres -h localhost -p 5432 -d juviks_saas -c "GRANT ALL PRIVILEGES ON DATABASE juviks_saas TO juviks_admin;"
& $psql -U postgres -h localhost -p 5432 -d juviks_saas -c "GRANT ALL ON SCHEMA public TO juviks_admin;"
& $psql -U postgres -h localhost -p 5432 -d juviks_saas -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO juviks_admin;"

Write-Host ""
Write-Host "=== Testando conexao com juviks_admin ===" -ForegroundColor Cyan
$env:PGPASSWORD = "JuviksHero2026"
$test = & $psql -U juviks_admin -h localhost -p 5432 -d juviks_saas -c "SELECT current_user, current_database();" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCESSO! Conexao com juviks_admin funcionando!" -ForegroundColor Green
    Write-Host $test
} else {
    Write-Host "Erro ao conectar com juviks_admin:" -ForegroundColor Red
    Write-Host $test
    exit 1
}

# Atualiza o db_config.json
$configPath = "h:\SISTEMA JUVIX SERVER - Copia\SISTEMA LIMPO - ESTAVEL\CONFIG_SISTEMA\db_config.json"
$config = @{
    engine           = "postgresql"
    host             = "localhost"
    port             = 5432
    database         = "juviks_saas"
    user             = "juviks_admin"
    password         = "JuviksHero2026"
    fallback_sqlite  = $true
    connect_timeout  = 5
}
$config | ConvertTo-Json -Depth 5 | Out-File -FilePath $configPath -Encoding UTF8NoBOM
Write-Host ""
Write-Host "=== db_config.json atualizado! ===" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " CONFIGURACAO CONCLUIDA!" -ForegroundColor Green
Write-Host " Usuario : juviks_admin" -ForegroundColor White
Write-Host " Senha   : JuviksHero2026" -ForegroundColor White
Write-Host " Banco   : juviks_saas" -ForegroundColor White
Write-Host " Host    : localhost:5432" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan

# Script de instalación automática para Windows PowerShell
# Autor: SISTEMAS MV v2.0
# Ubicación: C:\Users\Sistemas\Documents\pagos\install.ps1
# 
# Ejecución: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  SISTEMAS MV v2.0 - Instalación Windows" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Función para mostrar errores
function Show-Error {
    param([string]$message)
    Write-Host "[ERROR] $message" -ForegroundColor Red
    Write-Host ""
}

# Función para mostrar éxito
function Show-Success {
    param([string]$message)
    Write-Host "[OK] $message" -ForegroundColor Green
}

# Función para mostrar paso
function Show-Step {
    param([int]$step, [string]$message)
    Write-Host "[$step/5] $message" -ForegroundColor Yellow
}

# 1. Verificar Python
Show-Step 1 "Verificando Python..."
try {
    $pythonVersion = python --version 2>&1
    Show-Success "Python detectado: $pythonVersion"
} catch {
    Show-Error "Python no encontrado en PATH"
    Write-Host ""
    Write-Host "Soluciones:" -ForegroundColor Yellow
    Write-Host "1. Descarga Python desde python.org"
    Write-Host "2. Marca la opción 'Add Python to PATH'"
    Write-Host "3. Reinicia PowerShell"
    Write-Host ""
    Read-Host "Presiona ENTER para salir"
    exit 1
}

Write-Host ""

# 2. Actualizar pip
Show-Step 2 "Actualizando pip, wheel y setuptools..."
try {
    python -m pip install --upgrade pip wheel setuptools -q
    Show-Success "pip/wheel/setuptools actualizados"
} catch {
    Show-Error "Error actualizando pip"
    Read-Host "Presiona ENTER para salir"
    exit 1
}

Write-Host ""

# 3. Limpiar caché
Show-Step 3 "Limpiando caché pip..."
try {
    pip cache purge -q 2>$null
    Show-Success "Caché limpio"
} catch {
    Write-Host "[WARN] No se pudo limpiar caché (ignorado)" -ForegroundColor Yellow
}

Write-Host ""

# 4. Instalar librerías
Show-Step 4 "Instalando librerías (sin compilador necesario)..."
Write-Host "Esto puede tardar 3-5 minutos..." -ForegroundColor Cyan
Write-Host ""

$packages = @(
    "Flask==3.0.0",
    "Flask-WTF==1.2.1",
    "Flask-Limiter==3.5.0",
    "psycopg2-binary==2.9.9",
    "cryptography==41.0.7",
    "Werkzeug==3.0.1",
    "python-dotenv==1.0.0",
    "pytz==2023.3",
    "openpyxl==3.1.2",
    "pandas==2.0.3"
)

$installed = 0
foreach ($package in $packages) {
    $installed++
    $total = $packages.Count
    Write-Host "  [$installed/$total] Instalando $package..." -ForegroundColor Gray
    
    try {
        pip install --only-binary :all: $package -q 2>&1 | Out-Null
    } catch {
        Show-Error "Error instalando $package"
        Read-Host "Presiona ENTER para salir"
        exit 1
    }
}

Show-Success "Todas las librerías instaladas"
Write-Host ""

# 5. Verificar instalación
Show-Step 5 "Verificando instalación..."
try {
    $verification = python -c "import flask, psycopg2, cryptography, pandas; print('OK')" 2>&1
    if ($verification -eq "OK") {
        Show-Success "Verificación exitosa - todas las librerías importan correctamente"
    } else {
        Show-Error "Verificación fallida"
        Read-Host "Presiona ENTER para salir"
        exit 1
    }
} catch {
    Show-Error "Error en verificación: $_"
    Read-Host "Presiona ENTER para salir"
    exit 1
}

Write-Host ""
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  ✅ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Generar secretos:" -ForegroundColor White
Write-Host "   python generate_secrets.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Editar configuración:" -ForegroundColor White
Write-Host "   notepad .env" -ForegroundColor Yellow
Write-Host "   (Completar: DB_HOST, DB_USER, DB_PASS)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Ejecutar aplicación:" -ForegroundColor White
Write-Host "   python app_seguro.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Acceder a:" -ForegroundColor White
Write-Host "   http://localhost" -ForegroundColor Yellow
Write-Host ""
Read-Host "Presiona ENTER para cerrar"
exit 0

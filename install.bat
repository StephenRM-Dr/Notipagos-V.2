@echo off
REM Script de instalación automática para Windows
REM Autor: SISTEMAS MV v2.0
REM Ubicación: C:\Users\Sistemas\Documents\pagos\install.bat

echo.
echo =========================================
echo   SISTEMAS MV v2.0 - Instalación Windows
echo =========================================
echo.

REM Detectar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado en PATH
    echo.
    echo Soluciones:
    echo 1. Instala Python desde python.org
    echo 2. Marca la opción "Add Python to PATH"
    echo 3. Reinicia esta ventana
    pause
    exit /b 1
)

echo [1/5] Verificando Python...
python --version
echo [OK] Python detectado
echo.

echo [2/5] Actualizando pip, wheel y setuptools...
python -m pip install --upgrade pip wheel setuptools
echo [OK] pip/wheel/setuptools actualizados
echo.

echo [3/5] Limpiando caché pip...
pip cache purge
echo [OK] Caché limpio
echo.

echo [4/5] Instalando librerías (sin compilador necesario)...
echo Esto puede tardar 3-5 minutos...
echo.

REM Instalar con --only-binary para evitar compilación
pip install --only-binary :all: Flask==3.0.0 || goto error
pip install --only-binary :all: Flask-WTF==1.2.1 || goto error
pip install --only-binary :all: Flask-Limiter==3.5.0 || goto error
pip install --only-binary :all: psycopg2-binary==2.9.9 || goto error
pip install --only-binary :all: cryptography==41.0.7 || goto error
pip install --only-binary :all: Werkzeug==3.0.1 || goto error
pip install --only-binary :all: python-dotenv==1.0.0 || goto error
pip install --only-binary :all: pytz==2023.3 || goto error
pip install --only-binary :all: openpyxl==3.1.2 || goto error
pip install --only-binary :all: pandas==2.0.3 || goto error

echo [OK] Todas las librerías instaladas
echo.

echo [5/5] Verificando instalación...
python -c "import flask, psycopg2, cryptography, pandas; print('OK: Todas las librerías importan correctamente')"
if %errorlevel% neq 0 (
    echo [ERROR] Verificación fallida
    goto error
)
echo [OK] Verificación exitosa
echo.

echo.
echo =========================================
echo   ✅ INSTALACIÓN COMPLETADA
echo =========================================
echo.
echo Próximos pasos:
echo.
echo 1. Generar secretos:
echo    python generate_secrets.py
echo.
echo 2. Editar configuración:
echo    notepad .env
echo    (Completar: DB_HOST, DB_USER, DB_PASS)
echo.
echo 3. Ejecutar aplicación:
echo    python app_seguro.py
echo.
echo 4. Acceder a:
echo    http://localhost
echo.
pause
exit /b 0

:error
echo.
echo =========================================
echo   ❌ ERROR EN LA INSTALACIÓN
echo =========================================
echo.
echo El error anterior es lo que causó el problema.
echo.
echo Opciones:
echo.
echo 1. Si dice "wheel" o "compiler":
echo    - Tu Windows no tiene compilador C++
echo    - Descarga Python 3.11 (no 3.13)
echo    - O instala: Anaconda
echo    - O instala: Microsoft C++ Build Tools
echo.
echo 2. Si dice "Network":
echo    - Verifica tu conexión a internet
echo    - Intenta de nuevo
echo.
echo 3. Si nada funciona:
echo    - Abre: SOLUCION_DEFINITIVA.md
echo    - Lee las opciones detalladas
echo.
pause
exit /b 1

#!/bin/bash
# Script de despliegue seguro - SISTEMAS MV v2.0

set -e  # Salir si hay error

echo "================================"
echo "🚀 DEPLOY SEGURO - SISTEMAS MV"
echo "================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Verificar que estamos en el directorio correcto
echo ""
echo "1️⃣  Verificando estructura..."
[[ -f "app_seguro.py" ]] || log_error "app_seguro.py no encontrado"
[[ -f "requirements.txt" ]] || log_error "requirements.txt no encontrado"
[[ -f ".env.example" ]] || log_error ".env.example no encontrado"
log_success "Estructura de archivos OK"

# 2. Verificar .env
echo ""
echo "2️⃣  Verificando configuración..."
if [[ ! -f ".env" ]]; then
    log_error "Archivo .env no existe. Copia desde .env.example y completa los valores"
fi

# Validar que .env tiene permisos seguros
PERMS=$(stat -f %OLp .env 2>/dev/null || stat -c %a .env)
if [[ "$PERMS" != "600" && "$PERMS" != "400" ]]; then
    log_warn ".env tiene permisos inseguros: $PERMS. Corrigiendo a 600..."
    chmod 600 .env
fi
log_success "Archivo .env con permisos seguros"

# Validar variables críticas
for var in DB_HOST DB_NAME DB_USER DB_PASS ADMIN_PASSWORD_HASH SECRET_KEY ENCRYPTION_KEY; do
    if ! grep -q "^$var=" .env; then
        log_error "Variable $var no encontrada en .env"
    fi
done
log_success "Variables de entorno OK"

# 3. Crear virtual environment si no existe
echo ""
echo "3️⃣  Configurando Python..."
if [[ ! -d "venv" ]]; then
    log_warn "Virtual environment no existe. Creando..."
    python3 -m venv venv
fi

# Activar venv
source venv/bin/activate
log_success "Virtual environment activado"

# 4. Instalar dependencias
echo ""
echo "4️⃣  Instalando dependencias..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null || log_error "Error instalando dependencias"
log_success "Dependencias instaladas"

# 5. Pruebas básicas de importación
echo ""
echo "5️⃣  Verificando imports..."
python3 -c "
import flask
import psycopg2
import werkzeug
import cryptography
import flask_wtf
from flask_limiter import Limiter
" || log_error "Falta alguna dependencia"
log_success "Todas las librerías importan correctamente"

# 6. Validar que .env no está en git
echo ""
echo "6️⃣  Verificando seguridad de git..."
if [[ -d ".git" ]]; then
    if git ls-files .env 2>/dev/null | grep -q .env; then
        log_error ".env está tracked en git. Ejecuta: git rm --cached .env"
    fi
    if ! grep -q "^.env$" .gitignore 2>/dev/null; then
        log_warn "Agregando .env a .gitignore..."
        echo ".env" >> .gitignore
    fi
    log_success "Git está configurado correctamente"
fi

# 7. Verificar puerto disponible
echo ""
echo "7️⃣  Verificando puerto..."
PORT=${PORT:-80}
if [[ $EUID -ne 0 ]]; then
    PORT=8000
    log_warn "No eres root. Usando puerto 8000 en lugar de 80"
fi
log_success "Puerto a usar: $PORT"

# 8. Crear directorios de logs
echo ""
echo "8️⃣  Configurando logs..."
mkdir -p logs
chmod 755 logs
log_success "Directorio de logs creado"

# 9. Resumen final
echo ""
echo "================================"
echo "✅ DEPLOY LISTO"
echo "================================"
echo ""
echo "Próximos pasos:"
echo ""
echo "Para desarrollo local:"
echo "  source venv/bin/activate"
echo "  python3 app_seguro.py"
echo ""
echo "Para producción con Gunicorn:"
echo "  pip install gunicorn"
echo "  gunicorn -w 4 -b 0.0.0.0:$PORT app_seguro:app"
echo ""
echo "Con Nginx reverse proxy:"
echo "  sudo systemctl start nginx"
echo "  sudo systemctl status nginx"
echo ""
echo "Verificar logs:"
echo "  tail -f logs/app.log"
echo ""
echo "Documentación de seguridad:"
echo "  cat SEGURIDAD.md"
echo ""
echo "⚠️  RECUERDA:"
echo "  - Nunca compartir .env"
echo "  - Usar HTTPS en producción"
echo "  - Cambiar ADMIN_PASSWORD_HASH periódicamente"
echo "  - Hacer backups diarios de la BD"
echo "  - Monitorear logs regularmente"
echo ""

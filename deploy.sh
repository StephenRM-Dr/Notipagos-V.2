#!/bin/bash
# Script de despliegue para AWS EC2 Ubuntu - SISTEMAS MV v2.1
# Uso: ./deploy.sh

set -e  # Salir si hay error

echo "======================================="
echo "🚀 DEPLOY AWS EC2 - SISTEMAS MV v2.1"
echo "======================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Verificar que estamos en el directorio correcto
echo ""
echo "1️⃣  Verificando estructura..."
[[ -f "app.py" ]] || log_error "app.py no encontrado"
[[ -f "requirements.txt" ]] || log_error "requirements.txt no encontrado"
[[ -f ".env.example" ]] || log_error ".env.example no encontrado"
log_success "Estructura de archivos OK"

# 2. Verificar .env
echo ""
echo "2️⃣  Verificando configuración..."
if [[ ! -f ".env" ]]; then
    log_warn "Archivo .env no existe. Creando desde .env.example..."
    cp .env.example .env
    log_info "Edita .env con tus credenciales de AWS RDS/Neon"
    log_info "nano .env"
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Validar que .env tiene permisos seguros
chmod 600 .env
log_success "Permisos de .env configurados (600)"

# Validar variables críticas
for var in DB_HOST DB_NAME DB_USER DB_PASS; do
    if ! grep -q "^$var=" .env || grep -q "^$var=$" .env || grep -q "^$var=your-" .env; then
        log_error "Variable $var no configurada en .env. Edita el archivo con tus credenciales reales."
    fi
done
log_success "Variables de entorno configuradas"

# 3. Actualizar sistema
echo ""
echo "3️⃣  Actualizando sistema Ubuntu..."
sudo apt-get update -qq
log_success "Sistema actualizado"

# 4. Instalar dependencias del sistema
echo ""
echo "4️⃣  Instalando dependencias del sistema..."
sudo apt-get install -y -qq python3 python3-pip python3-venv nginx > /dev/null
log_success "Dependencias del sistema instaladas"

# 5. Crear virtual environment
echo ""
echo "5️⃣  Configurando Python virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    log_success "Virtual environment creado"
else
    log_info "Virtual environment ya existe"
fi

# Activar venv
source venv/bin/activate
log_success "Virtual environment activado"

# 6. Instalar dependencias Python
echo ""
echo "6️⃣  Instalando dependencias Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q || log_error "Error instalando dependencias"
pip install gunicorn -q
log_success "Dependencias Python instaladas"

# 7. Verificar imports
echo ""
echo "7️⃣  Verificando imports..."
python3 -c "
import flask
import psycopg2
import werkzeug
import cryptography
from flask_limiter import Limiter
print('OK')
" > /dev/null || log_error "Falta alguna dependencia"
log_success "Todas las librerías importan correctamente"

# 8. Crear tablas en la base de datos
echo ""
echo "8️⃣  Configurando base de datos..."
if [[ -f "create_table.py" ]]; then
    read -p "¿Crear/actualizar tablas en la BD? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        python3 create_table.py || log_warn "Error creando tablas (puede ser que ya existan)"
        log_success "Tablas verificadas/creadas"
    fi
else
    log_warn "create_table.py no encontrado"
fi

# 9. Configurar Gunicorn como servicio systemd
echo ""
echo "9️⃣  Configurando servicio systemd..."
CURRENT_DIR=$(pwd)
USER=$(whoami)

sudo tee /etc/systemd/system/pagos.service > /dev/null <<EOF
[Unit]
Description=Sistemas MV - Aplicación de Pagos
After=network.target

[Service]
Type=notify
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable pagos.service
log_success "Servicio systemd configurado"

# 10. Configurar Nginx
echo ""
echo "🔟 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/pagos > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Logs
    access_log /var/log/nginx/pagos_access.log;
    error_log /var/log/nginx/pagos_error.log;
}
EOF

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/pagos /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t || log_error "Error en configuración de Nginx"
log_success "Nginx configurado"

# 11. Configurar firewall (UFW)
echo ""
echo "1️⃣1️⃣  Configurando firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 22/tcp comment 'SSH'
    sudo ufw allow 80/tcp comment 'HTTP'
    sudo ufw allow 443/tcp comment 'HTTPS'
    sudo ufw --force enable
    log_success "Firewall configurado"
else
    log_warn "UFW no instalado, saltando configuración de firewall"
fi

# 12. Crear directorio de logs
echo ""
echo "1️⃣2️⃣  Configurando logs..."
mkdir -p logs
chmod 755 logs
log_success "Directorio de logs creado"

# 13. Iniciar servicios
echo ""
echo "1️⃣3️⃣  Iniciando servicios..."
sudo systemctl restart pagos.service
sudo systemctl restart nginx
log_success "Servicios iniciados"

# 14. Verificar estado
echo ""
echo "1️⃣4️⃣  Verificando estado..."
sleep 3

if sudo systemctl is-active --quiet pagos.service; then
    log_success "Servicio pagos.service está corriendo"
else
    log_error "Servicio pagos.service no está corriendo. Ver logs: sudo journalctl -u pagos.service -n 50"
fi

if sudo systemctl is-active --quiet nginx; then
    log_success "Nginx está corriendo"
else
    log_error "Nginx no está corriendo. Ver logs: sudo journalctl -u nginx -n 50"
fi

# 15. Obtener IP pública
echo ""
echo "1️⃣5️⃣  Obteniendo información del servidor..."
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "No disponible")
PRIVATE_IP=$(hostname -I | awk '{print $1}')

# Resumen final
echo ""
echo "======================================="
echo "✅ DEPLOY COMPLETADO"
echo "======================================="
echo ""
echo "📊 Información del Servidor:"
echo "  IP Pública:  $PUBLIC_IP"
echo "  IP Privada:  $PRIVATE_IP"
echo "  Puerto:      80 (HTTP)"
echo ""
echo "🌐 Acceso a la Aplicación:"
echo "  Portal:      http://$PUBLIC_IP"
echo "  Admin:       http://$PUBLIC_IP/login"
echo "  Webhook:     http://$PUBLIC_IP/webhook-bdv"
echo ""
echo "🔧 Comandos Útiles:"
echo "  Ver logs app:     sudo journalctl -u pagos.service -f"
echo "  Ver logs nginx:   sudo tail -f /var/log/nginx/pagos_error.log"
echo "  Reiniciar app:    sudo systemctl restart pagos.service"
echo "  Reiniciar nginx:  sudo systemctl restart nginx"
echo "  Estado servicios: sudo systemctl status pagos.service nginx"
echo ""
echo "📝 Configuración:"
echo "  Editar .env:      nano .env"
echo "  Editar nginx:     sudo nano /etc/nginx/sites-available/pagos"
echo "  Editar servicio:  sudo nano /etc/systemd/system/pagos.service"
echo ""
echo "⚠️  IMPORTANTE:"
echo "  1. Cambia el PIN por defecto (1234) en .env"
echo "  2. Configura MacroDroid con: http://$PUBLIC_IP/webhook-bdv"
echo "  3. Considera configurar HTTPS con Let's Encrypt"
echo "  4. Configura backups automáticos de la BD"
echo "  5. Monitorea los logs regularmente"
echo ""
echo "📚 Documentación:"
echo "  cat LEEME_PRIMERO.md"
echo "  cat CONFIGURACION_MACRODROID.md"
echo "  cat SEGURIDAD.md"
echo ""
echo "🎉 ¡Aplicación desplegada exitosamente!"
echo ""

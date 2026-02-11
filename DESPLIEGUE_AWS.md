# 🚀 Guía de Despliegue en AWS EC2

## 📋 Requisitos Previos

- ✅ Cuenta de AWS activa
- ✅ Instancia EC2 Ubuntu 20.04/22.04 LTS
- ✅ Base de datos PostgreSQL (AWS RDS o Neon)
- ✅ Security Group configurado (puertos 22, 80, 443)
- ✅ Par de claves SSH para acceder a EC2

---

## 🔧 Configuración de EC2

### 1. Crear Instancia EC2

**Especificaciones mínimas:**
- Tipo: t2.micro (capa gratuita) o t2.small
- AMI: Ubuntu Server 22.04 LTS
- Storage: 8-10 GB
- Security Group: Permitir puertos 22, 80, 443

### 2. Configurar Security Group

```
Inbound Rules:
- SSH (22)     → Tu IP o 0.0.0.0/0
- HTTP (80)    → 0.0.0.0/0
- HTTPS (443)  → 0.0.0.0/0

Outbound Rules:
- All traffic → 0.0.0.0/0
```

---

## 📦 Subir Archivos a EC2

### Opción 1: SCP (Desde tu PC)

```bash
# Comprimir archivos localmente
cd "C:\Users\Sistemas\Documents\Notipagos V.2"
tar -czf pagos.tar.gz app.py requirements.txt .env.example .gitignore \
  create_table.py migrate.py test_db.py nginx.conf.example deploy.sh \
  LEEME_PRIMERO.md CONFIGURACION_MACRODROID.md SEGURIDAD.md

# Subir a EC2
scp -i tu-clave.pem pagos.tar.gz ubuntu@TU-IP-EC2:/home/ubuntu/

# Conectar a EC2
ssh -i tu-clave.pem ubuntu@TU-IP-EC2

# Descomprimir
cd /home/ubuntu
tar -xzf pagos.tar.gz
mv pagos pagos-old  # Backup de versión anterior
mkdir pagos
mv app.py requirements.txt .env.example .gitignore create_table.py \
   migrate.py test_db.py nginx.conf.example deploy.sh \
   LEEME_PRIMERO.md CONFIGURACION_MACRODROID.md SEGURIDAD.md pagos/
cd pagos
```

### Opción 2: Git (Recomendado)

```bash
# En EC2
ssh -i tu-clave.pem ubuntu@TU-IP-EC2

# Clonar repositorio
cd /home/ubuntu
git clone https://github.com/tu-usuario/tu-repo.git pagos
cd pagos

# O actualizar si ya existe
cd /home/ubuntu/pagos
git pull origin main
```

### Opción 3: Reemplazar Archivos Manualmente

```bash
# Conectar a EC2
ssh -i tu-clave.pem ubuntu@TU-IP-EC2

# Backup de versión anterior
cd /home/ubuntu
mv pagos pagos-backup-$(date +%Y%m%d)

# Crear nuevo directorio
mkdir pagos
cd pagos

# Subir archivos uno por uno con scp desde otra terminal
# scp -i tu-clave.pem archivo ubuntu@TU-IP-EC2:/home/ubuntu/pagos/
```

---

## 🚀 Despliegue Automático

### Paso 1: Dar Permisos al Script

```bash
cd /home/ubuntu/pagos
chmod +x deploy.sh
```

### Paso 2: Ejecutar Script de Despliegue

```bash
./deploy.sh
```

El script hará automáticamente:
1. ✅ Verificar estructura de archivos
2. ✅ Crear/verificar .env
3. ✅ Actualizar sistema Ubuntu
4. ✅ Instalar dependencias (Python, Nginx)
5. ✅ Crear virtual environment
6. ✅ Instalar dependencias Python
7. ✅ Configurar base de datos
8. ✅ Configurar Gunicorn como servicio
9. ✅ Configurar Nginx
10. ✅ Configurar firewall
11. ✅ Iniciar servicios

### Paso 3: Configurar .env

```bash
nano .env
```

Editar con tus credenciales:
```env
# BASE DE DATOS (AWS RDS o Neon)
DB_HOST=tu-rds-endpoint.rds.amazonaws.com
DB_NAME=pagos
DB_USER=postgres
DB_PASS=tu-contraseña-segura
DB_PORT=5432

# Las claves de seguridad se generan automáticamente
# Solo cambia el PIN por defecto
```

Guardar: `Ctrl+O`, `Enter`, `Ctrl+X`

### Paso 4: Reiniciar Servicios

```bash
sudo systemctl restart pagos.service
sudo systemctl restart nginx
```

---

## 🔍 Verificación

### 1. Verificar Servicios

```bash
# Estado de la aplicación
sudo systemctl status pagos.service

# Estado de Nginx
sudo systemctl status nginx

# Ver logs en tiempo real
sudo journalctl -u pagos.service -f
```

### 2. Probar la Aplicación

```bash
# Obtener IP pública
curl http://checkip.amazonaws.com

# Probar desde el servidor
curl http://localhost

# Probar desde tu navegador
# http://TU-IP-PUBLICA
```

### 3. Probar Webhook

```bash
curl -X POST http://localhost/webhook-bdv \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Recibiste un PagomovilBDV comercio por Bs. 100,00 del 0414-1234567 Ref: 000123456789"}'
```

---

## 🔒 Configurar HTTPS (Opcional pero Recomendado)

### Instalar Certbot

```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

### Obtener Certificado SSL

```bash
# Reemplaza con tu dominio
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

### Renovación Automática

```bash
# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## 📊 Monitoreo

### Ver Logs

```bash
# Logs de la aplicación
sudo journalctl -u pagos.service -n 100

# Logs de Nginx
sudo tail -f /var/log/nginx/pagos_access.log
sudo tail -f /var/log/nginx/pagos_error.log

# Logs en tiempo real
sudo journalctl -u pagos.service -f
```

### Verificar Recursos

```bash
# Uso de CPU y memoria
htop

# Espacio en disco
df -h

# Procesos de Python
ps aux | grep gunicorn
```

---

## 🔄 Actualizar la Aplicación

### Método 1: Git Pull

```bash
cd /home/ubuntu/pagos
git pull origin main
sudo systemctl restart pagos.service
```

### Método 2: Reemplazar Archivos

```bash
# Backup
cd /home/ubuntu
cp -r pagos pagos-backup-$(date +%Y%m%d)

# Subir nuevos archivos
# scp -i tu-clave.pem app.py ubuntu@TU-IP-EC2:/home/ubuntu/pagos/

# Reiniciar
cd pagos
sudo systemctl restart pagos.service
```

---

## 🐛 Solución de Problemas

### Problema 1: Servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u pagos.service -n 50 --no-pager

# Verificar sintaxis de Python
cd /home/ubuntu/pagos
source venv/bin/activate
python3 -c "import app"
```

### Problema 2: Error de conexión a BD

```bash
# Probar conexión
cd /home/ubuntu/pagos
source venv/bin/activate
python3 test_db.py

# Verificar .env
cat .env | grep DB_
```

### Problema 3: Nginx no funciona

```bash
# Verificar configuración
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/error.log

# Reiniciar
sudo systemctl restart nginx
```

### Problema 4: Puerto 80 ocupado

```bash
# Ver qué usa el puerto 80
sudo lsof -i :80

# Matar proceso si es necesario
sudo kill -9 PID
```

---

## 🔐 Seguridad Adicional

### 1. Cambiar PIN por Defecto

```bash
cd /home/ubuntu/pagos
nano .env

# Generar nuevo hash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('tu-nuevo-pin'))"

# Copiar el hash y reemplazar ADMIN_PASSWORD_HASH en .env
```

### 2. Configurar Fail2Ban

```bash
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Actualizar Sistema Regularmente

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo reboot
```

---

## 📋 Checklist de Despliegue

- [ ] Instancia EC2 creada y accesible
- [ ] Security Group configurado (22, 80, 443)
- [ ] Base de datos PostgreSQL configurada
- [ ] Archivos subidos a EC2
- [ ] Script deploy.sh ejecutado
- [ ] Archivo .env configurado con credenciales reales
- [ ] PIN por defecto cambiado
- [ ] Servicios iniciados (pagos.service, nginx)
- [ ] Aplicación accesible desde navegador
- [ ] Webhook probado
- [ ] MacroDroid configurado con IP pública
- [ ] HTTPS configurado (opcional)
- [ ] Backups configurados

---

## 📞 Comandos Rápidos

```bash
# Reiniciar aplicación
sudo systemctl restart pagos.service

# Ver logs
sudo journalctl -u pagos.service -f

# Editar configuración
nano .env

# Verificar estado
sudo systemctl status pagos.service nginx

# Actualizar código
cd /home/ubuntu/pagos && git pull && sudo systemctl restart pagos.service
```

---

## 🎯 URLs Importantes

```
Portal público:    http://TU-IP-PUBLICA
Panel admin:       http://TU-IP-PUBLICA/login
Webhook MacroDroid: http://TU-IP-PUBLICA/webhook-bdv
```

---

*Guía de despliegue AWS - 2026-02-09*

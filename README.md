# 🚀 Sistemas MV - Aplicación de Verificación de Pagos v2.1

Sistema de verificación de pagos móviles con integración automática de notificaciones bancarias.

---

## ✨ Características

- ✅ Generación automática de claves de seguridad
- ✅ Verificación con últimos 6 dígitos de referencia
- ✅ Webhook para recibir notificaciones de MacroDroid
- ✅ Extractor inteligente para BDV, Plaza y Sofitasa
- ✅ Panel de administración seguro
- ✅ Protección contra duplicados y SQL injection
- ✅ Rate limiting y validaciones completas
- ✅ Listo para despliegue en AWS EC2

---

## 📦 Archivos Principales

```
├── app.py                          # Aplicación Flask principal
├── requirements.txt                # Dependencias Python
├── deploy.sh                       # Script de despliegue AWS
├── .env.example                    # Plantilla de configuración
└── DESPLIEGUE_AWS.md              # Guía de despliegue
```

---

## 🚀 Inicio Rápido

### Desarrollo Local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar aplicación
python app.py

# 3. Acceder
# http://localhost:5000
```

### Despliegue en AWS EC2

```bash
# 1. Subir archivos a EC2
scp -i clave.pem -r * ubuntu@IP:/home/ubuntu/pagos/

# 2. Conectar a EC2
ssh -i clave.pem ubuntu@IP

# 3. Ejecutar script de despliegue
cd /home/ubuntu/pagos
chmod +x deploy.sh
./deploy.sh

# 4. Configurar .env
nano .env
```

Ver guía completa: **DESPLIEGUE_AWS.md**

---

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Base de Datos
DB_HOST=tu-host.rds.amazonaws.com
DB_NAME=pagos
DB_USER=postgres
DB_PASS=tu-contraseña
DB_PORT=5432

# Seguridad (se generan automáticamente)
ADMIN_PASSWORD_HASH=...
SECRET_KEY=...
ENCRYPTION_KEY=...
```

### MacroDroid

Configurar webhook en MacroDroid:
- URL: `http://TU-IP-PUBLICA/webhook-bdv`
- Method: POST
- Body: `{"mensaje": "{notification_text}"}`

Ver guía: **CONFIGURACION_MACRODROID.md**

---

## 📱 Flujo de Trabajo

```
1. Cliente hace pago móvil
   ↓
2. Banco envía notificación SMS/WhatsApp
   ↓
3. MacroDroid captura y envía al servidor
   ↓
4. Servidor procesa y almacena en BD
   ↓
5. Cliente verifica con últimos 6 dígitos
   ↓
6. Sistema vincula pago con comanda
```

---

## 🔒 Seguridad

- ✅ Claves generadas automáticamente con métodos criptográficos
- ✅ Passwords hasheados con bcrypt/scrypt
- ✅ Protección SQL injection con parámetros preparados
- ✅ Rate limiting (100 requests/hora)
- ✅ Validación completa de entrada
- ✅ Encriptación de datos sensibles
- ✅ Logging y auditoría

---

## 📚 Documentación

- **LEEME_PRIMERO.md** - Guía de inicio rápido
- **DESPLIEGUE_AWS.md** - Guía completa de despliegue en AWS
- **CONFIGURACION_MACRODROID.md** - Configuración de MacroDroid
- **SEGURIDAD.md** - Documentación de seguridad
- **PREPARAR_PARA_AWS.md** - Preparar archivos para AWS

---

## 🛠️ Tecnologías

- Python 3.8+
- Flask 3.0
- PostgreSQL
- Gunicorn
- Nginx
- AWS EC2
- MacroDroid

---

## 📊 Endpoints

```
GET  /                  # Portal de verificación
POST /verificar         # Verificar pago
GET  /login             # Login admin
GET  /admin             # Panel admin
POST /webhook-bdv       # Webhook MacroDroid
GET  /admin/exportar    # Exportar Excel
```

---

## 🔄 Actualización

```bash
# En EC2
cd /home/ubuntu/pagos
git pull origin main
sudo systemctl restart pagos.service
```

---

## 🐛 Solución de Problemas

### Ver logs
```bash
sudo journalctl -u pagos.service -f
```

### Reiniciar servicios
```bash
sudo systemctl restart pagos.service nginx
```

### Verificar estado
```bash
sudo systemctl status pagos.service nginx
```

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la documentación en los archivos .md
2. Verifica los logs del servidor
3. Consulta DESPLIEGUE_AWS.md para AWS

---

## 📝 Licencia

Uso interno - Sistemas MV

---

## 🎯 Versión

**v2.1** - Optimizada para AWS EC2
- Generación automática de claves
- Verificación con últimos 6 dígitos
- Script de despliegue automatizado
- Documentación completa

---

*Última actualización: 2026-02-09*

# 📦 Preparar Archivos para AWS

## ✅ Archivos Listos para Despliegue

El proyecto ha sido limpiado y optimizado. Solo quedan los archivos esenciales.

---

## 📁 Estructura Final (15 archivos)

```
Notipagos V.2/
├── app.py                          ← Aplicación principal
├── requirements.txt                ← Dependencias Python
├── .env.example                    ← Plantilla de variables
├── .gitignore                      ← Git ignore
├── create_table.py                 ← Script crear tablas BD
├── migrate.py                      ← Script migración BD
├── test_db.py                      ← Test conexión BD
├── nginx.conf.example              ← Config Nginx
├── deploy.sh                       ← Script despliegue AWS
├── LEEME_PRIMERO.md               ← Guía rápida
├── CONFIGURACION_MACRODROID.md    ← Config MacroDroid
├── SEGURIDAD.md                   ← Documentación seguridad
├── DESPLIEGUE_AWS.md              ← Guía AWS (NUEVO)
├── ARCHIVOS_PARA_AWS.md           ← Lista de archivos
└── PREPARAR_PARA_AWS.md           ← Este archivo
```

---

## 🗑️ Archivos Eliminados (20 archivos)

- ❌ Documentación redundante (10 archivos)
- ❌ Scripts de Windows (2 archivos)
- ❌ Archivos obsoletos (3 archivos)
- ❌ Documentación de desarrollo (5 archivos)

**Total reducido:** De 35 a 15 archivos (~57% menos)

---

## 📦 Opción 1: Comprimir para Subir

### En Windows (PowerShell):

```powershell
# Ir al directorio
cd "C:\Users\Sistemas\Documents\Notipagos V.2"

# Comprimir archivos esenciales
Compress-Archive -Path app.py,requirements.txt,.env.example,.gitignore,`
  "create table.py",migrate.py,test_db.py,nginx.conf.example,deploy.sh,`
  LEEME_PRIMERO.md,CONFIGURACION_MACRODROID.md,SEGURIDAD.md,DESPLIEGUE_AWS.md `
  -DestinationPath pagos-aws.zip -Force

# Verificar
Get-ChildItem pagos-aws.zip
```

### En Linux/Mac:

```bash
# Ir al directorio
cd ~/Documents/Notipagos\ V.2

# Comprimir
tar -czf pagos-aws.tar.gz app.py requirements.txt .env.example .gitignore \
  create_table.py migrate.py test_db.py nginx.conf.example deploy.sh \
  LEEME_PRIMERO.md CONFIGURACION_MACRODROID.md SEGURIDAD.md DESPLIEGUE_AWS.md

# Verificar
ls -lh pagos-aws.tar.gz
```

---

## 📤 Opción 2: Subir con SCP

```bash
# Subir archivo comprimido
scp -i tu-clave.pem pagos-aws.tar.gz ubuntu@TU-IP-EC2:/home/ubuntu/

# Conectar a EC2
ssh -i tu-clave.pem ubuntu@TU-IP-EC2

# Descomprimir
cd /home/ubuntu
tar -xzf pagos-aws.tar.gz -C pagos/
cd pagos
```

---

## 🔄 Opción 3: Usar Git (Recomendado)

### Preparar Repositorio:

```bash
# En tu PC (Git Bash o PowerShell)
cd "C:\Users\Sistemas\Documents\Notipagos V.2"

# Verificar estado
git status

# Agregar archivos
git add app.py requirements.txt .env.example .gitignore \
  create_table.py migrate.py test_db.py nginx.conf.example deploy.sh \
  LEEME_PRIMERO.md CONFIGURACION_MACRODROID.md SEGURIDAD.md DESPLIEGUE_AWS.md

# Commit
git commit -m "Versión 2.1 - Optimizada para AWS"

# Push
git push origin main
```

### En EC2:

```bash
# Conectar
ssh -i tu-clave.pem ubuntu@TU-IP-EC2

# Backup de versión anterior
cd /home/ubuntu
mv pagos pagos-backup-$(date +%Y%m%d)

# Clonar nueva versión
git clone https://github.com/StephenRM-Dr/Notipagos-V.2.git pagos
cd pagos

# O actualizar si ya existe
cd /home/ubuntu/pagos
git pull origin main
```

---

## 🚀 Despliegue en AWS

### Paso 1: Subir Archivos

Elige una de las opciones anteriores (SCP, Git, etc.)

### Paso 2: Ejecutar Script de Despliegue

```bash
# Conectar a EC2
ssh -i tu-clave.pem ubuntu@TU-IP-EC2

# Ir al directorio
cd /home/ubuntu/pagos

# Dar permisos
chmod +x deploy.sh

# Ejecutar
./deploy.sh
```

### Paso 3: Configurar .env

```bash
nano .env

# Editar con credenciales de AWS RDS o Neon
# Guardar: Ctrl+O, Enter, Ctrl+X
```

### Paso 4: Reiniciar

```bash
sudo systemctl restart pagos.service
sudo systemctl restart nginx
```

---

## ✅ Verificación

### 1. Verificar Archivos Subidos

```bash
cd /home/ubuntu/pagos
ls -la

# Deberías ver:
# app.py
# requirements.txt
# .env.example
# deploy.sh
# etc.
```

### 2. Verificar Servicios

```bash
sudo systemctl status pagos.service
sudo systemctl status nginx
```

### 3. Probar Aplicación

```bash
# Obtener IP pública
curl http://checkip.amazonaws.com

# Probar en navegador
# http://TU-IP-PUBLICA
```

---

## 📋 Checklist Pre-Despliegue

- [ ] Archivos comprimidos o repositorio Git actualizado
- [ ] Clave SSH de EC2 disponible
- [ ] IP pública de EC2 conocida
- [ ] Credenciales de base de datos listas
- [ ] Security Group configurado (22, 80, 443)
- [ ] Backup de versión anterior hecho (si existe)

---

## 📋 Checklist Post-Despliegue

- [ ] Archivos subidos a EC2
- [ ] Script deploy.sh ejecutado sin errores
- [ ] Archivo .env configurado
- [ ] Servicios corriendo (pagos.service, nginx)
- [ ] Aplicación accesible desde navegador
- [ ] PIN por defecto cambiado
- [ ] Webhook probado
- [ ] MacroDroid configurado

---

## 🔧 Comandos Útiles

```bash
# Comprimir (Windows PowerShell)
Compress-Archive -Path * -DestinationPath pagos-aws.zip

# Comprimir (Linux/Mac)
tar -czf pagos-aws.tar.gz *

# Subir a EC2
scp -i clave.pem pagos-aws.tar.gz ubuntu@IP:/home/ubuntu/

# Conectar a EC2
ssh -i clave.pem ubuntu@IP

# Descomprimir en EC2
tar -xzf pagos-aws.tar.gz

# Ejecutar despliegue
chmod +x deploy.sh && ./deploy.sh
```

---

## 📚 Documentación

1. **DESPLIEGUE_AWS.md** - Guía completa de despliegue en AWS
2. **LEEME_PRIMERO.md** - Guía de inicio rápido
3. **CONFIGURACION_MACRODROID.md** - Configurar MacroDroid
4. **SEGURIDAD.md** - Documentación de seguridad

---

## 🎯 Próximos Pasos

1. Lee **DESPLIEGUE_AWS.md** para instrucciones detalladas
2. Sube los archivos a EC2
3. Ejecuta `./deploy.sh`
4. Configura `.env` con tus credenciales
5. Cambia el PIN por defecto
6. Configura MacroDroid con la IP pública

---

*Preparación para AWS - 2026-02-09*

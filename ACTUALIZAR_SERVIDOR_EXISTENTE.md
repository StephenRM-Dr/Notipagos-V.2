# 🔄 Actualizar Servidor AWS Existente

## 📍 Tu Servidor Actual

```
IP: 3.150.222.173
Puerto: 5000
URL actual: http://3.150.222.173:5000
```

---

## ✅ Ventaja: No Necesitas Cambiar MacroDroid

Como ya tienes la IP configurada en MacroDroid, solo necesitas actualizar los archivos en el servidor. Las macros seguirán funcionando sin cambios.

---

## 🔄 Opción 1: Actualización Rápida (Recomendada)

### Paso 1: Conectar al Servidor

```bash
ssh -i tu-clave.pem ubuntu@3.150.222.173
```

### Paso 2: Hacer Backup de la Versión Actual

```bash
cd /home/ubuntu
sudo systemctl stop pagos 2>/dev/null || true
cp -r pagos pagos-backup-$(date +%Y%m%d-%H%M%S)
cd pagos
```

### Paso 3: Subir Solo el Archivo Principal

Desde tu PC (PowerShell):

```powershell
# Subir app.py actualizado
scp -i tu-clave.pem app.py ubuntu@3.150.222.173:/home/ubuntu/pagos/

# Subir requirements.txt (por si hay nuevas dependencias)
scp -i tu-clave.pem requirements.txt ubuntu@3.150.222.173:/home/ubuntu/pagos/
```

### Paso 4: Actualizar en el Servidor

```bash
# Conectar al servidor
ssh -i tu-clave.pem ubuntu@3.150.222.173

# Ir al directorio
cd /home/ubuntu/pagos

# Activar virtual environment
source venv/bin/activate

# Actualizar dependencias (por si acaso)
pip install -r requirements.txt

# Verificar que el .env existe y tiene las claves
ls -la .env

# Si no existe .env, las claves se generarán automáticamente al iniciar
```

### Paso 5: Reiniciar la Aplicación

```bash
# Si usas systemd
sudo systemctl restart pagos

# O si ejecutas manualmente
pkill -f "python.*app.py"
nohup python app.py > app.log 2>&1 &
```

### Paso 6: Verificar

```bash
# Ver logs
tail -f app.log

# O si usas systemd
sudo journalctl -u pagos -f

# Probar que funciona
curl http://localhost:5000
```

---

## 🔄 Opción 2: Actualización Completa con Git

### Paso 1: Preparar Repositorio (En tu PC)

```powershell
# Agregar archivos
git add .

# Commit
git commit -m "v2.1 - Actualización con generación automática de claves"

# Push
git push origin main
```

### Paso 2: Actualizar en el Servidor

```bash
# Conectar
ssh -i tu-clave.pem ubuntu@3.150.222.173

# Ir al directorio
cd /home/ubuntu/pagos

# Backup
sudo systemctl stop pagos 2>/dev/null || true
cd ..
cp -r pagos pagos-backup-$(date +%Y%m%d)

# Actualizar desde Git
cd pagos
git pull origin main

# Activar venv y actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar
sudo systemctl restart pagos
```

---

## 🔄 Opción 3: Reemplazo Manual Completo

### Paso 1: Comprimir Archivos (En tu PC)

```powershell
# Comprimir archivos esenciales
Compress-Archive -Path app.py,requirements.txt,.env.example -DestinationPath pagos-update.zip -Force
```

### Paso 2: Subir y Reemplazar

```powershell
# Subir
scp -i tu-clave.pem pagos-update.zip ubuntu@3.150.222.173:/home/ubuntu/
```

```bash
# En el servidor
ssh -i tu-clave.pem ubuntu@3.150.222.173

# Detener servicio
sudo systemctl stop pagos 2>/dev/null || pkill -f "python.*app.py"

# Backup
cd /home/ubuntu
cp -r pagos pagos-backup-$(date +%Y%m%d)

# Descomprimir
cd pagos
unzip -o ../pagos-update.zip

# Reiniciar
sudo systemctl restart pagos || nohup python app.py > app.log 2>&1 &
```

---

## ⚙️ Configuración del .env

### Si el .env Ya Existe

El archivo `.env` actual se mantendrá. La aplicación detectará que ya tiene las claves y NO las regenerará.

### Si Quieres Regenerar las Claves

```bash
# Conectar al servidor
ssh -i tu-clave.pem ubuntu@3.150.222.173
cd /home/ubuntu/pagos

# Backup del .env actual
cp .env .env.backup

# Eliminar las claves que quieres regenerar
nano .env
# Borra las líneas: SECRET_KEY, ENCRYPTION_KEY, ADMIN_PASSWORD_HASH

# Reiniciar (se generarán automáticamente)
sudo systemctl restart pagos

# Ver las nuevas claves generadas
cat .env
```

---

## 🔍 Verificación Post-Actualización

### 1. Verificar que el Servicio Está Corriendo

```bash
# Si usas systemd
sudo systemctl status pagos

# O verificar procesos
ps aux | grep python
```

### 2. Verificar Logs

```bash
# Ver logs recientes
tail -n 50 app.log

# O con systemd
sudo journalctl -u pagos -n 50
```

### 3. Probar la Aplicación

```bash
# Desde el servidor
curl http://localhost:5000

# Desde tu PC (navegador)
# http://3.150.222.173:5000
```

### 4. Probar el Webhook

```bash
# Desde el servidor
curl -X POST http://localhost:5000/webhook-bdv \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Recibiste un PagomovilBDV comercio por Bs. 100,00 del 0414-1234567 Ref: 000123456789"}'
```

### 5. Probar Verificación con Últimos 6 Dígitos

```bash
# Acceder al portal
# http://3.150.222.173:5000

# Ingresar solo los últimos 6 dígitos de una referencia existente
# Ejemplo: 456789
```

---

## 📱 MacroDroid - Sin Cambios Necesarios

Tus macros seguirán funcionando con la misma configuración:

```
URL: http://3.150.222.173:5000/webhook-bdv
Method: POST
Body: {"mensaje": "{notification_text}"}
```

**No necesitas cambiar nada en MacroDroid** ✅

---

## 🆕 Nuevas Funcionalidades Disponibles

Después de actualizar, tendrás:

1. ✅ **Generación automática de claves** - Ya no necesitas ejecutar generate_secrets.py
2. ✅ **Verificación con últimos 6 dígitos** - Los clientes pueden usar solo 6 dígitos
3. ✅ **Mejor manejo de errores** - Mensajes más claros
4. ✅ **Código optimizado** - Mejor rendimiento

---

## 🐛 Solución de Problemas

### Problema: "Servicio no inicia"

```bash
# Ver logs detallados
sudo journalctl -u pagos -n 100 --no-pager

# Verificar sintaxis
cd /home/ubuntu/pagos
source venv/bin/activate
python -c "import app"
```

### Problema: "Error de importación"

```bash
# Reinstalar dependencias
cd /home/ubuntu/pagos
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Problema: "Puerto 5000 en uso"

```bash
# Ver qué usa el puerto
sudo lsof -i :5000

# Matar proceso
sudo kill -9 PID

# Reiniciar
sudo systemctl restart pagos
```

---

## 📋 Checklist de Actualización

- [ ] Backup de versión actual hecho
- [ ] Archivo app.py actualizado subido
- [ ] requirements.txt actualizado (si cambió)
- [ ] Dependencias actualizadas con pip
- [ ] Servicio reiniciado
- [ ] Logs verificados (sin errores)
- [ ] Aplicación accesible desde navegador
- [ ] Webhook probado
- [ ] Verificación con 6 dígitos probada
- [ ] MacroDroid sigue funcionando

---

## 🚀 Comando Rápido de Actualización

```bash
# Todo en uno (copia y pega)
ssh -i tu-clave.pem ubuntu@3.150.222.173 << 'EOF'
cd /home/ubuntu/pagos
sudo systemctl stop pagos 2>/dev/null || pkill -f "python.*app.py"
git pull origin main || echo "No git, actualizar manualmente"
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart pagos || nohup python app.py > app.log 2>&1 &
sleep 3
curl http://localhost:5000
echo "Actualización completada"
EOF
```

---

## 📞 URLs Finales

Después de actualizar, todo seguirá funcionando en:

```
Portal:    http://3.150.222.173:5000
Admin:     http://3.150.222.173:5000/login
Webhook:   http://3.150.222.173:5000/webhook-bdv
```

---

*Guía de actualización - 2026-02-09*

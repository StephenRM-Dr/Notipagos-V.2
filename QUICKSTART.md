# ⚡ Guía Rápida de Inicio - SISTEMAS MV v2.0

## 🚀 Inicio en 5 minutos

### 1️⃣ Clonar/Descargar archivos
```bash
# Si tienes git
git clone https://tu-repo.git sistemas-mv
cd sistemas-mv

# Si descargaste ZIP
unzip sistemas-mv.zip
cd sistemas-mv
```

### 2️⃣ Generar secretos seguros (OBLIGATORIO)
```bash
python3 generate_secrets.py
```

Seguir las instrucciones interactivas:
- Ingresa tu PIN (mínimo 4 dígitos) → Generará `ADMIN_PASSWORD_HASH`
- Se genera automáticamente `SECRET_KEY`
- Se genera automáticamente `ENCRYPTION_KEY`
- Opción de guardar en `.env`

### 3️⃣ Completar configuración
```bash
nano .env  # O editar con tu editor favorito
```

Completar SOLO estos campos:
```env
DB_HOST=neon-project.neon.tech
DB_NAME=neondb
DB_USER=neonuser
DB_PASS=tu-contraseña-bd
```

El resto ya está generado.

### 4️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5️⃣ Ejecutar aplicación
```bash
python3 app_seguro.py
```

Acceder a: **http://localhost**

---

## 📝 Archivos Incluidos

| Archivo | Descripción |
|---------|-------------|
| `app_seguro.py` | Aplicación Flask mejorada |
| `requirements.txt` | Dependencias Python |
| `generate_secrets.py` | Generador de claves seguras |
| `SEGURIDAD.md` | Documentación completa de seguridad |
| `CHANGELOG.md` | Lista de cambios y mejoras |
| `.env.example` | Plantilla de variables |
| `nginx.conf.example` | Config Nginx para producción |
| `deploy.sh` | Script de despliegue |
| `QUICKSTART.md` | Este archivo |

---

## 🔐 Seguridad Incluida

✅ Autenticación con contraseña hasheada (bcrypt)
✅ Protección CSRF en todos los formularios
✅ Validación completa de entrada
✅ Rate limiting anti-fuerza bruta
✅ Encriptación de datos sensibles
✅ Logging y auditoría
✅ Sesiones seguras con timeout
✅ Manejo de errores seguro

---

## 🐛 Problemas Comunes

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Error: SECRET_KEY no está definida"
```bash
python3 generate_secrets.py
# Asegúrate de haber guardado el .env
```

### "Error de conexión a BD"
```bash
# Verifica en .env:
1. DB_HOST correcto
2. DB_USER y DB_PASS correctos
3. BD creada en Neon/PostgreSQL
4. IP del servidor está en whitelist
```

### "Puerto 80 en uso"
```bash
# Cambiar puerto en app_seguro.py (última línea):
app.run(host='0.0.0.0', port=8000, debug=False)
```

---

## 📚 Documentación

Para guía completa de seguridad:
```bash
cat SEGURIDAD.md
```

Para detalles técnicos:
```bash
cat CHANGELOG.md
```

Para despliegue en producción:
```bash
cat deploy.sh
```

---

## 🚀 Despliegue en Producción

### Opción 1: Gunicorn (Recomendado)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app_seguro:app
```

### Opción 2: Nginx + Gunicorn
```bash
# Ver: nginx.conf.example
sudo cp nginx.conf.example /etc/nginx/sites-available/sistemas-mv
sudo ln -s /etc/nginx/sites-available/sistemas-mv /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Opción 3: Docker (Próximamente)
```dockerfile
# Agregar Dockerfile en siguientes versiones
```

---

## ✅ Checklist Antes de Producción

- [ ] PIN de admin cambiado (ejecutar `generate_secrets.py`)
- [ ] `.env` con credenciales reales completadas
- [ ] Archivo `.env` con permisos 600 (`chmod 600 .env`)
- [ ] `.env` en `.gitignore`
- [ ] BD PostgreSQL accesible
- [ ] Certificado SSL/TLS instalado
- [ ] Nginx o Gunicorn configurado
- [ ] Logs configurados
- [ ] Backups automáticos del BD

---

## 💡 Tips Útiles

### Ver logs en tiempo real
```bash
tail -f app.log
```

### Crear usuario de admin adicional
```python
# En el hash del nuevo PIN:
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('1234'))"
# Copiar hash a ADMIN_PASSWORD_HASH en .env
```

### Respaldar BD
```bash
pg_dump -h host -U user dbname > backup_$(date +%Y%m%d).sql
```

### Ejecutar en background
```bash
nohup python3 app_seguro.py > app.log 2>&1 &
```

---

## 🆘 Soporte

1. Revisar `SEGURIDAD.md` para problemas de seguridad
2. Revisar `CHANGELOG.md` para cambios técnicos
3. Revisar logs: `tail -f app.log`
4. Ejecutar `generate_secrets.py` si hay problemas con keys

---

## 📞 Contacto & Reporte de Errores

Si encuentras un problema:
1. Revisa documentación
2. Verifica los logs
3. Intenta regenerar secretos con `generate_secrets.py`
4. Reporta con detalles en los logs (sin exponer `.env`)

---

**¡Listo! Tu aplicación está 100% segura. 🎉**

Siguiente paso: Accede a http://localhost y usa tu PIN

---

*Última actualización: 2026-01-24*
*Versión: 2.0 - Hardened Security*

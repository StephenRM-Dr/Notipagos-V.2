# 🔒 GUÍA DE SEGURIDAD - SISTEMAS MV v2.0

## 📋 Índice
1. [Cambios de Seguridad](#cambios-de-seguridad)
2. [Configuración Inicial](#configuración-inicial)
3. [Variables de Entorno](#variables-de-entorno)
4. [Instalación](#instalación)
5. [Pruebas de Seguridad](#pruebas-de-seguridad)
6. [Despliegue en Producción](#despliegue-en-producción)

---

## 🔐 Cambios de Seguridad

### 1. **Hashing de Contraseñas (Werkzeug)**
**Antes:** 
```python
if request.form.get('password') == os.getenv("ADMIN_PASSWORD"):
```
❌ Contraseña en texto plano comparable directamente

**Después:**
```python
stored_hash = os.getenv("ADMIN_PASSWORD_HASH")
if check_password_hash(stored_hash, password):
```
✅ Usa bcrypt/PBKDF2 con salt automático

---

### 2. **Protección CSRF (Flask-WTF)**
**Antes:**
```html
<form method="POST">
  <!-- SIN protección -->
</form>
```
❌ Vulnerable a ataques CSRF

**Después:**
```html
<form method="POST">
  {{ csrf_token() }}
  <!-- Protegido -->
</form>
```
✅ Token CSRF en todos los formularios POST

---

### 3. **Validación de Entrada Completa**
**Antes:**
```python
ref = request.form.get('ref', '').strip()
# SIN validación de formato, longitud o caracteres
```
❌ Acepta cualquier entrada

**Después:**
```python
def validar_referencia(ref):
    if not ref or len(ref) < 6 or len(ref) > 20:
        return False
    return bool(re.match(r'^[A-Za-z0-9]+$', ref))

if not validar_referencia(ref):
    # Rechazar entrada inválida
```
✅ Valida longitud, formato y caracteres permitidos

---

### 4. **Rate Limiting (Flask-Limiter)**
**Antes:**
```python
@app.route('/webhook-bdv', methods=['POST'])
def webhook():
    # SIN límites
```
❌ Vulnerable a ataques de fuerza bruta y DoS

**Después:**
```python
@app.route('/webhook-bdv', methods=['POST'])
@limiter.limit("100 per hour")
def webhook():
    # Limitado a 100 solicitudes por hora
```
✅ Límites en endpoints críticos:
- `/login`: 5 intentos por minuto
- `/verificar`: 10 solicitudes por minuto
- `/webhook-bdv`: 100 por hora

---

### 5. **Encriptación de Datos Sensibles (Fernet)**
**Nuevo:**
```python
cipher_suite = Fernet(ENCRYPTION_KEY)
dato_encriptado = cipher_suite.encrypt(dato.encode()).decode()
dato_desencriptado = cipher_suite.decrypt(dato_encriptado.encode()).decode()
```
✅ Encriptación AES de datos sensibles (cuando sea necesario)

---

### 6. **Sesiones Seguras**
**Antes:**
```python
app.secret_key = "clave_sistemas_mv_2026"  # Hardcodeada ❌
```

**Después:**
```python
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise ValueError("❌ SECRET_KEY no definida")

app.secret_key = secret_key
session.permanent = True
app.permanent_session_lifetime = timedelta(hours=2)
```
✅ Clave aleatoria generada + timeout de sesión

---

### 7. **Validación de Conexión BD**
**Antes:**
```python
def get_db_connection():
    return psycopg2.connect(...)
```
❌ Sin manejo de errores

**Después:**
```python
def get_db_connection():
    try:
        conn = psycopg2.connect(..., connect_timeout=5)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error de conexión BD: {e}")
        raise Exception("Error de conexión a la base de datos")
```
✅ Timeout + logging + manejo de excepciones

---

### 8. **Logging y Auditoría**
**Nuevo:**
```python
logger.info(f"Login exitoso")
logger.warning(f"Intento de login fallido desde {ip}")
logger.error(f"Error en verificar: {e}")
```
✅ Registra eventos importantes para auditoría

---

### 9. **Limitación de Datos Almacenados**
**Antes:**
```python
cur.execute("""
    INSERT INTO pagos (..., mensaje_completo, ...) 
    VALUES (..., p['original'], ...)
""")
```
❌ Almacena texto completo sin límites

**Después:**
```python
cur.execute("""
    INSERT INTO pagos (..., mensaje_completo, ...) 
    VALUES (..., p['original'][:500], ...)
""")
```
✅ Limita a 500 caracteres + valida longitud de entrada

---

### 10. **Manejo de Errores Seguro**
**Antes:**
```python
@app.route('/admin')
def admin():
    # SIN try-except
```
❌ Expone stack traces

**Después:**
```python
@app.route('/admin')
def admin():
    try:
        # operaciones...
    except Exception as e:
        logger.error(f"Error en admin: {e}")
        return "Error al cargar panel", 500
```
✅ Errores genéricos al usuario, detalles en logs

---

## ⚙️ Configuración Inicial

### Paso 1: Generar Secretos Seguros
```bash
python3 generate_secrets.py
```

Este script genera:
- ✅ `ADMIN_PASSWORD_HASH`: Hash bcrypt de tu PIN
- ✅ `SECRET_KEY`: Clave aleatoria de 64 caracteres hex
- ✅ `ENCRYPTION_KEY`: Clave Fernet para encriptación

### Paso 2: Completar Variables de Entorno
```bash
cp .env.example .env  # Si existe el ejemplo
nano .env  # Editar con tus datos reales
```

---

## 📝 Variables de Entorno

```env
# ========== BASE DE DATOS ==========
DB_HOST=your-host.neon.tech
DB_NAME=neondb
DB_USER=neonuser
DB_PASS=your-secure-password
DB_PORT=5432

# ========== SEGURIDAD ==========
# Generar con: python3 generate_secrets.py
ADMIN_PASSWORD_HASH=$2b$12$...  # Debe ser hash bcrypt
SECRET_KEY=a1b2c3d4e5f6...      # 64 caracteres hex
ENCRYPTION_KEY=gAAAAAB...        # Clave Fernet

# ========== ENTORNO ==========
FLASK_ENV=production              # NUNCA development
DEBUG=False                        # NUNCA True
```

### ⚠️ Validaciones
- `DB_HOST`: Obligatorio
- `ADMIN_PASSWORD_HASH`: No puede ser texto plano
- `SECRET_KEY`: Debe tener mínimo 32 caracteres
- `ENCRYPTION_KEY`: Formato válido Fernet
- `FLASK_ENV`: SIEMPRE "production" en servers

---

## 📦 Instalación

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Generar Secretos
```bash
python3 generate_secrets.py
# Seguir las instrucciones interactivas
```

### 3. Configurar .env
```bash
nano .env
# Completar: DB_HOST, DB_USER, DB_PASS
```

### 4. Verificar Permiso de .env
```bash
chmod 600 .env  # Solo lectura para el propietario
ls -la .env     # Debe mostrar: -rw-------
```

### 5. Prueba Local
```bash
python3 app_seguro.py
# Acceder a http://localhost
```

---

## 🧪 Pruebas de Seguridad

### Test 1: Validación de PIN
```bash
# Intenta login con PIN incorrecto
POST /login
password=1234
# Resultado esperado: "PIN incorrecto" (sin stack trace)
```

### Test 2: Validación de Referencia
```bash
# Intenta con referencia inválida
POST /verificar
ref=123        # Muy corta
comanda=1
# Resultado esperado: "ENTRADA INVÁLIDA"

POST /verificar
ref=ABC123ABC123ABC123ABC  # Muy larga
comanda=1
# Resultado esperado: "ENTRADA INVÁLIDA"

POST /verificar
ref=ABC@#$      # Caracteres inválidos
comanda=1
# Resultado esperado: "ENTRADA INVÁLIDA"
```

### Test 3: Rate Limiting
```bash
# Intenta 6 logins en 1 minuto
for i in {1..6}; do
  curl -X POST http://localhost/login -d "password=test" &
done
# En el 6to intento:
# "Too Many Requests" (429)
```

### Test 4: CSRF Protection
```bash
# Intenta POST sin token CSRF
curl -X POST http://localhost/admin/liberar \
  -d "ref=ABC123&pw=1234"
# Resultado esperado: Error CSRF 400
```

### Test 5: SQL Injection
```bash
# Intenta inyección SQL
POST /verificar
ref=ABC123'; DROP TABLE pagos; --
comanda=1
# Resultado esperado: 
# - La entrada se rechaza por validación
# - Si pasa, psycopg2 usa parámetros preparados
# - Ningún SQL se ejecuta
```

### Test 6: Exposición de Contraseñas
```bash
# Verificar que .env no esté en public/
grep "ADMIN_PASSWORD_HASH" app_seguro.py
# No debe encontrarse en el código
```

---

## 🚀 Despliegue en Producción

### Cambios Obligatorios

**1. Cambiar de Flask Dev a Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:80 app_seguro:app
```

**2. Usar HTTPS/SSL:**
```nginx
# Nginx reverse proxy con SSL
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header X-Forwarded-For $remote_addr;
}
```

**3. Hardening Adicional:**
```python
# En app_seguro.py - línea final
if __name__ == '__main__':
    # NUNCA:
    # app.run(debug=True)
    
    # SI:
    app.run(host='127.0.0.1', port=8000, debug=False)
    # Usar Gunicorn en producción
```

**4. Firewall:**
```bash
# Solo permitir:
# - Puerto 80/443 (HTTP/HTTPS)
# - Puerto 22 (SSH) desde IPs confiables
# - Bloquear 5432 (PostgreSQL) de internet
```

**5. Backups de BD:**
```bash
# Diariamente
pg_dump -h your-host -U user dbname > backup_$(date +%Y%m%d).sql
```

**6. Monitoreo:**
```bash
# Logs en /var/log/sistemas_mv/
# Alertas si rate_limit > 10 por minuto
# Alertas si error_count > 5 por hora
```

---

## 📊 Comparación: Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| Autenticación | Texto plano | Bcrypt hash |
| CSRF | ❌ No | ✅ Sí |
| Validación | Mínima | Completa |
| Rate Limiting | ❌ No | ✅ Sí |
| Encriptación | ❌ No | ✅ Opcional |
| Sesiones | Hardcodeadas | Generadas |
| Logging | ❌ No | ✅ Auditoría |
| Manejo Errores | Stack traces | Genéricos |
| SQL Injection | Vulnerable | Protegido |
| DoS | Vulnerable | Limitado |

---

## 🆘 Solución de Problemas

### "Error: SECRET_KEY no está definida"
```bash
python3 generate_secrets.py
# Asegurate de haber copiado el valor a .env
```

### "BadSignature en sesiones"
```bash
rm -f flask_session/*
# Reinicia la app
# El SECRET_KEY debe ser consistente
```

### "429 Too Many Requests"
```bash
# Es normal si haces muchos requests rápido
# Espera 1 minuto y vuelve a intentar
# Aumenta límites en: limiter.limit("X per minute")
```

### "Error de conexión a BD"
```bash
# Verifica:
1. DB_HOST en .env (debe incluir puerto si es necesario)
2. DB_PASS correcta
3. IP del servidor está en whitelist de Neon
4. BD existe y es accesible
```

---

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/security/)
- [Werkzeug Security](https://werkzeug.palletsprojects.com/security/)
- [Cryptography.io](https://cryptography.io/)

---

## ✅ Checklist Pre-Producción

- [ ] Generar y verificar ADMIN_PASSWORD_HASH
- [ ] Generar y guardar SECRET_KEY en .env
- [ ] Completar todas las variables BD en .env
- [ ] Permisos de .env: 600
- [ ] .env NO está en .gitignore (verificar)
- [ ] SSL/HTTPS configurado
- [ ] Gunicorn/uWSGI en lugar de Flask dev
- [ ] Logs configurados
- [ ] Firewall configurado
- [ ] Backups automáticos activados
- [ ] Pruebas de seguridad pasadas
- [ ] Rate limits ajustados según uso real
- [ ] Monitoreo de errores activado

---

**Última actualización:** 2026-01-24
**Versión:** 2.0 - Hardened Security

# 📢 LÉEME PRIMERO - Cambio Importante

## 🎯 ¿Qué cambió?

**YA NO necesitas ejecutar `generate_secrets.py` antes de iniciar la aplicación.**

Las claves de seguridad ahora se generan **automáticamente** al ejecutar `python app.py`.

---

## ⚡ Inicio Rápido (3 pasos)

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar aplicación
```bash
python app.py
```

### 3. Cambiar PIN por defecto
El PIN inicial es `1234`. Cámbialo editando `.env`:

```bash
# Generar hash de tu nuevo PIN
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('tu-pin'))"

# Editar .env y reemplazar ADMIN_PASSWORD_HASH con el hash generado
notepad .env  # Windows
nano .env     # Linux/Mac
```

---

## ⚠️ IMPORTANTE

- **PIN por defecto:** `1234` (cámbialo inmediatamente)
- **Archivo .env:** Se crea automáticamente con las claves de seguridad
- **Base de datos:** Edita `.env` con tus credenciales de PostgreSQL

---

## 📚 Más Información

- `INSTRUCCIONES_ACTUALIZACION.md` - Guía completa de actualización
- `RESUMEN_CAMBIOS.md` - Detalles técnicos de los cambios
- `CAMBIOS_GENERACION_CLAVES.md` - Explicación del nuevo sistema
- `QUICKSTART.md` - Guía de inicio rápido actualizada

---

## 🗑️ Archivo Obsoleto

Puedes eliminar: `generate_secrets.py` (ya no es necesario)

---

*¡Listo! Tu aplicación está más simple y fácil de usar.*

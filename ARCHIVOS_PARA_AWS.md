# 📦 Archivos para Despliegue en AWS

## ✅ ARCHIVOS NECESARIOS (Mantener)

### Aplicación Principal
- ✅ `app.py` - Aplicación Flask principal con todas las mejoras
- ✅ `requirements.txt` - Dependencias Python
- ✅ `.env.example` - Plantilla de variables de entorno
- ✅ `.gitignore` - Ignorar archivos sensibles

### Scripts de Utilidad
- ✅ `create table.py` - Script para crear tablas en la BD
- ✅ `migrate.py` - Script de migración de BD (si es necesario)
- ✅ `test_db.py` - Script para probar conexión a BD

### Configuración de Servidor
- ✅ `nginx.conf.example` - Configuración de Nginx
- ✅ `deploy.sh` - Script de despliegue (actualizar para AWS)

### Documentación Esencial
- ✅ `LEEME_PRIMERO.md` - Guía de inicio rápido
- ✅ `CONFIGURACION_MACRODROID.md` - Configuración de MacroDroid
- ✅ `SEGURIDAD.md` - Documentación de seguridad

---

## ❌ ARCHIVOS A ELIMINAR (No necesarios para AWS)

### Archivos de Windows (No necesarios en Ubuntu)
- ❌ `install.bat` - Script de instalación Windows
- ❌ `install.ps1` - Script PowerShell Windows
- ❌ `WINDOWS_PASO_A_PASO.md` - Guía específica de Windows

### Archivos Obsoletos
- ❌ `main.py` - Versión antigua (ahora solo muestra advertencia)
- ❌ `generate_secrets.py` - Ya no necesario (generación automática)

### Documentación Redundante
- ❌ `CAMBIOS_GENERACION_CLAVES.md` - Documentación de cambios
- ❌ `CHANGELOG.md` - Historial de cambios
- ❌ `CHECKLIST.md` - Checklist de instalación
- ❌ `CUAL_ARCHIVO_USAR.md` - Ya no necesario
- ❌ `INDEX.md` - Índice general
- ❌ `INSTRUCCIONES_ACTUALIZACION.md` - Instrucciones de actualización
- ❌ `QUICKSTART.md` - Redundante con LEEME_PRIMERO.md
- ❌ `RESUMEN_CAMBIOS.md` - Resumen de cambios
- ❌ `RESUMEN_CORRECCIONES.txt` - Correcciones antiguas
- ❌ `RESUMEN_EJECUTIVO.md` - Resumen ejecutivo
- ❌ `RESUMEN_FINAL.md` - Resumen final
- ❌ `SOLUCION_DEFINITIVA.md` - Soluciones antiguas

### Documentación de Desarrollo
- ❌ `FLUJO_COMPLETO_SISTEMA.md` - Diagramas de flujo (útil pero no esencial)
- ❌ `MACRODROID_CONFIGURACION_RAPIDA.md` - Redundante con CONFIGURACION_MACRODROID.md
- ❌ `PRUEBAS_WEBHOOK.md` - Pruebas de desarrollo
- ❌ `VERIFICACION_ULTIMOS_6_DIGITOS.md` - Documentación técnica

---

## 📁 ESTRUCTURA FINAL PARA AWS

```
/home/ubuntu/pagos/
├── app.py                          ← Aplicación principal
├── requirements.txt                ← Dependencias
├── .env                            ← Variables de entorno (crear en servidor)
├── .env.example                    ← Plantilla
├── .gitignore                      ← Git ignore
├── create_table.py                 ← Script de BD
├── migrate.py                      ← Migraciones
├── test_db.py                      ← Test de conexión
├── nginx.conf.example              ← Config Nginx
├── deploy.sh                       ← Script de despliegue
├── LEEME_PRIMERO.md               ← Guía rápida
├── CONFIGURACION_MACRODROID.md    ← Config MacroDroid
└── SEGURIDAD.md                   ← Documentación seguridad
```

---

## 🗑️ TOTAL DE ARCHIVOS

- **Mantener:** 13 archivos
- **Eliminar:** 20+ archivos
- **Reducción:** ~60% de archivos

---

## 📝 NOTAS

1. El archivo `.env` NO debe subirse a Git (ya está en .gitignore)
2. Crear `.env` en el servidor AWS con las credenciales reales
3. Los archivos de documentación eliminados están en Git si se necesitan después
4. Los scripts de Windows no son necesarios en Ubuntu

---

*Lista creada: 2026-02-09*

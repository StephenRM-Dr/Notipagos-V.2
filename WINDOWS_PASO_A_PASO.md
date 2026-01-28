# 🪟 Guía de Instalación en Windows - Paso a Paso

## 🎯 Tu Situación

- ✅ Tienes Python 3.13 instalado
- ❌ pip intenta compilar pandas/psycopg2 (falla)
- ❌ No tienes compilador C++

**Solución:** Usa nuestros scripts que **NO necesitan compilador**

---

## ⚡ OPCIÓN MÁS FÁCIL (30 segundos)

### Método 1: Script .BAT (Recomendado)

1. **Descarga todos los archivos de `/mnt/user-data/outputs/`**
2. **Coloca `install.bat` en tu carpeta de proyecto:**
   ```
   C:\Users\Sistemas\Documents\pagos\install.bat
   ```

3. **Haz doble-click en `install.bat`**
   - Se abrirá Command Prompt automáticamente
   - Espera 3-5 minutos
   - Verás: `✅ INSTALACIÓN COMPLETADA`

4. **¡LISTO! Ahora ejecuta:**
   ```bash
   python generate_secrets.py
   ```

---

## 🔧 OPCIÓN 2: Script PowerShell

1. **Coloca `install.ps1` en tu carpeta:**
   ```
   C:\Users\Sistemas\Documents\pagos\install.ps1
   ```

2. **Abre PowerShell en esa carpeta:**
   - Click derecho en la carpeta
   - Selecciona "Open PowerShell here"

3. **Ejecuta:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File install.ps1
   ```

4. **Espera 3-5 minutos**

5. **¡LISTO!**

---

## 📝 OPCIÓN 3: Manual con un Comando

Si los scripts no funcionan, copia y pega esto en PowerShell:

```powershell
pip install --only-binary :all: Flask==3.0.0 Flask-WTF==1.2.1 Flask-Limiter==3.5.0 psycopg2-binary==2.9.9 cryptography==41.0.7 Werkzeug==3.0.1 python-dotenv==1.0.0 pytz==2023.3 openpyxl==3.1.2 pandas==2.0.3
```

Espera 5 minutos. ¡Listo!

---

## ✅ Verificar que Funcionó

Ejecuta esto en PowerShell:

```powershell
python -c "import flask, psycopg2, pandas; print('✅ TODO OK')"
```

Si ves `✅ TODO OK` → **¡FUNCIONA!**

---

## 🚀 Una vez Instalado

### 1. Generar secretos (interactivo)
```powershell
python generate_secrets.py
```

Responde las preguntas:
- PIN: Ej: `1234` (mínimo 4 dígitos)
- Selecciona guardar en `.env`

### 2. Editar .env
```powershell
notepad .env
```

Cambia SOLO estos 3 valores:
```env
DB_HOST=tu-host.neon.tech
DB_USER=neonuser
DB_PASS=tu-contraseña-segura
```

Guarda (Ctrl+S) y cierra.

### 3. Ejecutar Aplicación
```powershell
python app_seguro.py
```

Deberías ver:
```
 * Running on http://127.0.0.1:80
```

### 4. Acceder
Abre tu navegador: **http://localhost**

Usa tu PIN para entrar.

---

## 🆘 Problemas Comunes

### "install.bat no hace nada"
→ Haz doble-click más lentamente o abre PowerShell y ejecuta:
```powershell
C:\Users\Sistemas\Documents\pagos\install.bat
```

### "Se cerró la ventana muy rápido"
→ El script se completó. Es normal.
→ Verifica ejecutando:
```powershell
python -c "import pandas; print('OK')"
```

### "Sigue dando error de compilador"
→ Tu Python 3.13 tiene problemas
→ Solución: Desinstala Python 3.13, instala Python 3.11

**Pasos:**
1. Abre "Add or Remove Programs"
2. Busca "Python 3.13"
3. Click derecha → Desinstala
4. Descarga Python 3.11: https://www.python.org/downloads/
5. Instala marcando ✓ "Add Python to PATH"
6. Vuelve a ejecutar: `install.bat`

### "pip no es reconocido"
→ Python no está en PATH
→ Solución:
1. Desinstala Python
2. Reinstala marcando ✓ "Add Python to PATH"
3. Abre PowerShell NUEVA (cierra y abre de nuevo)
4. Vuelve a ejecutar

---

## 📋 Archivos que Necesitas

```
C:\Users\Sistemas\Documents\pagos\
├── install.bat              ← Haz doble-click AQUÍ
├── install.ps1              ← O ejecuta esto en PowerShell
├── app_seguro.py            ← Tu aplicación
├── generate_secrets.py      ← Generador de claves
├── requirements.txt         ← Dependencias (referencia)
├── .env.example            ← Plantilla de variables
└── [archivos de documentación]
```

---

## ⏱️ Tiempo Total

- Scripts automáticos: **5-10 minutos**
- Comando manual: **5-10 minutos**
- Toda la configuración: **10-15 minutos**

**TOTAL hasta tener todo corriendo: 20 minutos**

---

## 🎉 Checklist Final

- [ ] Descargué `install.bat` y `install.ps1`
- [ ] Coloqué los archivos en `C:\Users\Sistemas\Documents\pagos\`
- [ ] Ejecuté uno de los scripts (esperé 5 min)
- [ ] Ejecuté `python -c "import pandas; print('OK')"`
- [ ] Vi mensaje de éxito
- [ ] Ejecuté `python generate_secrets.py`
- [ ] Edité `.env` con datos reales
- [ ] Ejecuté `python app_seguro.py`
- [ ] Accedí a `http://localhost`
- [ ] ✅ **¡LISTO!**

---

## 💡 Recordatorios Importantes

⚠️ **NO cambies:** `app_seguro.py` ni archivos de config
✅ **SÍ cambia:** `.env` con tus datos reales
✅ **SÍ genera:** Secretos con `generate_secrets.py`
✅ **SÍ instala:** Dependencias con los scripts

---

## 📞 Si Nada Funciona

1. **Lee:** `SOLUCION_DEFINITIVA.md`
2. **Opción:** Usa Python 3.11 en lugar de 3.13
3. **Opción:** Instala Anaconda (trae compiladores)
4. **Opción:** Instala compilador Visual C++ Build Tools

---

*Guía actualizada: 2026-01-24*
*Plataforma: Windows 10/11*
*Python: 3.11+*

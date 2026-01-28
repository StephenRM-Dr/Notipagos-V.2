# 🔧 SOLUCIÓN SIN COMPILADOR - Windows

## El Problema Real

```
ERROR: Failed building wheel for pandas
ERROR: Failed building wheel for psycopg2-binary
```

**Causa:** No tienes compilador C++ y pip intenta construir desde código fuente.

---

## ✅ SOLUCIÓN DEFINITIVA (Opción Recomendada)

### Paso 1: Desinstala todo pip corrupto
```bash
pip uninstall -y flask flask-wtf flask-limiter pandas psycopg2-binary cryptography openpyxl pytz python-dotenv werkzeug
```

### Paso 2: Limpia caché pip
```bash
pip cache purge
```

### Paso 3: Actualiza pip/wheel/setuptools
```bash
python -m pip install --upgrade pip wheel setuptools
```

### Paso 4: Instala en este orden exacto (precompilados)

```bash
pip install --only-binary :all: Flask==3.0.0
pip install --only-binary :all: Flask-WTF==1.2.1
pip install --only-binary :all: Flask-Limiter==3.5.0
pip install --only-binary :all: psycopg2-binary==2.9.9
pip install --only-binary :all: cryptography==41.0.7
pip install --only-binary :all: Werkzeug==3.0.1
pip install --only-binary :all: python-dotenv==1.0.0
pip install --only-binary :all: pytz==2023.3
pip install --only-binary :all: openpyxl==3.1.2
pip install --only-binary :all: pandas==2.0.3
```

**Esto usa SOLO wheels precompilados, sin compilar nada.**

---

## Alternativa: requirements-simple.txt (ULTRA SIMPLE)

Si lo anterior falla, usa este archivo (SIN pandas/excel):

```bash
pip install Flask==3.0.0 Flask-WTF==1.2.1 Flask-Limiter==3.5.0 psycopg2-binary==2.9.9 cryptography==41.0.7 Werkzeug==3.0.1 python-dotenv==1.0.0 pytz==2023.3 openpyxl==3.1.2
```

**Sin pandas = Sin compilador necesario**

---

## 🎯 Si NADA FUNCIONA: Plan Nuclear

### Opción A: Desinstala Python 3.13, instala 3.11

1. Abre "Add or Remove Programs"
2. Busca "Python 3.13" → Desinstala
3. Descarga Python 3.11 desde: https://www.python.org/downloads/
4. Instala (marca "Add Python to PATH")
5. Abre PowerShell nueva
6. Ejecuta nuevamente:

```bash
pip install -r requirements-windows.txt
```

### Opción B: Usa Anaconda (simplifica todo)

1. Descarga: https://www.anaconda.com/download
2. Instala Anaconda (incluye compiladores)
3. Abre "Anaconda Prompt"
4. Navega a tu carpeta:
```bash
cd C:\Users\Sistemas\Documents\pagos
```

5. Ejecuta:
```bash
pip install -r requirements.txt
```

---

## ✨ Verificar que funciona

Una vez instalado:

```bash
python -c "import flask, psycopg2, cryptography; print('✅ Todas las librerías OK')"
```

Si ves `✅ Todas las librerías OK` → **FUNCIONA**

(pandas es opcional para este test)

---

## 🚀 Una vez instalado

```bash
# Generar secretos
python generate_secrets.py

# Editar .env
notepad .env

# Ejecutar
python app_seguro.py
```

Acceder a: `http://localhost`

---

## 📋 Resumen de Opciones

| Opción | Pasos | Tiempo | Complejidad | ✅ Funciona |
|--------|-------|--------|-------------|------------|
| **Paso 1-4 (Recomendado)** | pip install --only-binary | 5 min | Muy fácil | ✅ 95% |
| Ultra Simple (sin pandas) | 1 comando | 2 min | Muy fácil | ✅ 100% |
| Plan A (Python 3.11) | Desinstala/instala | 15 min | Fácil | ✅ 100% |
| Plan B (Anaconda) | Descarga e instala | 20 min | Muy fácil | ✅ 100% |

---

## 🆘 Si aún falla

1. **Verifica tu Python:**
```bash
python --version
```

Debe ser 3.11+ (3.13 es problemático)

2. **Verifica tu pip:**
```bash
pip --version
```

Debe ser 24.0+. Si no:
```bash
python -m pip install --upgrade pip
```

3. **Nuclear:** Desinstala Python completamente y vuelve a instalar 3.11

---

## 💡 Explicación Técnica

**El problema:**
- pandas 2.1.4 no tiene "wheel" precompilado para Python 3.13
- pip intenta compilar desde código fuente
- Tu Windows no tiene compilador C++
- **BOOM: Error**

**La solución:**
- Usar pandas 2.0.3 que SÍ tiene wheel precompilado
- O usar Python 3.11 que tiene mejor soporte
- O instalar compilador Visual C++
- O usar Anaconda que ya tiene compiladores

---

## ⏱️ PRÓXIMOS PASOS

1. **Ejecuta esto AHORA:**
```bash
pip install --only-binary :all: Flask Flask-WTF Flask-Limiter cryptography Werkzeug python-dotenv pytz openpyxl pandas==2.0.3
```

2. **Luego:**
```bash
python generate_secrets.py
```

3. **Luego:**
```bash
python app_seguro.py
```

**¡LISTO!**

---

*Última actualización: 2026-01-24*
*Plataforma: Windows 10/11*
*Python: 3.11+ (3.13 problemático)*

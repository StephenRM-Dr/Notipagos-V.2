#!/usr/bin/env python3
"""
Script de diagnóstico - Prueba conexión a BD
Ejecución: python test_db.py
"""

import psycopg2
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

print("\n" + "="*60)
print("  PRUEBA DE CONEXIÓN A BASE DE DATOS")
print("="*60 + "\n")

# Verificar variables
print("1️⃣  Verificando variables de entorno...")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_port = os.getenv("DB_PORT", "5432")

if not all([db_host, db_name, db_user, db_pass]):
    print("❌ ERROR: Falta alguna variable en .env")
    print(f"   DB_HOST: {db_host or '❌ VACIO'}")
    print(f"   DB_NAME: {db_name or '❌ VACIO'}")
    print(f"   DB_USER: {db_user or '❌ VACIO'}")
    print(f"   DB_PASS: {db_pass or '❌ VACIO'}")
    print(f"   DB_PORT: {db_port}")
    exit(1)

print(f"✅ Variables encontradas:")
print(f"   DB_HOST: {db_host}")
print(f"   DB_NAME: {db_name}")
print(f"   DB_USER: {db_user}")
print(f"   DB_PORT: {db_port}")

# Intentar conexión
print("\n2️⃣  Conectando a base de datos...")
try:
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_pass,
        port=db_port,
        sslmode="require" if "neon.tech" in db_host else "disable",
        connect_timeout=5
    )
    print("✅ Conexión exitosa!")
    
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión: {e}")
    print("\n   Posibles causas:")
    print("   1. DB_HOST incorrecto")
    print("   2. DB_USER o DB_PASS incorrecto")
    print("   3. Servidor BD inaccesible")
    print("   4. Firewall bloqueando puerto 5432")
    print("   5. IP no está en whitelist (Neon)")
    print("\n   Solución:")
    print("   - Verifica .env")
    print("   - Si usas Neon: Añade tu IP a whitelist en https://console.neon.tech")
    exit(1)

except Exception as e:
    print(f"❌ Error inesperado: {e}")
    exit(1)

# Verificar tabla
print("\n3️⃣  Verificando tabla 'pagos'...")
try:
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'pagos'
        )
    """)
    tabla_existe = cur.fetchone()[0]
    
    if tabla_existe:
        print("✅ Tabla 'pagos' existe")
        
        # Contar registros
        cur.execute("SELECT COUNT(*) FROM pagos")
        count = cur.fetchone()[0]
        print(f"   Registros: {count}")
        
    else:
        print("❌ Tabla 'pagos' NO existe")
        print("\n   Necesitas crearla. Opciones:")
        print("\n   A) Usar script create_table.py (recomendado)")
        print("   B) Ejecutar SQL manualmente en Neon console")
        print("\n   SQL para crear tabla:")
        print("""
        CREATE TABLE pagos (
            id SERIAL PRIMARY KEY,
            fecha_recepcion VARCHAR(50),
            hora_recepcion VARCHAR(50),
            emisor VARCHAR(100),
            monto VARCHAR(50),
            referencia VARCHAR(50) UNIQUE,
            mensaje_completo TEXT,
            fecha_canje VARCHAR(50),
            estado VARCHAR(50) DEFAULT 'LIBRE',
            comanda VARCHAR(50),
            banco VARCHAR(50),
            ip_canje VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        )
        """)
        
except Exception as e:
    print(f"❌ Error verificando tabla: {e}")
    exit(1)

finally:
    cur.close()
    conn.close()

print("\n" + "="*60)
print("  ✅ DIAGNÓSTICO COMPLETADO")
print("="*60)
print("\nEstado:")
print("✅ Conexión a BD: OK")
print("✅ Tabla existe: OK" if tabla_existe else "❌ Tabla NO existe")
print("\nPróximo paso:")
if tabla_existe:
    print("→ Ejecuta: python app_seguro_simple.py")
else:
    print("→ Crea la tabla primero")
    print("→ Luego ejecuta: python app_seguro_simple.py")

print()
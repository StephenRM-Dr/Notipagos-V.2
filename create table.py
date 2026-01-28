#!/usr/bin/env python3
"""
Script para crear tabla 'pagos' en PostgreSQL
Ejecución: python create_table.py
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

print("\n" + "="*60)
print("  CREAR TABLA 'pagos'")
print("="*60 + "\n")

try:
    # Conectar
    print("Conectando a BD...")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432"),
        sslmode="require" if "neon.tech" in (os.getenv("DB_HOST") or "") else "disable",
        connect_timeout=5
    )
    print("✅ Conexión exitosa\n")
    
    cur = conn.cursor()
    
    # Crear tabla
    print("Creando tabla 'pagos'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
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
    
    conn.commit()
    print("✅ Tabla creada exitosamente\n")
    
    # Verificar
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'pagos'
        )
    """)
    
    if cur.fetchone()[0]:
        print("✅ Tabla verificada - ¡Lista para usar!\n")
        
        # Crear índices para mejor performance
        print("Creando índices...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_referencia ON pagos(referencia)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_estado ON pagos(estado)")
        conn.commit()
        print("✅ Índices creados\n")
    
    cur.close()
    conn.close()
    
    print("="*60)
    print("  ✅ TABLA CREADA EXITOSAMENTE")
    print("="*60)
    print("\nPróximo paso:")
    print("→ Ejecuta: python app_seguro_simple.py")
    print()
    
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión: {e}\n")
    print("Causas posibles:")
    print("  1. Credenciales incorrectas en .env")
    print("  2. Base de datos no existe")
    print("  3. IP no está en whitelist (Neon)")
    exit(1)
    
except psycopg2.ProgrammingError as e:
    print(f"❌ Error SQL: {e}\n")
    print("Soluciones:")
    print("  1. Verifica que .env tenga DB_NAME correcto")
    print("  2. Verifica que usuario tenga permisos")
    exit(1)
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    exit(1)
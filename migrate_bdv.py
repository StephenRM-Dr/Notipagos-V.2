#!/usr/bin/env python3
"""
Script para agregar columnas de validación BDV a la tabla pagos
Ejecución: python migrate_bdv.py
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

print("\n" + "="*60)
print("  MIGRACIÓN: Agregar columnas BDV a tabla 'pagos'")
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
    
    # Agregar columnas si no existen
    print("Agregando columnas para validación BDV...")
    
    columnas_nuevas = [
        ("cedula_pagador", "VARCHAR(20)"),
        ("telefono_pagador", "VARCHAR(20)"),
        ("banco_origen", "VARCHAR(10)"),
        ("estado_bdv", "VARCHAR(10)"),
        ("fecha_validacion", "TIMESTAMP"),
        ("fecha_pago", "DATE")
    ]
    
    for columna, tipo in columnas_nuevas:
        try:
            cur.execute(f"""
                ALTER TABLE pagos 
                ADD COLUMN IF NOT EXISTS {columna} {tipo}
            """)
            print(f"  ✅ Columna '{columna}' agregada")
        except Exception as e:
            print(f"  ⚠️  Columna '{columna}': {e}")
    
    conn.commit()
    
    # Crear índices adicionales
    print("\nCreando índices adicionales...")
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_cedula ON pagos(cedula_pagador)",
        "CREATE INDEX IF NOT EXISTS idx_telefono ON pagos(telefono_pagador)",
        "CREATE INDEX IF NOT EXISTS idx_fecha_pago ON pagos(fecha_pago)"
    ]
    
    for idx in indices:
        try:
            cur.execute(idx)
            print(f"  ✅ Índice creado")
        except Exception as e:
            print(f"  ⚠️  {e}")
    
    conn.commit()
    
    # Verificar estructura final
    print("\nVerificando estructura de la tabla...")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'pagos'
        ORDER BY ordinal_position
    """)
    
    columnas = cur.fetchall()
    print("\nColumnas en la tabla 'pagos':")
    for col in columnas:
        print(f"  - {col[0]}: {col[1]}")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    print("  ✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\nLa tabla 'pagos' ahora soporta validación BDV")
    print()
    
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión: {e}\n")
    exit(1)
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

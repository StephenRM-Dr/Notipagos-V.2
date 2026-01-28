#!/usr/bin/env python3
"""
Script de migración - Agregar columnas faltantes a tabla 'pagos'
Ejecución: python migrate_table.py
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

print("\n" + "="*60)
print("  MIGRACIÓN DE TABLA 'pagos'")
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
    
    # Verificar qué columnas existen
    print("Verificando estructura actual...")
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'pagos'
        ORDER BY ordinal_position
    """)
    
    columnas_existentes = [row[0] for row in cur.fetchall()]
    print(f"Columnas actuales: {', '.join(columnas_existentes)}\n")
    
    # Definir columnas que deben existir
    columnas_requeridas = [
        'id', 'fecha_recepcion', 'hora_recepcion', 'emisor', 'monto',
        'referencia', 'mensaje_completo', 'fecha_canje', 'estado',
        'comanda', 'banco', 'ip_canje'
    ]
    
    # Agregar columnas faltantes
    columnas_faltantes = [col for col in columnas_requeridas if col not in columnas_existentes]
    
    if columnas_faltantes:
        print(f"Columnas faltantes: {', '.join(columnas_faltantes)}\n")
        print("Agregando columnas...")
        
        # Mapeo de columnas y sus definiciones
        definiciones = {
            'comanda': "VARCHAR(50)",
            'banco': "VARCHAR(50)",
            'ip_canje': "VARCHAR(50)",
            'estado': "VARCHAR(50) DEFAULT 'LIBRE'",
            'fecha_canje': "VARCHAR(50)",
            'mensaje_completo': "TEXT"
        }
        
        for col in columnas_faltantes:
            if col in definiciones:
                sql = f"ALTER TABLE pagos ADD COLUMN IF NOT EXISTS {col} {definiciones[col]}"
                try:
                    cur.execute(sql)
                    print(f"  ✅ Agregada columna: {col}")
                except psycopg2.Error as e:
                    print(f"  ⚠️  Error en {col}: {e}")
                    # Continuar con otras columnas
        
        conn.commit()
        print("\n✅ Migración completada\n")
    
    else:
        print("✅ Todas las columnas existen - Sin cambios necesarios\n")
    
    # Verificar resultado final
    print("Verificando resultado final...")
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'pagos'
        ORDER BY ordinal_position
    """)
    
    columnas_finales = [row[0] for row in cur.fetchall()]
    print(f"Columnas finales: {', '.join(columnas_finales)}\n")
    
    # Crear índices si no existen
    print("Creando índices para mejor performance...")
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_referencia ON pagos(referencia)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_estado ON pagos(estado)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_banco ON pagos(banco)")
        conn.commit()
        print("✅ Índices creados\n")
    except:
        pass
    
    cur.close()
    conn.close()
    
    print("="*60)
    print("  ✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\nPróximo paso:")
    print("→ Ejecuta: python app_seguro_simple.py")
    print()
    
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión: {e}\n")
    exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
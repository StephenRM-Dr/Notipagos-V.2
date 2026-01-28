#!/usr/bin/env python3
"""
Script para generar hashes seguros y claves de encriptación
Ejecutar: python3 generate_secrets.py
"""

import os
import secrets
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet

def generar_secrets():
    print("\n" + "="*70)
    print("GENERADOR DE SECRETOS SEGUROS - SISTEMAS MV")
    print("="*70 + "\n")
    
    # 1. Generar PIN Admin
    print("1️⃣  PIN DE ADMINISTRADOR")
    print("-" * 70)
    pin = input("   Ingresa tu PIN deseado (mínimo 4 dígitos): ").strip()
    
    if len(pin) < 4:
        print("   ❌ El PIN debe tener al menos 4 caracteres")
        return
    
    pin_hash = generate_password_hash(pin)
    print(f"   ✅ Hash generado (usar en .env):")
    print(f"   ADMIN_PASSWORD_HASH={pin_hash}\n")
    
    # 2. Generar SECRET_KEY para sesiones
    print("2️⃣  SECRET_KEY PARA SESIONES")
    print("-" * 70)
    secret_key = secrets.token_hex(32)
    print(f"   ✅ Clave generada (usar en .env):")
    print(f"   SECRET_KEY={secret_key}\n")
    
    # 3. Generar ENCRYPTION_KEY
    print("3️⃣  ENCRYPTION_KEY PARA DATOS")
    print("-" * 70)
    encryption_key = Fernet.generate_key().decode()
    print(f"   ✅ Clave generada (usar en .env):")
    print(f"   ENCRYPTION_KEY={encryption_key}\n")
    
    # 4. Crear plantilla .env
    print("4️⃣  PLANTILLA .env LISTA")
    print("-" * 70)
    
    env_content = f"""# BASE DE DATOS
DB_HOST=your-db-host.neon.tech
DB_NAME=neondb
DB_USER=neonuser
DB_PASS=your-password
DB_PORT=5432

# SEGURIDAD - GENERADOS AUTOMÁTICAMENTE
ADMIN_PASSWORD_HASH={pin_hash}
SECRET_KEY={secret_key}
ENCRYPTION_KEY={encryption_key}

# ENTORNO
FLASK_ENV=production
"""
    
    print("   Contenido recomendado para .env:")
    print("   " + env_content.replace('\n', '\n   '))
    
    # Opción de guardar
    print("\n5️⃣  GUARDAR EN ARCHIVO")
    print("-" * 70)
    guardar = input("   ¿Deseas guardar en .env? (s/n): ").strip().lower()
    
    if guardar == 's':
        if os.path.exists('.env'):
            backup = input("   El archivo .env ya existe. ¿Hacer backup? (s/n): ").strip().lower()
            if backup == 's':
                os.rename('.env', '.env.backup')
                print("   ✅ Backup creado: .env.backup")
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("   ✅ Archivo .env creado exitosamente")
        os.chmod('.env', 0o600)  # Permisos restrictivos
        print("   🔒 Permisos restringidos (600) aplicados")
    
    print("\n" + "="*70)
    print("⚠️  IMPORTANTE:")
    print("   1. Guarda estos valores en un lugar seguro")
    print("   2. Completa manualmente DB_HOST, DB_USER, DB_PASS en .env")
    print("   3. NUNCA commits .env al repositorio")
    print("   4. Usa .env.example para documentar variables necesarias")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        generar_secrets()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")

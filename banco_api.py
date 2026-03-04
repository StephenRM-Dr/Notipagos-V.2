"""
Módulo de integración con API de Conciliación BDV
Versión: 1.0 - Producción
"""
import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar configuración
load_dotenv()


def limpiar_referencia(texto):
    """Normaliza referencia eliminando caracteres especiales y ceros a la izquierda"""
    if not texto:
        return ""
    limpio = "".join(filter(str.isalnum, str(texto)))
    return limpio.lstrip('0') or limpio  # Mantener al menos un cero si todo es cero


def obtener_conexion():
    """Obtiene conexión a la base de datos PostgreSQL"""
    try:
        return psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME'),
            port=os.getenv('DB_PORT', '5432'),
            sslmode='require' if 'neon.tech' in (os.getenv('DB_HOST') or '') else 'prefer',
            connect_timeout=10
        )
    except Exception as e:
        logger.error(f"Error de conexión a BD: {e}")
        raise


def validar_pago_bdv(referencia, banco_origen, cedula_pagador=None, telefono_pagador=None, 
                     fecha_pago=None, importe=None):
    """
    Valida un pago móvil contra el API de Conciliación BDV.
    
    Args:
        referencia (str): Número de referencia del pago (REQUERIDO)
        banco_origen (str): Código del banco de 4 dígitos (REQUERIDO)
        cedula_pagador (str): Cédula del pagador (opcional)
        telefono_pagador (str): Teléfono del pagador (opcional)
        fecha_pago (str): Fecha en formato YYYY-MM-DD (opcional)
        importe (str): Monto con 2 decimales (opcional)
    
    Returns:
        dict: {
            'success': bool,
            'code': int|str,
            'message': str,
            'amount': str (si success=True),
            'status': str (si success=True),
            'reason': str (si success=True)
        }
    """
    ambiente = os.getenv('BDV_AMBIENTE', 'produccion')
    
    # MODO SIMULACIÓN (solo para desarrollo)
    if ambiente == 'simulacion':
        logger.info(f"SIMULACIÓN - Ref: {referencia}, Banco: {banco_origen}")
        return {
            'success': True,
            'code': 1000,
            'message': 'Transaccion realizada (SIMULADO)',
            'amount': importe or '100.00',
            'status': '1000',
            'reason': 'Transaccion realizada (SIMULADO)'
        }
    
    # Validaciones
    if not referencia or not banco_origen:
        return {
            'success': False,
            'code': 'VALIDATION_ERROR',
            'message': 'Referencia y banco son obligatorios'
        }
    
    # Configuración del API
    api_key = os.getenv('BDV_API_KEY')
    if not api_key or api_key == 'TU_API_KEY_DE_PRODUCCION_AQUI':
        logger.error("API Key no configurado")
        return {
            'success': False,
            'code': 'CONFIG_ERROR',
            'message': 'API Key no configurado. Contacte al administrador.'
        }
    
    url = os.getenv('BDV_API_URL', 'https://bdvconciliacion.banvenez.com:443/getMovement')
    
    # Valores por defecto para campos obligatorios del API
    cedula_pagador = cedula_pagador or "V00000000"
    telefono_pagador = telefono_pagador or "04120000000"
    telefono_destino = telefono_pagador
    fecha_pago = fecha_pago or datetime.now().strftime("%Y-%m-%d")
    importe = importe or "0.01"
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "cedulaPagador": cedula_pagador,
        "telefonoPagador": telefono_pagador,
        "telefonoDestino": telefono_destino,
        "referencia": referencia,
        "fechaPago": fecha_pago,
        "importe": importe,
        "bancoOrigen": banco_origen
    }
    
    try:
        logger.info(f"Validando pago - Ref: {referencia}, Banco: {banco_origen}")
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=30,
            verify=True
        )
        
        if response.status_code == 200:
            resultado = response.json()
            
            # Código 1000 = Transacción exitosa
            if resultado.get('code') == 1000:
                monto_validado = resultado.get('data', {}).get('amount', importe)
                logger.info(f"✅ Pago validado - Ref: {referencia}, Monto: {monto_validado}")
                
                return {
                    'success': True,
                    'code': resultado.get('code'),
                    'message': resultado.get('message'),
                    'amount': monto_validado,
                    'status': resultado.get('data', {}).get('status'),
                    'reason': resultado.get('data', {}).get('reason')
                }
            else:
                # Código 1010 u otros = Error
                logger.warning(f"❌ Pago no validado - Ref: {referencia}, Código: {resultado.get('code')}")
                return {
                    'success': False,
                    'code': resultado.get('code'),
                    'message': resultado.get('message'),
                    'data': resultado.get('data')
                }
        else:
            logger.error(f"Error HTTP {response.status_code} - Ref: {referencia}")
            return {
                'success': False,
                'code': response.status_code,
                'message': f"Error HTTP: {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout - Ref: {referencia}")
        return {
            'success': False,
            'code': 'TIMEOUT',
            'message': 'Tiempo de espera agotado. Intente nuevamente.'
        }
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexión - Ref: {referencia}: {e}")
        return {
            'success': False,
            'code': 'CONNECTION_ERROR',
            'message': 'Error de conexión con el banco. Verifique su red.'
        }
    except Exception as e:
        logger.error(f"Error inesperado - Ref: {referencia}: {e}")
        return {
            'success': False,
            'code': 'ERROR',
            'message': 'Error interno del sistema.'
        }


def registrar_pago_validado(cedula, telefono, referencia, monto, banco_origen, datos_bdv):
    """
    Registra un pago validado en la base de datos.
    
    Args:
        cedula (str): Cédula del pagador
        telefono (str): Teléfono del pagador
        referencia (str): Referencia del pago
        monto (str): Monto del pago
        banco_origen (str): Código del banco
        datos_bdv (dict): Datos de respuesta del BDV
    
    Returns:
        bool: True si se registró exitosamente, False en caso contrario
    """
    try:
        conexion = obtener_conexion()
        
        with conexion.cursor() as cursor:
            ref_limpia = limpiar_referencia(referencia)
            
            sql = """
                INSERT INTO pagos 
                (cedula_pagador, telefono_pagador, referencia, monto, banco_origen, 
                 estado_bdv, fecha_validacion, fecha_registro, estado, banco) 
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 'LIBRE', %s)
                ON CONFLICT (referencia) DO NOTHING
                RETURNING id
            """
            
            cursor.execute(sql, (
                cedula, 
                telefono, 
                ref_limpia, 
                monto, 
                banco_origen,
                datos_bdv.get('status', '1000'),
                'BDV' if banco_origen == '0102' else banco_origen
            ))
            
            resultado = cursor.fetchone()
            conexion.commit()
            
            if resultado:
                logger.info(f"✅ Pago registrado - ID: {resultado[0]}, Ref: {ref_limpia}")
                return True
            else:
                logger.warning(f"⚠️ Pago ya existe - Ref: {ref_limpia}")
                return False
        
    except Exception as e:
        logger.error(f"❌ Error al registrar pago - Ref: {referencia}: {e}")
        return False
    finally:
        if 'conexion' in locals():
            conexion.close()


# Ejemplo de uso (solo para pruebas)
if __name__ == "__main__":
    print("Módulo banco_api.py - Listo para producción")
    print(f"Ambiente: {os.getenv('BDV_AMBIENTE', 'produccion')}")
    print(f"API URL: {os.getenv('BDV_API_URL', 'https://bdvconciliacion.banvenez.com:443/getMovement')}")

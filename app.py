import psycopg2
import re
import os
import pandas as pd
import pytz
import secrets
from flask import Flask, request, render_template_string, redirect, url_for, session, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from io import BytesIO
from dotenv import load_dotenv, set_key
import logging

# --- GENERACIÓN AUTOMÁTICA DE CLAVES ---
def generar_claves_automaticas():
    """Genera automáticamente las claves necesarias si no existen en .env"""
    env_path = '.env'
    env_modificado = False
    
    # Cargar variables actuales
    load_dotenv(override=True)
    
    # Verificar y generar SECRET_KEY
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key or secret_key == "clave_sistemas_mv_2026":
        nuevo_secret = secrets.token_hex(32)
        set_key(env_path, "SECRET_KEY", nuevo_secret)
        os.environ["SECRET_KEY"] = nuevo_secret
        print(f"✅ SECRET_KEY generada automáticamente")
        env_modificado = True
    
    # Verificar y generar ENCRYPTION_KEY
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        nueva_encryption = Fernet.generate_key().decode()
        set_key(env_path, "ENCRYPTION_KEY", nueva_encryption)
        os.environ["ENCRYPTION_KEY"] = nueva_encryption
        print(f"✅ ENCRYPTION_KEY generada automáticamente")
        env_modificado = True
    
    # Verificar y generar ADMIN_PASSWORD_HASH (PIN por defecto: 1234)
    admin_hash = os.getenv("ADMIN_PASSWORD_HASH")
    if not admin_hash:
        pin_default = "1234"
        nuevo_hash = generate_password_hash(pin_default)
        set_key(env_path, "ADMIN_PASSWORD_HASH", nuevo_hash)
        os.environ["ADMIN_PASSWORD_HASH"] = nuevo_hash
        print(f"⚠️  ADMIN_PASSWORD_HASH generado con PIN por defecto: {pin_default}")
        print(f"   CAMBIA EL PIN INMEDIATAMENTE en el archivo .env")
        env_modificado = True
    
    if env_modificado:
        print(f"\n🔒 Claves de seguridad actualizadas en {env_path}")
        print(f"   Revisa el archivo y ajusta las credenciales de base de datos si es necesario\n")

# --- CONFIGURACIÓN ---
generar_claves_automaticas()
load_dotenv(override=True)
app = Flask(__name__)

# Obtener SECRET_KEY (ya garantizada por la función anterior)
secret_key = os.getenv("SECRET_KEY")
app.secret_key = secret_key
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Zona Horaria de Venezuela
VET = pytz.timezone('America/Caracas')

# Encriptación para datos sensibles (ya garantizada por la función de generación automática)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

# --- VALIDADORES ---
def validar_referencia(ref):
    """Valida formato de referencia (alfanumérico, 6-20 caracteres)"""
    if not ref or not isinstance(ref, str):
        return False
    ref = ref.strip()
    if len(ref) < 6 or len(ref) > 20:
        return False
    return bool(re.match(r'^[A-Za-z0-9]+$', ref))

def validar_comanda(comanda):
    """Valida formato de comanda (numérico, 1-50 caracteres)"""
    if not comanda or not isinstance(comanda, str):
        return False
    comanda = comanda.strip()
    if len(comanda) < 1 or len(comanda) > 50:
        return False
    return bool(re.match(r'^[A-Za-z0-9\-#]+$', comanda))

def validar_monto(monto):
    """Valida formato de monto (numérico con máximo 2 decimales)"""
    if not monto or not isinstance(monto, str):
        return False
    try:
        val = float(monto.replace('.', '').replace(',', '.'))
        return 0.01 <= val <= 999999999.99
    except:
        return False

def obtener_ip_real():
    """Obtiene la IP real considerando proxies"""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0].strip()
    return request.remote_addr

def encriptar_dato(dato):
    """Encripta un dato sensible"""
    if not dato:
        return None
    return cipher_suite.encrypt(str(dato).encode()).decode()

def desencriptar_dato(dato):
    """Desencripta un dato sensible"""
    if not dato:
        return None
    try:
        return cipher_suite.decrypt(dato.encode()).decode()
    except:
        return None

# --- CONEXIÓN BASE DE DATOS (CON VALIDACIÓN) ---
def get_db_connection():
    """Obtiene conexión a BD con manejo de errores"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "5432"),
            sslmode="require" if "neon.tech" in (os.getenv("DB_HOST") or "") else "disable",
            connect_timeout=5
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error de conexión BD: {e}")
        raise Exception("Error de conexión a la base de datos")

# --- EXTRACTOR INTELIGENTE (v16 - MEJORADO) ---
def extractor_inteligente(texto):
    """Extrae pagos de texto con validación"""
    texto_limpio = texto.replace('"', '').replace('\\n', ' ').replace('\n', ' ').strip()
    pagos_detectados = []
    
    # Validar longitud máxima del texto (prevenir DoS)
    if len(texto_limpio) > 5000:
        logger.warning("Texto excesivamente largo en extractor")
        return []
    
    patrones = {
        "BDV": (r"BDV|PagomovilBDV", r"(?:del|tlf|desde el tlf)\s*(\d+)", r"(?:por|Bs\.?|Monto:)\s*([\d.]+,\d{2})", r"Ref:\s*(\d+)"),
        "BANESCO": (r"Banesco", r"(?:de|desde|tlf)\s*(\d+)", r"(?:Bs\.?|Monto:?)\s*([\d.]+,\d{2})", r"Ref:\s*(\d+)"),
        "SOFITASA": (r"SOFITASA", r"Telf\.?([\d*]+)", r"Bs\.?\s*([\d,.]+)", r"Ref[:\s]*(\d+)"),
        "BINANCE": (r"Binance", r"(?:from|de)\s+(.*?)\s", r"([\d.]+)\s*USDT", r"(?:ID|Order)[:\s]+(\d+)"),
        "PLAZA": (r"Plaza", r"Celular\s+([\d]+)", r"(?:BS\.?|por)\s*([\d,.]+)", r"Ref[\.:]\s*(\d+)")
    }

    for banco, (key, re_emi, re_mon, re_ref) in patrones.items():
        if re.search(key, texto_limpio, re.IGNORECASE):
            m_emi = re.search(re_emi, texto_limpio, re.IGNORECASE)
            m_mon = re.search(re_mon, texto_limpio, re.IGNORECASE)
            m_ref = re.search(re_ref, texto_limpio, re.IGNORECASE)
            
            if m_ref:
                referencia = m_ref.group(1)
                
                # Validar referencia extraída
                if not validar_referencia(referencia):
                    logger.warning(f"Referencia inválida detectada: {referencia}")
                    continue
                
                monto_raw = m_mon.group(1) if m_mon else "0,00"
                
                # Validar monto
                if not validar_monto(monto_raw):
                    logger.warning(f"Monto inválido detectado: {monto_raw}")
                    continue
                
                pagos_detectados.append({
                    "banco": banco, 
                    "emisor": m_emi.group(1) if m_emi else "S/D", 
                    "monto": monto_raw, 
                    "referencia": referencia,
                    "original": texto_limpio[:500]  # Limitar texto almacenado
                })
    
    return pagos_detectados

# --- ESTILOS CSS PREMIUM (IGUAL AL ORIGINAL) ---
CSS_FINAL = '''
:root { 
    --primary: #004481; --secondary: #f4f7f9; --danger: #d9534f; --success: #28a745; --warning: #ffc107;
    --bdv: #D32F2F; --banesco: #007A33; --binance: #F3BA2F; --plaza: #005691; --sofitasa: #0097A7;
}
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--secondary); margin: 0; min-height: 100vh; display: flex; flex-direction: column; }
.container { width: 100%; max-width: 1250px; margin: auto; padding: 20px; flex: 1; }
.card { background: white; border-radius: 18px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); padding: 30px; margin-bottom: 25px; text-align: center; }
.nav-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; flex-wrap: wrap; gap: 15px; }
.btn { border: none; border-radius: 12px; padding: 14px 24px; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 10px; transition: 0.3s; justify-content: center; font-size: 14px; }
.btn-primary { background: var(--primary); color: white; }
.btn-light { background: #fff; color: #555; border: 1px solid #ddd; }
.btn-danger { background: var(--danger); color: white; }
.btn-success { background: var(--success); color: white; }
.btn-warning { background: var(--warning); color: #333; }
.table-wrapper { width: 100%; overflow-x: auto; background: white; border-radius: 18px; border: 1px solid #eee; }
table { width: 100%; border-collapse: collapse; min-width: 1100px; text-align: center; }
th { background: #fcfcfc; padding: 18px; font-size: 11px; color: #888; border-bottom: 2px solid #eee; text-transform: uppercase; }
td { padding: 18px; border-bottom: 1px solid #f1f1f1; font-size: 13px; vertical-align: middle; }
.badge { padding: 8px 16px; border-radius: 25px; font-weight: bold; font-size: 10px; text-transform: uppercase; color: white; display: inline-block; }
.badge-bdv { background: var(--bdv); } .badge-sofitasa { background: var(--sofitasa); } .badge-plaza { background: var(--plaza); } .badge-binance { background: var(--binance); color: #000; } .badge-banesco { background: var(--banesco); }
input { border: 2px solid #eee; border-radius: 12px; padding: 15px; outline: none; width: 100%; max-width: 100%; text-align: center; font-size: 16px; transition: 0.3s; box-sizing: border-box; word-break: break-word; overflow-wrap: break-word; }
input:focus { border-color: var(--primary); background: #fdfdfd; }
.notif-pago { border-radius: 15px; padding: 25px; margin-top: 25px; border: 1px solid rgba(0,0,0,0.05); text-align: left; }
.notif-success { background: #e8f5e9; border-left: 6px solid var(--success); color: #1b5e20; }
.notif-error { background: #ffebee; border-left: 6px solid var(--danger); color: #b71c1c; }
.notif-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
.notif-item { background: rgba(255,255,255,0.6); padding: 10px; border-radius: 10px; }
.notif-label { font-size: 9px; text-transform: uppercase; opacity: 0.8; display: block; font-weight: bold; }
.grid-totales { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-top: 25px; }
.total-item { padding: 25px; border-radius: 20px; color: white; font-weight: bold; font-size: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
.error-msg { color: #d9534f; font-size: 12px; margin-top: 5px; }
@media (max-width: 600px) { .nav-header { justify-content: center; } .btn { width: 100%; } .notif-grid { grid-template-columns: 1fr; } }
'''

# --- VISTAS HTML ---
HTML_LOGIN = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>''' + CSS_FINAL + '''</style></head><body><div style="display:flex; align-items:center; justify-content:center; min-height:100vh; background: radial-gradient(circle at top, #004481 0%, #001a33 100%); padding: 20px;"><div class="card" style="width:100%; max-width:420px; border:none;"> <h1 style="color:var(--primary); margin-bottom:5px;">SISTEMAS MV</h1><p style="color:#777; margin-bottom:25px;">Control Administrativo v2026</p><form method="POST"><input type="password" name="password" placeholder="PIN de Seguridad" style="margin-bottom:20px;" autofocus required><button class="btn btn-primary" style="width:100%;">ENTRAR AL SISTEMA</button></form>{% if error %}<p class="error-msg">{{ error }}</p>{% endif %}<hr style="margin:25px 0; border:0; border-top:1px solid #eee;"><a href="/" class="btn btn-light" style="width:100%;">🔍 IR AL VERIFICADOR</a></div></div></body></html>'''

HTML_PORTAL = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>''' + CSS_FINAL + '''</style></head><body><div class="container"><div style="max-width:550px; margin: 40px auto 0; padding: 0 20px;"><div class="nav-header"><a href="/" class="btn btn-light">🔄 Recargar</a><a href="/login" class="btn btn-primary">⚙️ Acceso Admin</a></div><div class="card"><h2>Verificar Transacción</h2><p style="color:#888; font-size:14px; margin-bottom:25px;">Ingrese los datos para validar su comanda</p><form method="POST" action="/verificar"><input type="text" name="ref" placeholder="Últimos 6 dígitos o Referencia completa" style="margin-bottom:15px;" required minlength="6"><input type="text" name="comanda" placeholder="Nro de Comanda / Orden" style="margin-bottom:25px;" required><button class="btn btn-primary" style="width:100%; padding:18px;">VALIDAR AHORA</button></form>
{% if resultado %}
    <div class="notif-pago notif-{{ resultado.clase }}">
        <div style="display:flex; align-items:center; gap:10px;"><strong style="font-size:18px;">{{ resultado.titulo }}</strong></div>
        <p style="margin:10px 0; font-size:14px;">{{ resultado.mensaje }}</p>
        {% if resultado.datos %}
        <div class="notif-grid">
            <div class="notif-item"><span class="notif-label">Banco</span><strong>{{ resultado.datos.banco }}</strong></div>
            <div class="notif-item"><span class="notif-label">Monto</span><strong>Bs. {{ resultado.datos.monto }}</strong></div>
            <div class="notif-item"><span class="notif-label">Referencia</span><code>{{ resultado.datos.ref }}</code></div>
            <div class="notif-item"><span class="notif-label">Comanda</span><strong>#{{ resultado.datos.comanda }}</strong></div>
            <div class="notif-item" style="grid-column: span 2;"><span class="notif-label">Registro VET (Hora Local)</span><small>{{ resultado.datos.fecha }} | IP: {{ resultado.datos.ip }}</small></div>
        </div>
        {% endif %}
    </div>
{% endif %}
</div></div></div></body></html>'''

HTML_ADMIN = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>''' + CSS_FINAL + '''
.pagination { display: flex; justify-content: center; align-items: center; gap: 10px; margin: 25px 0; flex-wrap: wrap; }
.pagination a, .pagination span { padding: 10px 15px; border-radius: 8px; text-decoration: none; font-weight: 600; transition: 0.3s; }
.pagination a { background: white; color: var(--primary); border: 2px solid var(--primary); }
.pagination a:hover { background: var(--primary); color: white; }
.pagination .active { background: var(--primary); color: white; border: 2px solid var(--primary); }
.pagination .disabled { background: #f0f0f0; color: #999; border: 2px solid #ddd; cursor: not-allowed; }
.pagination-info { text-align: center; color: #666; font-size: 14px; margin: 15px 0; }
.per-page-selector { display: flex; justify-content: center; align-items: center; gap: 10px; margin: 15px 0; }
.per-page-selector select { padding: 8px 12px; border-radius: 8px; border: 2px solid #ddd; font-size: 14px; cursor: pointer; }
.search-form { display: flex; gap: 10px; align-items: center; }
.search-form input[type="text"] { flex: 1; }
.search-form button { white-space: nowrap; }
</style></head><body><div class="container"><div class="nav-header"><h2>Panel de Control</h2><div style="display:flex; gap:10px; flex-wrap:wrap;"><a href="/" class="btn btn-light">🔍 Verificador</a><a href="/admin/exportar" class="btn btn-success">📊 Excel</a><a href="/logout" class="btn btn-danger">🚪 Salir</a></div></div>

<div class="pagination-info">
    {% if paginacion.search %}
        Resultados de búsqueda: <strong>{{ paginacion.total_registros }}</strong> registros encontrados
        <br>
        <a href="/admin?page=1&per_page={{ paginacion.per_page }}" class="btn btn-light" style="margin-top:10px;">❌ Limpiar búsqueda</a>
    {% else %}
        Mostrando <strong>{{ paginacion.inicio_registro }}</strong> a <strong>{{ paginacion.fin_registro }}</strong> de <strong>{{ paginacion.total_registros }}</strong> registros
    {% endif %}
</div>

<div class="per-page-selector">
    <label>Registros por página:</label>
    <select onchange="window.location.href='/admin?page=1&per_page='+this.value{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">
        <option value="25" {% if paginacion.per_page == 25 %}selected{% endif %}>25</option>
        <option value="50" {% if paginacion.per_page == 50 %}selected{% endif %}>50</option>
        <option value="100" {% if paginacion.per_page == 100 %}selected{% endif %}>100</option>
        <option value="200" {% if paginacion.per_page == 200 %}selected{% endif %}>200</option>
    </select>
</div>

<div class="card" style="padding:15px;">
    <form method="GET" action="/admin" class="search-form">
        <input type="hidden" name="page" value="1">
        <input type="hidden" name="per_page" value="{{ paginacion.per_page }}">
        <input type="text" name="search" placeholder="🔍 Buscar por referencia, comanda, banco, emisor o monto..." value="{{ paginacion.search }}" autofocus>
        <button type="submit" class="btn btn-primary">Buscar</button>
        {% if paginacion.search %}
            <a href="/admin?page=1&per_page={{ paginacion.per_page }}" class="btn btn-light">Limpiar</a>
        {% endif %}
    </form>
</div>

<div class="pagination">
    {% if paginacion.tiene_anterior %}
        <a href="/admin?page=1&per_page={{ paginacion.per_page }}{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">⏮️ Primera</a>
        <a href="/admin?page={{ paginacion.pagina_anterior }}&per_page={{ paginacion.per_page }}{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">⬅️ Anterior</a>
    {% else %}
        <span class="disabled">⏮️ Primera</span>
        <span class="disabled">⬅️ Anterior</span>
    {% endif %}
    
    <span class="active">Página {{ paginacion.page }} de {{ paginacion.total_paginas }}</span>
    
    {% if paginacion.tiene_siguiente %}
        <a href="/admin?page={{ paginacion.pagina_siguiente }}&per_page={{ paginacion.per_page }}{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">Siguiente ➡️</a>
        <a href="/admin?page={{ paginacion.total_paginas }}&per_page={{ paginacion.per_page }}{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">Última ⏭️</a>
    {% else %}
        <span class="disabled">Siguiente ➡️</span>
        <span class="disabled">Última ⏭️</span>
    {% endif %}
</div>

<div class="table-wrapper"><table id="tab"><thead><tr><th>Recepción (VET)</th><th>Banco</th><th>Emisor</th><th>Monto</th><th>Referencia</th><th>Comanda</th><th>Fecha Canje</th><th>IP Canje</th><th>Acciones</th></tr></thead><tbody>
{% if pagos %}
{% for p in pagos %}<tr>
<td><small>{{p[1]}}<br>{{p[2]}}</small></td>
<td><span class="badge badge-{{p[10]|lower}}">{{p[10]}}</span></td>
<td>{{p[3]}}</td>
<td style="font-weight:800;">Bs. {{p[4]}}</td>
<td><code>{{p[5]}}</code></td>
<td><b style="color:var(--primary)">{{p[9] if p[9] else '-'}}</b></td>
<td><small>{{p[7] if p[7] else '-'}}</small></td>
<td><small style="color:#888">{{p[11] if p[11] else '-'}}</small></td>
<td><div style="display:flex; gap:5px; justify-content:center;">
<form method="POST" action="/admin/liberar" style="display:flex; gap:2px;"><input type="hidden" name="ref" value="{{p[5]}}"><input type="password" name="pw" placeholder="PIN" style="width:40px; padding:5px; font-size:9px;" required><button class="btn-warning" style="padding:5px 8px; border-radius:6px; border:none; cursor:pointer;" title="Liberar">🔓</button></form>
<form method="POST" action="/admin/eliminar" onsubmit="return confirm('¿Borrar definitivamente?');" style="display:flex; gap:2px;"><input type="hidden" name="ref" value="{{p[5]}}"><input type="password" name="pw" placeholder="PIN" style="width:40px; padding:5px; font-size:9px;" required><button class="btn-danger" style="padding:5px 8px; border-radius:6px; border:none; cursor:pointer;" title="Eliminar">🗑️</button></form>
</div></td></tr>{% endfor %}
{% else %}
<tr><td colspan="9" style="text-align:center; padding:40px; color:#999;">
    {% if paginacion.search %}
        No se encontraron resultados para "{{ paginacion.search }}"
    {% else %}
        No hay registros para mostrar
    {% endif %}
</td></tr>
{% endif %}
</tbody></table></div>

<div class="pagination">
    {% if paginacion.tiene_anterior %}
        <a href="/admin?page=1&per_page={{ paginacion.per_page }}{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">⏮️ Primera</a>
        <a href="/admin?page={{ paginacion.pagina_anterior }}&per_page={{ paginacion.per_page }}{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">⬅️ Anterior</a>
    {% else %}
        <span class="disabled">⏮️ Primera</span>
        <span class="disabled">⬅️ Anterior</span>
    {% endif %}
    
    <span class="active">Página {{ paginacion.page }} de {{ paginacion.total_paginas }}</span>
    
    {% if paginacion.tiene_siguiente %}
        <a href="/admin?page={{ paginacion.pagina_siguiente }}&per_page={{ paginacion.per_page }}{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">Siguiente ➡️</a>
        <a href="/admin?page={{ paginacion.total_paginas }}&per_page={{ paginacion.per_page }}{% if paginacion.search %}&search={{ paginacion.search }}{% endif %}">Última ⏭️</a>
    {% else %}
        <span class="disabled">Siguiente ➡️</span>
        <span class="disabled">Última ⏭️</span>
    {% endif %}
</div>

<div class="grid-totales"><div class="total-item" style="background:linear-gradient(135deg,#D32F2F,#FF5252);">Bs. {{ totales.bs }}</div><div class="total-item" style="background:linear-gradient(135deg,#f3ba2f,#fdd835); color:#000;">$ {{ totales.usd }}</div><div class="total-item" style="background:linear-gradient(135deg,#007A33,#2E7D32);">{{ totales.cop }} COP</div></div></div></body></html>'''

# --- RUTAS ---
@app.route('/')
def index():
    return render_template_string(HTML_PORTAL)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Login con validación de contraseña hasheada"""
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        stored_hash = os.getenv("ADMIN_PASSWORD_HASH")
        
        if stored_hash and check_password_hash(stored_hash, password):
            session['logged_in'] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=2)
            logger.info("Login exitoso")
            return redirect(url_for('admin'))
        else:
            logger.warning(f"Intento de login fallido desde {obtener_ip_real()}")
            return render_template_string(HTML_LOGIN, error="PIN incorrecto")
    
    return render_template_string(HTML_LOGIN)

@app.route('/admin')
def admin():
    """Panel administrativo con paginación y búsqueda global (requiere autenticación)"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        # Obtener parámetros de paginación y búsqueda
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str).strip()
        
        # Validar parámetros
        if page < 1:
            page = 1
        if per_page not in [25, 50, 100, 200]:
            per_page = 50
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Construir query con búsqueda
        if search:
            # Búsqueda en múltiples campos
            search_pattern = f"%{search}%"
            
            # Contar total de registros con búsqueda
            cur.execute("""
                SELECT COUNT(*) FROM pagos 
                WHERE referencia ILIKE %s 
                   OR comanda ILIKE %s 
                   OR emisor ILIKE %s 
                   OR banco ILIKE %s
                   OR monto::text ILIKE %s
            """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            total_registros = cur.fetchone()[0]
            total_paginas = (total_registros + per_page - 1) // per_page if total_registros > 0 else 1
            
            # Obtener registros filtrados
            cur.execute("""
                SELECT id, fecha_recepcion, hora_recepcion, emisor, monto, referencia, 
                       mensaje_completo, fecha_canje, estado, comanda, banco, ip_canje 
                FROM pagos 
                WHERE referencia ILIKE %s 
                   OR comanda ILIKE %s 
                   OR emisor ILIKE %s 
                   OR banco ILIKE %s
                   OR monto::text ILIKE %s
                ORDER BY id DESC 
                LIMIT %s OFFSET %s
            """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, per_page, offset))
            pagos = cur.fetchall()
        else:
            # Sin búsqueda - query normal
            cur.execute("SELECT COUNT(*) FROM pagos")
            total_registros = cur.fetchone()[0]
            total_paginas = (total_registros + per_page - 1) // per_page if total_registros > 0 else 1
            
            cur.execute("""
                SELECT id, fecha_recepcion, hora_recepcion, emisor, monto, referencia, 
                       mensaje_completo, fecha_canje, estado, comanda, banco, ip_canje 
                FROM pagos 
                ORDER BY id DESC 
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            pagos = cur.fetchall()
        
        # Calcular totales (de todos los registros, no solo la página actual)
        if search:
            # Totales solo de los registros filtrados
            cur.execute("""
                SELECT monto, banco FROM pagos 
                WHERE referencia ILIKE %s 
                   OR comanda ILIKE %s 
                   OR emisor ILIKE %s 
                   OR banco ILIKE %s
                   OR monto::text ILIKE %s
            """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        else:
            # Totales de todos los registros
            cur.execute("SELECT monto, banco FROM pagos")
        
        todos_pagos = cur.fetchall()
        
        t_bs, t_usd, t_cop = 0.0, 0.0, 0.0
        for p in todos_pagos:
            try:
                m, b = str(p[0]), p[1]
                val = float(m.replace('.', '').replace(',', '.')) if ',' in m else float(m)
                if b == 'BINANCE':
                    t_usd += val
                elif b in ['NEQUI', 'BANCOLOMBIA']:
                    t_cop += val
                else:
                    t_bs += val
            except:
                continue
        
        totales = {"bs": f"{t_bs:,.2f}", "usd": f"{t_usd:,.2f}", "cop": f"{t_cop:,.0f}"}
        
        # Información de paginación
        paginacion = {
            "page": page,
            "per_page": per_page,
            "total_registros": total_registros,
            "total_paginas": total_paginas,
            "tiene_anterior": page > 1,
            "tiene_siguiente": page < total_paginas,
            "pagina_anterior": page - 1,
            "pagina_siguiente": page + 1,
            "inicio_registro": offset + 1 if total_registros > 0 else 0,
            "fin_registro": min(offset + per_page, total_registros),
            "search": search  # Pasar el término de búsqueda al template
        }
        
        conn.close()
        return render_template_string(HTML_ADMIN, pagos=pagos, totales=totales, paginacion=paginacion)
        conn.close()
        return render_template_string(HTML_ADMIN, pagos=pagos, totales=totales, paginacion=paginacion)
    
    except Exception as e:
        logger.error(f"Error en admin: {e}")
        return "Error al cargar panel", 500

@app.route('/verificar', methods=['POST'])
@limiter.limit("10 per minute")
def verificar():
    """Verificar transacción con validación completa - Acepta referencia completa o últimos 6 dígitos"""
    ref = request.form.get('ref', '').strip()
    com_ingresada = request.form.get('comanda', '').strip()
    
    # Validación de entrada - Permitir mínimo 6 caracteres
    if not ref or len(ref) < 6:
        res = {
            "titulo": "ENTRADA INVÁLIDA",
            "mensaje": "El número de referencia debe tener mínimo 6 caracteres.",
            "clase": "error"
        }
        return render_template_string(HTML_PORTAL, resultado=res)
    
    if not validar_comanda(com_ingresada):
        res = {
            "titulo": "ENTRADA INVÁLIDA",
            "mensaje": "El número de comanda no es válido.",
            "clase": "error"
        }
        return render_template_string(HTML_PORTAL, resultado=res)
    
    user_ip = obtener_ip_real()
    fecha_accion = datetime.now(VET).strftime("%d/%m/%Y %I:%M %p")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Buscar por referencia completa o por los últimos 6 dígitos
        if len(ref) == 6 and ref.isdigit():
            # Búsqueda por últimos 6 dígitos
            cur.execute(
                "SELECT id, estado, banco, monto, referencia FROM pagos WHERE referencia LIKE %s",
                ('%' + ref,)
            )
        else:
            # Búsqueda por referencia completa
            cur.execute(
                "SELECT id, estado, banco, monto, referencia FROM pagos WHERE referencia = %s",
                (ref,)
            )
        
        pagos_encontrados = cur.fetchall()
        
        # Validar resultados
        if not pagos_encontrados:
            res = {"titulo": "ERROR", "mensaje": "Referencia no encontrada.", "clase": "error"}
        elif len(pagos_encontrados) > 1:
            res = {
                "titulo": "REFERENCIA AMBIGUA",
                "mensaje": f"Se encontraron {len(pagos_encontrados)} pagos con esos últimos dígitos. Por favor ingresa la referencia completa.",
                "clase": "error"
            }
        else:
            pago = pagos_encontrados[0]
            
            if pago[1] == 'LIBRE':
                cur.execute("""
                    UPDATE pagos 
                    SET estado = 'CANJEADO', comanda = %s, fecha_canje = %s, ip_canje = %s 
                    WHERE id = %s
                """, (com_ingresada, fecha_accion, user_ip, pago[0]))
                conn.commit()
                
                res = {
                    "titulo": "PAGO VALIDADO",
                    "mensaje": "Comprobante vinculado exitosamente.",
                    "clase": "success",
                    "datos": {
                        "banco": pago[2],
                        "monto": pago[3],
                        "ref": pago[4],
                        "comanda": com_ingresada,
                        "fecha": fecha_accion,
                        "ip": user_ip
                    }
                }
                logger.info(f"Pago canjeado: {ref} - Comanda: {com_ingresada}")
            else:
                res = {
                    "titulo": "PAGO YA USADO",
                    "mensaje": "Esta referencia ya fue canjeada anteriormente.",
                    "clase": "error"
                }
        
        conn.close()
        return render_template_string(HTML_PORTAL, resultado=res)
    
    except Exception as e:
        logger.error(f"Error en verificar: {e}")
        return render_template_string(HTML_PORTAL, resultado={
            "titulo": "ERROR",
            "mensaje": "Error procesando la solicitud",
            "clase": "error"
        }), 500

@app.route('/admin/liberar', methods=['POST'])
def liberar():
    """Liberar un pago (requiere PIN)"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    pw = request.form.get('pw', '').strip()
    ref = request.form.get('ref', '').strip()
    stored_hash = os.getenv("ADMIN_PASSWORD_HASH")
    
    if not stored_hash or not check_password_hash(stored_hash, pw):
        logger.warning(f"Intento de liberar con PIN incorrecto desde {obtener_ip_real()}")
        return redirect(url_for('admin'))
    
    if not validar_referencia(ref):
        return redirect(url_for('admin'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE pagos 
            SET estado = 'LIBRE', comanda = NULL, fecha_canje = NULL, ip_canje = NULL 
            WHERE referencia = %s
        """, (ref,))
        conn.commit()
        conn.close()
        logger.info(f"Pago liberado: {ref}")
    except Exception as e:
        logger.error(f"Error al liberar pago: {e}")
    
    return redirect(url_for('admin'))

@app.route('/admin/eliminar', methods=['POST'])
def eliminar():
    """Eliminar un pago (requiere PIN)"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    pw = request.form.get('pw', '').strip()
    ref = request.form.get('ref', '').strip()
    stored_hash = os.getenv("ADMIN_PASSWORD_HASH")
    
    if not stored_hash or not check_password_hash(stored_hash, pw):
        logger.warning(f"Intento de eliminar con PIN incorrecto desde {obtener_ip_real()}")
        return redirect(url_for('admin'))
    
    if not validar_referencia(ref):
        return redirect(url_for('admin'))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM pagos WHERE referencia = %s", (ref,))
        conn.commit()
        conn.close()
        logger.info(f"Pago eliminado: {ref}")
    except Exception as e:
        logger.error(f"Error al eliminar pago: {e}")
    
    return redirect(url_for('admin'))

@app.route('/admin/exportar')
def exportar():
    """Exportar datos a Excel (requiere autenticación)"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM pagos ORDER BY id DESC LIMIT 5000", conn)
        conn.close()
        
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Pagos')
        
        out.seek(0)
        logger.info("Exportación Excel realizada")
        return send_file(
            out,
            as_attachment=True,
            download_name=f"reporte_sistemas_mv_{datetime.now(VET).strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Error en exportar: {e}")
        return "Error al exportar", 500

@app.route('/webhook-bdv', methods=['POST'])
@limiter.limit("100 per hour")
def webhook():
    """Webhook para recibir pagos (con rate limiting)"""
    try:
        # Validar que sea JSON o texto
        raw_data = request.get_json(silent=True)
        if not raw_data:
            raw_data = {"mensaje": request.get_data(as_text=True)}
        
        texto = str(raw_data.get('mensaje', '')).strip()
        
        # Limitar tamaño del mensaje
        if len(texto) > 5000:
            logger.warning("Webhook rechazado por tamaño excesivo")
            return "Mensaje muy grande", 400
        
        pagos = extractor_inteligente(texto)
        
        if pagos:
            conn = get_db_connection()
            cur = conn.cursor()
            ahora_vet = datetime.now(VET)
            
            for p in pagos:
                try:
                    # Verificar que no exista duplicado
                    cur.execute(
                        "SELECT 1 FROM pagos WHERE referencia = %s LIMIT 1",
                        (p['referencia'],)
                    )
                    
                    if not cur.fetchone():
                        cur.execute("""
                            INSERT INTO pagos 
                            (fecha_recepcion, hora_recepcion, emisor, monto, referencia, mensaje_completo, estado, banco) 
                            VALUES (%s, %s, %s, %s, %s, %s, 'LIBRE', %s)
                        """, (
                            ahora_vet.strftime("%d/%m/%Y"),
                            ahora_vet.strftime("%I:%M %p"),
                            p['emisor'][:50],  # Limitar longitud
                            p['monto'],
                            p['referencia'],
                            p['original'][:500],  # Limitar texto almacenado
                            p['banco']
                        ))
                        logger.info(f"Pago insertado: {p['referencia']} - {p['banco']}")
                
                except Exception as e:
                    logger.error(f"Error insertando pago: {e}")
                    continue
            
            conn.commit()
            conn.close()
        
        return "OK", 200
    
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return "OK", 200

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    logger.info("Logout realizado")
    return redirect(url_for('index'))

# --- MANEJO DE ERRORES ---
@app.errorhandler(429)
def ratelimit_handler(e):
    return "Demasiadas solicitudes. Intente más tarde.", 429

@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Error interno del servidor: {e}")
    return "Error interno del servidor", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # NUNCA debug=True en producción
# 📱 Configuración de MacroDroid para Notificaciones Bancarias

## 🎯 Objetivo

Configurar MacroDroid para que capture las notificaciones de los bancos (BDV, Plaza, Sofitasa) y las envíe automáticamente al servidor para registrar los pagos.

---

## 📋 Requisitos Previos

1. ✅ Aplicación MacroDroid instalada en el teléfono
2. ✅ Servidor con `app.py` ejecutándose
3. ✅ Servidor accesible desde internet (puerto abierto o túnel)
4. ✅ URL del servidor (ejemplo: `http://tu-servidor.com:5000` o `https://tu-dominio.com`)

---

## 🔧 Configuración Paso a Paso

### Paso 1: Crear Macro en MacroDroid

1. Abre MacroDroid
2. Toca el botón **"+"** (Agregar Macro)
3. Dale un nombre: **"Enviar Pagos al Servidor"**

---

### Paso 2: Configurar TRIGGER (Disparador)

**Trigger:** Notification

1. Selecciona: **Triggers** → **Notification**
2. Configuración:
   - **Application:** Selecciona las 3 apps de mensajería que recibes notificaciones
     - SMS (si recibes por SMS)
     - WhatsApp (si recibes por WhatsApp)
     - Telegram (si recibes por Telegram)
   - **Notification Title/Text Contains:** (dejar vacío para capturar todas)
   - **Get Notification Text:** ✅ **ACTIVAR** (muy importante)

**Configuración Avanzada:**
- **Trigger when notification is:** Posted
- **Include persistent notifications:** NO
- **Exclude ongoing notifications:** SÍ

---

### Paso 3: Configurar FILTRO (Constraint)

**Constraint:** Text Manipulation

1. Selecciona: **Constraints** → **Text Manipulation**
2. Configuración:
   - **Text to check:** `{notification_text}`
   - **Operation:** Contains
   - **Text:** `Ref` (para filtrar solo notificaciones con referencia)

Esto asegura que solo se envíen notificaciones bancarias que contengan "Ref".

---

### Paso 4: Configurar ACTION (Acción)

**Action:** HTTP Request

1. Selecciona: **Actions** → **Connectivity** → **HTTP Request**
2. Configuración:

#### Configuración Básica:
```
URL: http://TU-SERVIDOR:5000/webhook-bdv
Method: POST
Content Type: application/json
```

#### Body (Cuerpo del Request):
```json
{
  "mensaje": "{notification_text}"
}
```

#### Headers (Encabezados):
```
Content-Type: application/json
```

#### Configuración Avanzada:
- **Timeout:** 30 segundos
- **Follow Redirects:** SÍ
- **Store Response in Variable:** (opcional, para debug)
- **Retry on Failure:** SÍ (2 intentos)

---

### Paso 5: Agregar Notificación de Confirmación (Opcional)

**Action:** Toast/Notification

1. Selecciona: **Actions** → **Notification** → **Toast**
2. Configuración:
   - **Message:** "Pago enviado al servidor ✅"
   - **Duration:** Short
   - **Position:** Bottom

Esto te permite saber cuando se envió un pago.

---

## 📱 Configuración Completa de la Macro

```
MACRO: "Enviar Pagos al Servidor"

├─ TRIGGER
│  └─ Notification
│     ├─ Apps: SMS, WhatsApp, Telegram
│     └─ Get Notification Text: ✅
│
├─ CONSTRAINT
│  └─ Text Contains "Ref"
│     └─ Text: {notification_text}
│
└─ ACTIONS
   ├─ HTTP Request
   │  ├─ URL: http://tu-servidor:5000/webhook-bdv
   │  ├─ Method: POST
   │  ├─ Body: {"mensaje": "{notification_text}"}
   │  └─ Content-Type: application/json
   │
   └─ Toast (opcional)
      └─ Message: "Pago enviado ✅"
```

---

## 🌐 Configuración del Servidor

### Opción 1: Servidor con IP Pública

Si tu servidor tiene IP pública:
```
URL: http://TU-IP-PUBLICA:5000/webhook-bdv
```

### Opción 2: Dominio con HTTPS (Recomendado)

Si tienes un dominio:
```
URL: https://tu-dominio.com/webhook-bdv
```

### Opción 3: Túnel ngrok (Para Pruebas)

Si estás probando localmente:

1. Instala ngrok: https://ngrok.com/
2. Ejecuta:
   ```bash
   ngrok http 5000
   ```
3. Copia la URL generada (ejemplo: `https://abc123.ngrok.io`)
4. Usa en MacroDroid:
   ```
   URL: https://abc123.ngrok.io/webhook-bdv
   ```

---

## 🧪 Pruebas

### Prueba 1: Envío Manual

1. En MacroDroid, ve a la macro creada
2. Toca el botón **"Test Actions"**
3. Ingresa un mensaje de prueba:
   ```
   Recibiste un PagomovilBDV comercio por Bs. 100,00 del 0414-1234567 Ref: 000123456789
   ```
4. Verifica en el servidor que se recibió

### Prueba 2: Notificación Real

1. Envía un mensaje de prueba al teléfono con formato bancario
2. Verifica que MacroDroid capture la notificación
3. Verifica en el panel admin que el pago se registró

---

## 📝 Ejemplos de Mensajes que se Procesarán

### BDV (Banco de Venezuela)
```
Recibiste un PagomovilBDV comercio por Bs. 8.187,03 del 0414-2774266 
Ref: 000602279657 comision Bs 122,81 fecha: 10-02-26 hora: 15:24
```

**Datos extraídos:**
- Banco: BDV
- Monto: 8.187,03
- Emisor: 0414-2774266
- Referencia: 000602279657

### Banco Plaza
```
Bco.Plaza informa que ha recibido una transaccion Tu DineroYA por BS.1265.34 
del Nro Celular 04129618333. Ref.000556895149 13-01-26 15:24. Inf.: 05017529200
```

**Datos extraídos:**
- Banco: PLAZA
- Monto: 1265.34
- Emisor: 04129618333
- Referencia: 000556895149

### Sofitasa
```
SOFITASA Pago Movil Recibido Bs.3095,49 Telf.0414***1081 
Dia:09/02/26-17:02 Ref:051967214 Llamar al 0500-7634835 si no realizo la Operacion
```

**Datos extraídos:**
- Banco: SOFITASA
- Monto: 3095,49
- Emisor: 0414***1081
- Referencia: 051967214

---

## 🔒 Seguridad

### 1. Usar HTTPS en Producción

En lugar de HTTP, usa HTTPS para encriptar la comunicación:
```
URL: https://tu-dominio.com/webhook-bdv
```

### 2. Autenticación (Opcional)

Puedes agregar un token de autenticación en los headers:

**En MacroDroid:**
```
Headers:
Content-Type: application/json
Authorization: Bearer TU-TOKEN-SECRETO
```

**En app.py** (agregar validación):
```python
@app.route('/webhook-bdv', methods=['POST'])
def webhook():
    token = request.headers.get('Authorization')
    if token != 'Bearer TU-TOKEN-SECRETO':
        return "No autorizado", 401
    # ... resto del código
```

### 3. Whitelist de IPs (Opcional)

Configura el firewall para aceptar solo requests desde la IP del teléfono.

---

## 🐛 Solución de Problemas

### Problema 1: "Connection Failed"

**Causas:**
- Servidor no accesible desde internet
- Puerto cerrado en firewall
- URL incorrecta

**Solución:**
1. Verifica que el servidor esté corriendo: `python app.py`
2. Verifica que el puerto esté abierto
3. Prueba la URL desde el navegador del teléfono

### Problema 2: "Timeout"

**Causas:**
- Servidor lento
- Conexión de internet débil

**Solución:**
1. Aumenta el timeout en MacroDroid a 60 segundos
2. Verifica la conexión del teléfono

### Problema 3: "No se registran los pagos"

**Causas:**
- Formato del mensaje no reconocido
- Error en el extractor inteligente

**Solución:**
1. Revisa los logs del servidor
2. Verifica que el mensaje contenga "Ref:"
3. Prueba manualmente con curl:
   ```bash
   curl -X POST http://tu-servidor:5000/webhook-bdv \
     -H "Content-Type: application/json" \
     -d '{"mensaje": "tu mensaje de prueba"}'
   ```

---

## 📊 Monitoreo

### Ver Logs en el Servidor

```bash
# Ver logs en tiempo real
tail -f app.log

# O ver en consola si ejecutas directamente
python app.py
```

### Verificar Pagos Registrados

1. Accede al panel admin: `http://tu-servidor:5000/login`
2. Ingresa tu PIN
3. Verifica que los pagos aparezcan en la tabla

---

## 🔄 Configuración Avanzada

### Enviar a Múltiples Servidores (Backup)

Puedes crear 2 acciones HTTP Request en la misma macro:

```
ACTIONS:
├─ HTTP Request → Servidor Principal
└─ HTTP Request → Servidor Backup
```

### Guardar Localmente (Backup)

Agrega una acción para guardar en archivo local:

```
ACTIONS:
├─ HTTP Request → Servidor
└─ Write to File
   ├─ File: /sdcard/pagos_backup.txt
   └─ Content: {notification_text}
```

---

## ✅ Checklist de Configuración

- [ ] MacroDroid instalado
- [ ] Macro creada con nombre descriptivo
- [ ] Trigger configurado (Notification)
- [ ] Constraint configurado (Text Contains "Ref")
- [ ] Action HTTP Request configurada
- [ ] URL del servidor correcta
- [ ] Method: POST
- [ ] Content-Type: application/json
- [ ] Body: {"mensaje": "{notification_text}"}
- [ ] Prueba manual realizada
- [ ] Prueba con notificación real realizada
- [ ] Pagos aparecen en el panel admin

---

## 📞 Soporte

Si tienes problemas:
1. Verifica los logs del servidor
2. Prueba con curl manualmente
3. Verifica que MacroDroid tenga permisos de notificación
4. Revisa el historial de ejecución en MacroDroid

---

*Guía creada: 2026-02-09*

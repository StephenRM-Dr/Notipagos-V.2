# Instrucciones: Validación de Pagos BDV

## 🚀 Pasos para Activar la Validación BDV

### 1. Migrar la Base de Datos

Primero, agrega las columnas necesarias a tu tabla `pagos`:

```bash
python migrate_bdv.py
```

Esto agregará las siguientes columnas:
- `cedula_pagador` - Cédula del cliente
- `telefono_pagador` - Teléfono del cliente
- `banco_origen` - Código del banco (4 dígitos)
- `estado_bdv` - Estado de validación del BDV
- `fecha_validacion` - Fecha de validación con el banco
- `fecha_pago` - Fecha del pago móvil

### 2. Verificar Configuración

Asegúrate de que tu archivo `.env` tenga configurado:

```env
# API BANCO BDV
BDV_API_KEY=TU_API_KEY_REAL_AQUI
BDV_API_URL=https://bdvconciliacion.banvenez.com:443/getMovement
BDV_AMBIENTE=produccion
```

**Opciones de ambiente:**
- `produccion` - Usa el API real del banco (requiere API Key válido)
- `simulacion` - Modo de desarrollo sin conexión al banco

### 3. Iniciar la Aplicación

```bash
python app.py
```

## 📋 Cómo Usar la Validación

### Desde el Panel de Administración

1. Inicia sesión en `/login`
2. Ve al panel de administración `/admin`
3. Accede al formulario de validación en `/validar-bdv`

### Formulario de Validación

El formulario requiere los siguientes datos:

1. **Cédula del Pagador**
   - Formato: V12345678, E12345678, J12345678, G12345678
   - Incluir la letra de nacionalidad

2. **Teléfono**
   - Formato: 04121234567
   - 11 dígitos sin espacios ni guiones

3. **Referencia del Pago**
   - Número de referencia del pago móvil
   - Tal como aparece en el comprobante

4. **Fecha del Pago**
   - Formato: YYYY-MM-DD
   - Usar el selector de fecha

5. **Monto**
   - Formato: 120.00
   - Sin comas, usar punto para decimales

6. **Banco Origen**
   - Seleccionar del listado
   - Códigos de 4 dígitos (ej: 0102 para BDV)

### Proceso de Validación

1. El sistema envía los datos al API del BDV
2. El banco valida si el pago existe y es válido
3. Si es válido (código 1000):
   - Se registra en la base de datos
   - Estado: LIBRE (disponible para canjear)
4. Si no es válido:
   - Se muestra el mensaje de error del banco
   - No se registra en la base de datos

## 🔍 Códigos de Respuesta del BDV

### ✅ Código 1000 - Éxito
```json
{
  "code": 1000,
  "message": "Monto: 120.00 - estatus : Transaccion realizada"
}
```
El pago es válido y se registra en la base de datos.

### ❌ Código 1010 - Error
```json
{
  "code": 1010,
  "message": "No se pudo validar el movimiento : Registro solicitado no existe"
}
```
El pago no existe en el sistema del banco.

### ❌ Otros Errores
- **Datos Mandatorios null**: Algún campo está vacío
- **Bad Request (400)**: Formato de datos incorrecto
- **Timeout**: El banco no respondió a tiempo
- **Connection Error**: No hay conexión con el banco

## 🔄 Flujo Completo

```
1. Cliente hace pago móvil
   ↓
2. Cliente proporciona datos del pago
   ↓
3. Admin ingresa datos en formulario /validar-bdv
   ↓
4. Sistema valida con API BDV
   ↓
5. Si válido → Registra en BD con estado LIBRE
   ↓
6. Cliente puede canjear en /verificar
```

## 🛠️ Troubleshooting

### Error: "API Key no configurado"
- Verifica que `BDV_API_KEY` esté en tu `.env`
- O usa `BDV_AMBIENTE=simulacion` para desarrollo

### Error: "Connection Error"
- Verifica tu conexión a internet
- El servidor del banco puede estar temporalmente no disponible
- Usa modo simulación para desarrollo

### Error: "Registro solicitado no existe"
- Verifica que los datos sean correctos
- La fecha debe coincidir con la del pago
- El monto debe ser exacto (con 2 decimales)
- La referencia debe ser la correcta

### Pago ya registrado
- Si intentas registrar un pago que ya existe, el sistema lo detectará
- La columna `referencia` es UNIQUE en la base de datos

## 📊 Consultar Pagos Validados

En el panel de administración (`/admin`) verás todos los pagos registrados:
- Los validados con BDV tendrán datos en las columnas nuevas
- Estado inicial: LIBRE
- Después de canjear: CANJEADO

## 🔐 Seguridad

- Solo usuarios autenticados pueden acceder al formulario
- El API Key nunca se expone al cliente
- Todas las comunicaciones con el banco usan HTTPS
- Los datos sensibles se validan antes de enviar

## 📝 Logs

El sistema registra:
- Intentos de validación
- Respuestas del banco
- Errores de conexión
- Pagos registrados exitosamente

Revisa los logs en la consola donde ejecutas `python app.py`

## 🎯 Próximos Pasos

1. Ejecuta la migración: `python migrate_bdv.py`
2. Configura tu API Key en `.env`
3. Inicia la aplicación: `python app.py`
4. Accede a `/validar-bdv` desde el admin
5. Prueba con un pago real

¡Listo! Tu sistema ahora valida pagos automáticamente con el banco.

  # 🔍 Verificación con Últimos 6 Dígitos

## ✨ Nueva Funcionalidad

Ahora los usuarios pueden verificar sus pagos ingresando **solo los últimos 6 dígitos** de la referencia en lugar de la referencia completa.

---

## 🎯 Cómo Funciona

### Opción 1: Últimos 6 Dígitos (Nuevo)
Si el usuario ingresa exactamente **6 dígitos numéricos**, el sistema busca todas las referencias que terminen con esos dígitos.

**Ejemplo:**
- Referencia completa: `123456789012`
- Usuario ingresa: `789012`
- ✅ El sistema encuentra el pago

### Opción 2: Referencia Completa (Original)
El usuario puede seguir ingresando la referencia completa como antes.

**Ejemplo:**
- Usuario ingresa: `123456789012`
- ✅ El sistema encuentra el pago

---

## 🔒 Validaciones de Seguridad

### 1. Mínimo 6 Caracteres
```
❌ "12345" → Error: Mínimo 6 caracteres
✅ "123456" → Busca por últimos 6 dígitos
✅ "1234567890" → Busca por referencia completa
```

### 2. Detección de Ambigüedad
Si hay múltiples pagos con los mismos últimos 6 dígitos:

```
Usuario ingresa: "123456"

Pagos encontrados:
- Ref: 789123456
- Ref: 456123456

❌ Resultado: "Se encontraron 2 pagos con esos últimos dígitos. 
              Por favor ingresa la referencia completa."
```

### 3. Protección SQL Injection
La búsqueda usa parámetros preparados para prevenir inyección SQL:
```python
cur.execute(
    "SELECT ... FROM pagos WHERE referencia LIKE %s",
    ('%' + ref,)
)
```

---

## 💡 Casos de Uso

### Caso 1: Usuario con Referencia Corta
```
Referencia: 789012
Comanda: #1234
✅ Pago encontrado y vinculado
```

### Caso 2: Usuario con Referencia Completa
```
Referencia: 123456789012
Comanda: #1234
✅ Pago encontrado y vinculado
```

### Caso 3: Múltiples Coincidencias
```
Referencia: 123456
Resultado: "Se encontraron 3 pagos con esos últimos dígitos"
Solución: Ingresar referencia completa
```

### Caso 4: Referencia No Encontrada
```
Referencia: 999999
Resultado: "Referencia no encontrada"
```

---

## 🎨 Interfaz Actualizada

El campo de entrada ahora muestra:
```
Placeholder: "Últimos 6 dígitos o Referencia completa"
Validación HTML: minlength="6"
```

---

## 📊 Flujo de Verificación

```
Usuario ingresa referencia
         ↓
¿Tiene exactamente 6 dígitos numéricos?
         ↓
    Sí        No
    ↓          ↓
Buscar por  Buscar por
últimos 6   referencia
dígitos     completa
    ↓          ↓
    └──────┬───┘
           ↓
¿Cuántos pagos encontrados?
           ↓
    0      1      2+
    ↓      ↓       ↓
  Error  Validar  Error
         pago     ambiguo
```

---

## 🔧 Código Implementado

### Función de Verificación
```python
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
    # No encontrado
elif len(pagos_encontrados) > 1:
    # Ambiguo
else:
    # Único pago encontrado - procesar
```

---

## ✅ Ventajas

1. **Más fácil para usuarios** - No necesitan copiar/pegar referencias largas
2. **Menos errores de tipeo** - Solo 6 dígitos en lugar de 12-20
3. **Más rápido** - Menos tiempo ingresando datos
4. **Seguro** - Detecta ambigüedades y solicita referencia completa
5. **Compatible** - Sigue funcionando con referencias completas

---

## ⚠️ Consideraciones

### Probabilidad de Colisión
Con 6 dígitos hay 1,000,000 combinaciones posibles. La probabilidad de colisión depende del volumen de transacciones:

- **< 1,000 pagos/día**: Probabilidad muy baja
- **1,000-10,000 pagos/día**: Probabilidad baja
- **> 10,000 pagos/día**: Considerar aumentar a 8 dígitos

### Recomendación
Si experimentas muchas colisiones, puedes modificar el código para requerir 8 dígitos en lugar de 6:

```python
if len(ref) == 8 and ref.isdigit():  # Cambiar de 6 a 8
```

---

## 🧪 Pruebas

### Prueba 1: Últimos 6 Dígitos
```
1. Ir a http://localhost
2. Ingresar: "123456" (últimos 6 de una referencia real)
3. Ingresar comanda
4. Verificar que encuentra el pago
```

### Prueba 2: Referencia Completa
```
1. Ir a http://localhost
2. Ingresar referencia completa
3. Ingresar comanda
4. Verificar que encuentra el pago
```

### Prueba 3: Ambigüedad
```
1. Crear 2 pagos con referencias que terminen igual
2. Ingresar los últimos 6 dígitos
3. Verificar mensaje de ambigüedad
```

---

## 📝 Mensajes de Error

| Situación | Mensaje |
|-----------|---------|
| Menos de 6 caracteres | "El número de referencia debe tener mínimo 6 caracteres." |
| No encontrado | "Referencia no encontrada." |
| Múltiples coincidencias | "Se encontraron X pagos con esos últimos dígitos. Por favor ingresa la referencia completa." |
| Pago ya usado | "Esta referencia ya fue canjeada anteriormente." |

---

*Funcionalidad implementada: 2026-02-09*

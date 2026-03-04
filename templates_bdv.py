"""
Templates HTML para validación de pagos BDV
"""

HTML_VALIDAR_BDV = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validar Pago BDV</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #555;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .loading.active {
            display: block;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .back-link a {
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
        }
        .back-link a:hover {
            text-decoration: underline;
        }
        .help-text {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            font-size: 13px;
            color: #0d47a1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏦 Validar Pago BDV</h1>
        <p class="subtitle">Validación simplificada con el banco</p>
        
        <div class="info-box">
            ℹ️ Solo necesitas la referencia y el banco. El sistema validará automáticamente con el BDV y obtendrá el monto real del pago.
        </div>
        
        <div id="alert-container"></div>
        
        <form id="formValidarBDV">
            <div class="form-group">
                <label for="referencia">Referencia del Pago *</label>
                <input type="text" id="referencia" name="referencia" placeholder="060551816980" required>
                <div class="help-text">Número de referencia del pago móvil</div>
            </div>
            
            <div class="form-group">
                <label for="banco">Banco Origen *</label>
                <select id="banco" name="banco" required>
                    <option value="">Seleccionar banco...</option>
                    <option value="0102">0102 - Banco de Venezuela</option>
                    <option value="0134">0134 - Banesco</option>
                    <option value="0108">0108 - BBVA Provincial</option>
                    <option value="0105">0105 - Mercantil</option>
                    <option value="0191">0191 - BNC</option>
                    <option value="0114">0114 - Bancaribe</option>
                    <option value="0104">0104 - Venezolano de Crédito</option>
                    <option value="0115">0115 - Exterior</option>
                    <option value="0128">0128 - Caroní</option>
                    <option value="0163">0163 - Tesoro</option>
                    <option value="0166">0166 - Agrícola</option>
                    <option value="0172">0172 - Bancamiga</option>
                    <option value="0175">0175 - Bicentenario</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="importe">Importe (Opcional)</label>
                <input type="text" id="importe" name="importe" placeholder="10776.00">
                <div class="help-text">Monto sin comas, con punto decimal</div>
            </div>
            
            <button type="submit" class="btn" id="btnSubmit">
                🔍 Validar Pago
            </button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">Validando con el banco...</p>
        </div>
        
        <div class="back-link">
            <a href="/admin">← Volver al panel de administración</a>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('formValidarBDV');
        const btnSubmit = document.getElementById('btnSubmit');
        const loading = document.getElementById('loading');
        const alertContainer = document.getElementById('alert-container');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Deshabilitar botón y mostrar loading
            btnSubmit.disabled = true;
            loading.classList.add('active');
            alertContainer.innerHTML = '';
            
            // Obtener datos del formulario
            const formData = new FormData(form);
            
            try {
                const response = await fetch('/validar-pago-bdv', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alertContainer.innerHTML = `
                        <div class="alert alert-success">
                            <strong>✅ Pago Validado</strong><br>
                            ${result.message}<br>
                            <strong>Referencia:</strong> ${result.data.referencia}<br>
                            <strong>Monto:</strong> Bs. ${result.data.monto}<br>
                            <strong>Banco:</strong> ${result.data.banco}
                        </div>
                    `;
                    form.reset();
                } else {
                    alertContainer.innerHTML = `
                        <div class="alert alert-error">
                            <strong>❌ Error</strong><br>
                            ${result.message}
                            ${result.code ? '<br><strong>Código:</strong> ' + result.code : ''}
                        </div>
                    `;
                }
            } catch (error) {
                alertContainer.innerHTML = `
                    <div class="alert alert-error">
                        <strong>❌ Error de Conexión</strong><br>
                        No se pudo conectar con el servidor
                    </div>
                `;
            } finally {
                btnSubmit.disabled = false;
                loading.classList.remove('active');
            }
        });
    </script>
</body>
</html>
'''

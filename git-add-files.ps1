# Script para agregar archivos a Git en PowerShell
# Uso: .\git-add-files.ps1

Write-Host "Agregando archivos al repositorio Git..." -ForegroundColor Green

# Agregar archivos uno por uno
git add app.py
git add requirements.txt
git add .env.example
git add .gitignore
git add "create table.py"
git add migrate.py
git add test_db.py
git add nginx.conf.example
git add deploy.sh
git add LEEME_PRIMERO.md
git add CONFIGURACION_MACRODROID.md
git add SEGURIDAD.md
git add DESPLIEGUE_AWS.md
git add PREPARAR_PARA_AWS.md
git add ARCHIVOS_PARA_AWS.md
git add README.md

Write-Host "`nArchivos agregados exitosamente!" -ForegroundColor Green
Write-Host "`nVerificando estado..." -ForegroundColor Yellow
git status

Write-Host "`n¿Deseas hacer commit ahora? (s/n): " -ForegroundColor Cyan -NoNewline
$respuesta = Read-Host

if ($respuesta -eq 's' -or $respuesta -eq 'S') {
    $mensaje = Read-Host "Ingresa el mensaje del commit"
    git commit -m "$mensaje"
    Write-Host "`nCommit realizado!" -ForegroundColor Green
    
    Write-Host "`n¿Deseas hacer push? (s/n): " -ForegroundColor Cyan -NoNewline
    $push = Read-Host
    
    if ($push -eq 's' -or $push -eq 'S') {
        git push origin main
        Write-Host "`nPush completado!" -ForegroundColor Green
    }
}

Write-Host "`n¡Listo!" -ForegroundColor Green

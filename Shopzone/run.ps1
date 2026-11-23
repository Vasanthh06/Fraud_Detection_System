Set-Location $PSScriptRoot

Write-Host "== Step 1: venv ==" -ForegroundColor Cyan
if (-not (Test-Path .venv)) { python -m venv .venv }
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1

Write-Host "== Step 2: deps ==" -ForegroundColor Cyan
pip install --upgrade pip
pip install -r backend\requirements.txt

Write-Host "== Step 3: .env ==" -ForegroundColor Cyan
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    $hash = python -c "import bcrypt; print(bcrypt.hashpw(b'YourNewPassword123!', bcrypt.gensalt(rounds=12)).decode())"
    (Get-Content .env) -replace '^ADMIN_PASSWORD_HASH=.*$', "ADMIN_PASSWORD_HASH=$hash" | Set-Content .env -Encoding UTF8
    (Get-Content .env) -replace '^JWT_SECRET=.*$', "JWT_SECRET=dev-secret-$(Get-Random)" | Set-Content .env -Encoding UTF8
    Write-Host "  .env created. Admin password: YourNewPassword123!" -ForegroundColor Yellow
}

Write-Host "== Step 4: models ==" -ForegroundColor Cyan
if (-not (Test-Path models\fraud_model.pkl)) {
    python scripts\dataset_generator.py
    python scripts\train_model.py
    python scripts\train_ecommerce_model.py
}

Write-Host "== Step 5: server ==" -ForegroundColor Green
Write-Host "Open http://127.0.0.1:8000  |  Admin: adminhere@gmail.com / YourNewPassword123!" -ForegroundColor Yellow
uvicorn backend.app.main:app --reload
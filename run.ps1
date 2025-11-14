Write-Host "Starting OMR Scanner Server..." -ForegroundColor Green
Set-Location backend
..\..venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload


@echo off
echo Waking up Local AI Engine...
start /B ollama serve

:: Give the massive AI models 5 seconds to load into memory
timeout /t 5 /nobreak > NUL

cd "C:\Users\Aarav Gupta\Downloads\Forecasting_Engine"
call .\venv\Scripts\activate
python master_dispatcher.py

:: We will remove 'pause' once you confirm this works, so it closes automatically
pause
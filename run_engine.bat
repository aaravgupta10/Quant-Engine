@echo off
echo Waking up Local AI Engine...

cd "C:\Users\Aarav Gupta\Downloads\Forecasting_Engine"
call .\venv\Scripts\activate
python master_dispatcher.py

:: We will remove 'pause' once you confirm this works, so it closes automatically
pause
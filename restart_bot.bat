@echo off
echo 🔄 กำลังรีสตาร์ทบอท...
echo.

rem หยุดกระบวนการ Python ที่กำลังทำงาน (ถ้ามี)
taskkill /f /im python.exe 2>nul

echo ⏰ รอ 3 วินาที...
timeout /t 3 /nobreak >nul

echo 🚀 เริ่มต้นบอทใหม่...
python main.py

pause

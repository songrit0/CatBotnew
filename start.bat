@echo off
echo กำลังติดตั้ง dependencies...
pip install -r requirements.txt

echo.
echo กำลังเริ่มบอท Discord...
python bot.py

pause

@echo off
echo 🤖 Cat Bot - ติดตั้ง Google Sheets Integration
echo ================================================

echo 📦 กำลังติดตั้ง Python packages...
pip install -r requirements.txt

echo.
echo 🔍 กำลังทดสอบการเชื่อมต่อ Google Sheets...
python test_sheets.py

echo.
echo ✅ การติดตั้งเสร็จสิ้น!
echo.
echo 📋 วิธีใช้งาน:
echo 1. ตรวจสอบไฟล์ .env ให้มี GOOGLE_SHEETS_ID และ GOOGLE_SHEET_NAME
echo 2. ตรวจสอบไฟล์ credentials.json จาก Google Service Account
echo 3. เรียกใช้ start.bat เพื่อเริ่มบอท
echo.
pause

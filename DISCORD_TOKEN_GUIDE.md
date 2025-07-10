# 🤖 วิธีการขอ Discord Bot Token

## 📋 ขั้นตอนการสร้าง Discord Bot

### 1. เข้าไปที่ Discord Developer Portal
- ไปที่: https://discord.com/developers/applications
- เข้าสู่ระบบด้วยบัญชี Discord ของคุณ

### 2. สร้าง Application ใหม่
- คลิก **"New Application"**
- ใส่ชื่อ Application (เช่น "Cat Bot")
- คลิก **"Create"**

### 3. สร้าง Bot
- ไปที่แท็บ **"Bot"** ทางด้านซ้าย
- คลิก **"Add Bot"**
- ยืนยันด้วยการคลิก **"Yes, do it!"**

### 4. คัดลอก Token
- ในหน้า Bot ให้คลิก **"Reset Token"**
- คัดลอก Token ที่ได้ (จะขึ้นเป็นรหัสยาวๆ)
- ⚠️ **อย่าแชร์ Token นี้กับใคร**

### 5. ตั้งค่า Bot
```
Bot Permissions ที่จำเป็น:
✅ Send Messages
✅ Connect (Voice)
✅ Speak (Voice)
✅ Manage Channels
✅ View Channels
✅ Read Message History
```

### 6. เพิ่ม Bot เข้า Discord Server
- ไปที่แท็บ **"OAuth2"** > **"URL Generator"**
- เลือก Scope: **"bot"**
- เลือก Bot Permissions ตามข้างต้น
- คัดลอก URL ที่ได้และเปิดในเบราว์เซอร์
- เลือก Server ที่ต้องการเพิ่ม Bot

## 🔧 การตั้งค่าใน .env

หลังจากได้ Token แล้ว ให้แก้ไขไฟล์ `.env`:

```env
# Discord Bot Token (ได้จาก Discord Developer Portal)
DISCORD_TOKEN="YOUR_ACTUAL_BOT_TOKEN_HERE"

# Google Sheets Configuration
GOOGLE_SHEETS_ID="19GsVNITyyohhPz6dZKMeD9bQoje6Cg8VYelUMDZhhQw"
GOOGLE_SHEET_NAME="Cat_bot_Spreadsheets"
```

## ⚠️ หมายเหตุสำคัญ

### Token ที่ถูกต้องจะเป็น:
```
MTxxxxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- เริ่มต้นด้วยตัวอักษรและตัวเลข
- มีจุด (.) คั่น
- ยาวประมาณ 70+ ตัวอักษร

### Token ที่ผิด:
❌ URL (เช่น https://api.render.com/...)
❌ Client ID
❌ Client Secret
❌ Application ID

## 🧪 การทดสอบหลังตั้งค่า

```bash
# ทดสอบว่า Token ทำงาน
python main.py
```

หากยังมีปัญหา:
1. ตรวจสอบว่า Token ถูกต้อง
2. ตรวจสอบว่า Bot อยู่ใน Server แล้ว
3. ตรวจสอบสิทธิ์ของ Bot

## 🔗 ลิงก์ที่เป็นประโยชน์

- Discord Developer Portal: https://discord.com/developers/applications
- Discord.py Documentation: https://discordpy.readthedocs.io/
- Discord Permissions Calculator: https://discordapi.com/permissions.html

---
*อัปเดตครั้งล่าสุด: 10 กรกฎาคม 2025*

# CatBot - Discord Voice Channel Management Bot

## 📁 โครงสร้างไฟล์

```
CatBotnew/
├── main.py              # ไฟล์หลักสำหรับเริ่มต้นบอท
├── config_manager.py    # จัดการการโหลดและบันทึกการตั้งค่า
├── voice_manager.py     # จัดการการอัปเดตชื่อห้องเสียง
├── queue_processor.py   # จัดการการประมวลผลคิวการอัพเดต
├── commands.py          # คำสั่งต่างๆ ของบอท
├── events.py            # จัดการ Event ต่างๆ ของบอท
├── ui_components.py     # คอมโพเนนต์ UI สำหรับ Discord
├── config.json          # ไฟล์การตั้งค่า
├── requirements.txt     # รายการ package ที่ต้องติดตั้ง
├── .env.example         # ตัวอย่างไฟล์ environment variables
├── .env                 # ไฟล์ environment variables (ไม่รวมใน git)
├── start.bat           # ไฟล์สำหรับเริ่มบอทใน Windows
└── README.md           # ไฟล์นี้
```

## 📦 ความสามารถของแต่ละไฟล์

### main.py
- ไฟล์หลักสำหรับเริ่มต้นบอท
- จัดการการตั้งค่าเริ่มต้น
- โหลด Cogs ต่างๆ

### config_manager.py
- โหลดและบันทึกการตั้งค่าจาก `config.json`
- ฟังก์ชันช่วยเหลือสำหรับจัดการการตั้งค่า
- ตรวจสอบห้องพิเศษ

### voice_manager.py
- จัดการการอัปเดตชื่อห้องเสียง
- จัดการ Rate Limiting
- ส่งการแจ้งเตือน

### queue_processor.py
- ประมวลผลคิวการอัพเดตที่ถูกล่าช้าเนื่องจาก Rate Limiting
- ทำงานเป็น background task

### commands.py
- คำสั่งต่างๆ ของบอท (!help, !info, !status, etc.)
- จัดการสิทธิ์การใช้งาน
- คำสั่งสำหรับ Administrator

### events.py
- จัดการ Event การเข้า/ออกห้องเสียง
- Event เมื่อบอทพร้อมใช้งาน

### ui_components.py
- UI Components สำหรับ Discord (Views, Modals, Buttons)
- ระบบจัดการ Voice Channels ผ่าน UI

## 🚀 วิธีการใช้งาน

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า Environment Variables
1. คัดลอก `.env.example` เป็น `.env`
2. แก้ไขค่า `DISCORD_TOKEN` ในไฟล์ `.env`

### 3. เริ่มต้นบอท
```bash
python main.py
```
หรือใน Windows:
```bash
start.bat
```

## ⚙️ การตั้งค่า

### config.json
```json
{
  "voice_channels": {
    "channel_id": {
      "empty_name": "ชื่อเมื่อว่าง",
      "occupied_name": "ชื่อเมื่อมีคน"
    }
  },
  "command_channel": "channel_id_for_commands",
  "notification_channel": "channel_id_for_notifications"
}
```

## 📋 คำสั่งที่ใช้ได้

### คำสั่งสำหรับทุกคน
- `!help` - แสดงคำสั่งทั้งหมด
- `!info` - แสดงข้อมูลห้องเสียงทั้งหมด
- `!status` - แสดงสถานะบอท
- `!queue` - แสดงคิวการอัพเดต
- `!debug` - แสดงข้อมูลดีบัก
- `!test` - ทดสอบระบบ
- `!check` - ตรวจสอบสถานะห้อง
- `!manage` - จัดการการตั้งค่า voice channels

### คำสั่งสำหรับ Administrator
- `!forcenow <channel_id>` - บังคับอัพเดตทันที
- `!update` - อัพเดตห้องเสียงทั้งหมด

## 🔧 ข้อดีของการแยกไฟล์

1. **ง่ายต่อการบำรุงรักษา** - แต่ละไฟล์มีหน้าที่ชัดเจน
2. **ง่ายต่อการพัฒนา** - สามารถแก้ไขส่วนเฉพาะได้โดยไม่กระทบส่วนอื่น
3. **ง่ายต่อการทดสอบ** - สามารถทดสอบแต่ละส่วนแยกกันได้
4. **ง่ายต่อการเพิ่มฟีเจอร์** - สามารถเพิ่มฟีเจอร์ใหม่ได้ง่าย
5. **ลดความซับซ้อน** - โค้ดแต่ละไฟล์ไม่ยาวเกินไป

## 🐛 การแก้ไขปัญหา

### บอทไม่ตอบสนอง
1. ตรวจสอบว่าบอทออนไลน์หรือไม่
2. ตรวจสอบสิทธิ์ของบอทในเซิร์ฟเวอร์
3. ตรวจสอบการตั้งค่า `command_channel` ใน config.json

### Rate Limiting
- บอทจะจัดการ Rate Limiting อัตโนมัติ
- คิวการอัพเดตจะทำงานอัตโนมัติ

## 📄 License

โครงการนี้เป็น Open Source สามารถนำไปใช้และแก้ไขได้ตามต้องการ

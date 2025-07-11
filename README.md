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
├── music_manager.py     # ระบบจัดการเพลงจาก YouTube
├── music_commands.py    # คำสั่งเพลงและปุ่มควบคุม
├── config.json          # ไฟล์การตั้งค่า
├── requirements.txt     # รายการ package ที่ต้องติดตั้ง
├── .env.example         # ตัวอย่างไฟล์ environment variables
├── .env                 # ไฟล์ environment variables (ไม่รวมใน git)
├── start.bat           # ไฟล์สำหรับเริ่มบอทใน Windows
├── MUSIC_GUIDE.md      # คู่มือระบบเพลง
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

### music_manager.py
- ระบบจัดการเพลงจาก YouTube
- คลาส Song, MusicQueue และ YTDLSource
- การจัดการ voice clients และคิวเพลง

### music_commands.py  
- คำสั่งเพลงทั้งหมด (!play, !skip, !queue, etc.)
- Views สำหรับควบคุมเพลงด้วยปุ่ม
- Modal สำหรับเพิ่มเพลง

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

### คำสั่งเพลง 🎵
- `!play <ชื่อเพลง/URL>` - เล่นเพลงจาก YouTube
- `!skip` - ข้ามเพลงปัจจุบัน
- `!stop` - หยุดเพลงและล้างคิว
- `!queue` - ดูคิวเพลง
- `!music` - เปิดแผงควบคุมเพลง
- `!musiccontrol` - แผงควบคุมเพลงแบบละเอียด

**📖 ดูคู่มือเพิ่มเติมใน [MUSIC_GUIDE.md](MUSIC_GUIDE.md)**

## 🆕 อัปเดตใหม่: ระบบหลายห้อง (Multiple Channels)

ตอนนี้บอทรองรับการตั้งค่า Command Channels และ Notification Channels แบบหลายห้องแล้ว!

### คำสั่งใหม่สำหรับจัดการห้อง

- `!add_command_channel [#channel]` - เพิ่มห้องเป็น command channel
- `!remove_command_channel [#channel]` - ลบห้องออกจาก command channels
- `!add_notification_channel [#channel]` - เพิ่มห้องเป็น notification channel  
- `!remove_notification_channel [#channel]` - ลบห้องออกจาก notification channels
- `!list_channels` - แสดงรายการห้องที่ตั้งค่าไว้ทั้งหมด

### การอัปเดตจากรูปแบบเก่า

1. รันไฟล์ `migrate_channels.bat` เพื่ออัปเดต Google Sheets
2. หรือรัน `python migrate_channels.py` ใน command line
3. ระบบจะคงการตั้งค่าเก่าไว้และเพิ่มรองรับหลายห้อง

### ข้อดี

- ใช้คำสั่งบอทได้จากหลายห้อง
- ส่งการแจ้งเตือนไปหลายห้องพร้อมกัน
- รองรับการตั้งค่าเก่าเพื่อความเข้ากันได้
- จัดการง่ายผ่านคำสั่งใน Discord

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

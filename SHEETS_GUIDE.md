# Google Sheets Integration - คำแนะนำการใช้งาน

## 📋 ภาพรวม
ระบบนี้จะบันทึกการตั้งค่า config.json ของ Cat Bot ลงใน Google Sheets โดยอัตโนมัติ เพื่อสำรองข้อมูลและติดตามการเปลี่ยนแปลงการตั้งค่า

## 🔧 การตั้งค่าเริ่มต้น

### 1. เตรียม Google Service Account
- ไปที่ [Google Cloud Console](https://console.cloud.google.com/)
- สร้างโปรเจคใหม่หรือเลือกโปรเจคที่มีอยู่
- เปิดใช้งาน Google Sheets API และ Google Drive API
- สร้าง Service Account และดาวน์โหลด JSON credentials
- เปลี่ยนชื่อไฟล์เป็น `credentials.json`

### 2. สร้าง Google Spreadsheet
- สร้าง Google Spreadsheet ใหม่
- คัดลอก ID จาก URL (ส่วนที่อยู่ระหว่าง `/d/` และ `/edit`)
- แชร์ Spreadsheet ให้กับ Service Account email ที่อยู่ในไฟล์ credentials.json

### 3. ตั้งค่าไฟล์ .env
```env
GOOGLE_SHEETS_ID="your_spreadsheet_id_here"
GOOGLE_SHEET_NAME="Cat_bot_Spreadsheets"
```

## 📊 โครงสร้างข้อมูลใน Google Sheets

| คอลัมน์ | คำอธิบาย |
|---------|----------|
| Timestamp | วันที่และเวลาที่บันทึกข้อมูล |
| Config Type | ประเภทของการอัปเดต (Full Config Update, Voice Channel, Voice Channel Update) |
| Channel ID | ID ของ voice channel (สำหรับการอัปเดต voice channel) |
| Empty Name | ชื่อเมื่อห้องว่าง |
| Occupied Name | ชื่อเมื่อห้องไม่ว่าง |
| Command Channel | ID ของ command channel |
| Notification Channel | ID ของ notification channel |
| Music Settings | การตั้งค่าเพลง (JSON format) |
| Full Config | ข้อมูล config เต็มรูปแบบ (JSON format) |

## 🚀 การใช้งาน

### ติดตั้งและทดสอบ
```bash
# ติดตั้ง dependencies และทดสอบระบบ
setup_sheets.bat

# หรือใช้คำสั่ง Python โดยตรง
pip install -r requirements.txt
python test_sheets.py
```

### ฟังก์ชันหลัก

#### 1. การบันทึกอัตโนมัติ
- ทุกครั้งที่มีการเปลี่ยนแปลง config.json จะถูกบันทึกลง Google Sheets โดยอัตโนมัติ
- การอัปเดต voice channel จะถูกบันทึกแยกต่างหาก

#### 2. การสำรองข้อมูล
```python
from config_manager import backup_config_to_sheets
backup_config_to_sheets()
```

#### 3. การกู้คืนข้อมูล
```python
from config_manager import restore_config_from_sheets
restore_config_from_sheets()
```

#### 4. การซิงค์ข้อมูล
```python
from config_manager import sync_config_with_sheets
sync_config_with_sheets()
```

## 🔍 การตรวจสอบสถานะ

### ทดสอบการเชื่อมต่อ
```bash
python test_sheets.py
```

### ตรวจสอบ logs
บอทจะแสดงข้อความเมื่อ:
- ✅ บันทึกข้อมูลสำเร็จ
- ⚠️ เกิดข้อผิดพลาดในการบันทึก
- 🔄 กำลังซิงค์ข้อมูล

## 🛠️ การแก้ไขปัญหา

### ปัญหา: ไม่สามารถเชื่อมต่อ Google Sheets ได้
**วิธีแก้:**
1. ตรวจสอบไฟล์ `credentials.json` ว่าถูกต้อง
2. ตรวจสอบ GOOGLE_SHEETS_ID ใน .env
3. ตรวจสอบว่าแชร์ Spreadsheet ให้ Service Account แล้ว
4. ตรวจสอบว่าเปิดใช้งาน Google Sheets API และ Google Drive API แล้ว

### ปัญหา: ได้รับ Permission Error
**วิธีแก้:**
1. ตรวจสอบสิทธิ์การเข้าถึง Spreadsheet
2. แชร์ Spreadsheet ให้ Service Account ด้วยสิทธิ์ Editor
3. ตรวจสอบว่า Service Account มีสิทธิ์เข้าถึง Google Drive

### ปัญหา: Worksheet ไม่พบ
**วิธีแก้:**
1. ตรวจสอบชื่อ Sheet ใน GOOGLE_SHEET_NAME
2. ระบบจะสร้าง Sheet ใหม่โดยอัตโนมัติถ้าไม่พบ

## 📈 คุณสมบัติพิเศษ

### 1. การติดตามประวัติ
- บันทึกทุกการเปลี่ยนแปลงพร้อม timestamp
- สามารถดูประวัติการเปลี่ยนแปลงย้อนหลังได้

### 2. การสำรองข้อมูลอัตโนมัติ
- บันทึกข้อมูลทุกครั้งที่มีการเปลี่ยนแปลง
- ไม่ต้องกังวลเรื่องข้อมูลสูญหาย

### 3. การซิงค์ข้อมูล
- ตรวจสอบความถูกต้องระหว่างไฟล์ local และ Google Sheets
- อัปเดตข้อมูลให้ตรงกันโดยอัตโนมัติ

## 🔐 ความปลอดภัย

### ข้อควรระวัง
- ไม่แชร์ไฟล์ `credentials.json` กับผู้อื่น
- ใส่ `credentials.json` ใน .gitignore
- ใช้ Service Account แทน OAuth สำหรับความปลอดภัย

### การจำกัดสิทธิ์
- Service Account ควรมีสิทธิ์เฉพาะ Spreadsheet ที่จำเป็น
- ไม่ควรให้สิทธิ์ Project Owner หรือ Editor

## 📞 การสนับสนุน

หากพบปัญหาในการใช้งาน:
1. ตรวจสอบ logs จากบอท
2. รันการทดสอบด้วย `python test_sheets.py`
3. ตรวจสอบการตั้งค่าตามคำแนะนำข้างต้น

---
*อัปเดตครั้งล่าสุด: มกราคม 2025*

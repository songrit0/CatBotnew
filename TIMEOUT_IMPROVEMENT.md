# Google Sheets Timeout Improvement - การปรับปรุง Timeout

## 🎯 สิ่งที่ได้ปรับปรุง

### ✅ การเพิ่ม Timeout Configuration
- **HTTP Timeout**: เพิ่มจาก default เป็น 60 วินาที
- **Socket Timeout**: ตั้งค่า socket timeout สำหรับป้องกันการค้าง
- **Connection Timeout**: ใช้ httplib2 สำหรับจัดการ connection timeout

### ✅ Retry Mechanism
- **Max Retries**: ลองใหม่สูงสุด 3 ครั้ง
- **Retry Delay**: รอ 2 วินาทีระหว่างการลองใหม่
- **Smart Recovery**: แยกประเภทข้อผิดพลาดเพื่อจัดการที่เหมาะสม

### ✅ ฟีเจอร์ที่เพิ่ม

#### 1. `_get_records_with_retry()`
- อ่านข้อมูลจาก Google Sheets พร้อม retry
- จัดการ timeout และ connection errors
- แสดง progress เมื่อกำลังโหลด

#### 2. `_update_with_retry()`
- อัปเดตข้อมูลพร้อม retry mechanism
- ป้องกันการสูญหายข้อมูลเมื่อ connection ช้า

#### 3. `_append_row_with_retry()`
- เพิ่มแถวใหม่พร้อม retry mechanism
- รองรับการเพิ่มข้อมูลเมื่อ network ไม่เสียร

## 🔧 การตั้งค่าที่เพิ่ม

### ใน `SheetsManager.__init__()`:
```python
# ตั้งค่า timeout และ retry
self.max_retries = 3          # จำนวนครั้งที่ลองใหม่
self.retry_delay = 2          # วินาทีที่รอระหว่างการลองใหม่
self.api_timeout = 60         # timeout สำหรับ API calls
```

### ใน `_initialize()`:
```python
# สร้าง client พร้อมตั้งค่า timeout เพิ่มขึ้น
import httplib2
http = httplib2.Http(timeout=60)  # เพิ่ม timeout เป็น 60 วินาที
self.client = gspread.authorize(creds, http=http)
```

## 📦 Dependencies ที่เพิ่ม

### ใน `requirements.txt`:
```
httplib2>=0.20.0
```

### ใน `sheets_manager.py`:
```python
import time
import socket
```

## 🎮 การใช้งาน

### การโหลดข้อมูลปกติ:
```python
# จะมี retry mechanism โดยอัตโนมัติ
config = sheets_manager.get_config_from_sheets()
```

### การอัปเดตข้อมูล:
```python
# จะมี retry mechanism โดยอัตโนมัติ
sheets_manager.update_config_value('key', 'value')
```

## 📊 การแสดงผล Logs

### เมื่อโหลดข้อมูล:
```
🔄 กำลังโหลดข้อมูลจาก Google Sheets (ครั้งที่ 1/3)...
✅ โหลดข้อมูลจาก Google Sheets สำเร็จ
```

### เมื่อเกิด Timeout:
```
⏰ Timeout ในการโหลดข้อมูล (ครั้งที่ 1): timed out
⏳ รอ 2 วินาทีก่อนลองใหม่...
🔄 กำลังโหลดข้อมูลจาก Google Sheets (ครั้งที่ 2/3)...
```

### เมื่ออัปเดตข้อมูล:
```
🔄 กำลังอัปเดตข้อมูลใน Google Sheets (ครั้งที่ 1/3)...
✅ อัปเดตข้อมูลสำเร็จ
```

## 🛠️ การแก้ไขปัญหา

### ปัญหา: ยังคงโหลดช้า
**วิธีแก้:**
1. เพิ่ม `api_timeout` ใน `__init__()`
2. เพิ่ม `max_retries` หากต้องการลองมากกว่า 3 ครั้ง
3. ลด `retry_delay` หากต้องการลองใหม่เร็วขึ้น

### ปัญหา: Connection ขาดบ่อย
**วิธีแก้:**
1. ตรวจสอบ internet connection
2. ตรวจสอบ Google Sheets API quota
3. ใช้ cache มากขึ้นเพื่อลดการเรียก API

### ปัญหา: ได้รับ HTTP 429 (Too Many Requests)
**วิธีแก้:**
1. เพิ่ม `retry_delay` เป็น 5-10 วินาที
2. ลด frequency ของการเรียก API
3. ใช้ cache เพื่อลดการเรียก API

## 📈 ประโยชน์

### 1. **ความเสียรภาพ**
- ระบบทำงานได้แม้ connection ช้า
- ลด error จาก timeout

### 2. **ประสิทธิภาพ**
- ลองใหม่อัตโนมัติเมื่อล้มเหลว
- แสดง progress ให้ผู้ใช้เห็น

### 3. **การจัดการข้อผิดพลาด**
- แยกประเภท timeout และ connection error
- แสดงข้อความที่เข้าใจง่าย

### 4. **การรองรับ Network ไม่เสียร**
- ทำงานได้แม้ network มีปัญหาชั่วคราว
- รักษาข้อมูลไม่ให้สูญหาย

---

**สถานะ**: ✅ **ปรับปรุงเสร็จสิ้น** - ระบบรองรับการโหลดช้าและ timeout ได้ดีขึ้น

*อัปเดตเมื่อ: กรกฎาคม 2025*

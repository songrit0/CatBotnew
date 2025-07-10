"""
Google Sheets Manager - จัดการการบันทึกและอ่านข้อมูลจาก Google Sheets
"""
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv
import time
import socket

# โหลด environment variables
load_dotenv()

class SheetsManager:
    def __init__(self):
        self.sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        self.sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Cat_bot_Spreadsheets')
        self.client = None
        self.worksheet = None
        self.config_cache = None  # Cache สำหรับ config
        self.cache_timestamp = None
        # ตั้งค่า timeout และ retry
        self.max_retries = 3
        self.retry_delay = 2
        self.api_timeout = 60
        self._initialize()
    
    def _get_credentials_from_env(self):
        """สร้าง credentials จาก environment variables"""
        # แก้ไข private key ให้มี newline ที่ถูกต้อง
        private_key = os.getenv('GOOGLE_PRIVATE_KEY', '')
        if private_key and '\\n' in private_key:
            private_key = private_key.replace('\\n', '\n')
        
        credentials_data = {
            "type": os.getenv('GOOGLE_SERVICE_ACCOUNT_TYPE'),
            "project_id": os.getenv('GOOGLE_PROJECT_ID'),
            "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
            "private_key": private_key,
            "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
            "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
            "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
            "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
            "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
        }
        return credentials_data
    
    def _initialize(self):
        """เริ่มต้นการเชื่อมต่อกับ Google Sheets"""
        try:
            # ตั้งค่า scope สำหรับ Google Sheets API
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # โหลด credentials จาก environment variables
            credentials_data = self._get_credentials_from_env()
            
            # ตรวจสอบว่าข้อมูล credentials ครบหรือไม่
            if not all(credentials_data.values()):
                raise ValueError("ข้อมูล Google Service Account ไม่ครบถ้วนใน .env file")
            
            # สร้าง credentials
            creds = Credentials.from_service_account_info(
                credentials_data, 
                scopes=scope
            )
            
            # สร้าง client พร้อมตั้งค่า timeout เพิ่มขึ้น
            self.client = gspread.authorize(creds)
            
            # เปิด spreadsheet
            spreadsheet = self.client.open_by_key(self.sheets_id)
            
            # พยายามเปิด worksheet หรือสร้างใหม่ถ้าไม่มี
            try:
                self.worksheet = spreadsheet.worksheet(self.sheet_name)
            except gspread.WorksheetNotFound:
                self.worksheet = spreadsheet.add_worksheet(
                    title=self.sheet_name, 
                    rows=1000, 
                    cols=10
                )
                # เพิ่ม header ให้ worksheet ใหม่
                self._setup_headers()
            
            print(f"✅ เชื่อมต่อ Google Sheets สำเร็จ: {self.sheet_name}")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {e}")
            self.client = None
            self.worksheet = None
    
    def _setup_headers(self):
        """ตั้งค่า header สำหรับ worksheet ใหม่"""
        headers = [
            'Config Key',
            'Config Value',
            'Data Type',
            'Last Updated',
            'Notes'
        ]
        self.worksheet.append_row(headers)
        
        # เพิ่มข้อมูลเริ่มต้น
        default_data = [
            ['voice_channels', '{}', 'json', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Voice channel configurations'],
            ['command_channels', '[]', 'json', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Command channel IDs (multiple)'],
            ['notification_channels', '[]', 'json', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Notification channel IDs (multiple)'],
            ['music_settings', '{"use_fallback": true, "max_retries": 3, "retry_delay": 2, "default_volume": 0.5, "max_queue_size": 50}', 'json', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Music player settings'],
            # รองรับรูปแบบเก่าเพื่อความเข้ากันได้
            ['command_channel', '', 'string', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Command channel ID (legacy)'],
            ['notification_channel', '', 'string', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Notification channel ID (legacy)']
        ]
        
        for row in default_data:
            self.worksheet.append_row(row)
    
    def get_config_from_sheets(self):
        """อ่านข้อมูล config จาก Google Sheets โดยตรง"""
        if not self.worksheet:
            print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
            return self._get_default_config()
        
        try:
            # ตรวจสอบ cache (ลด cache time เป็น 10 วินาที)
            current_time = datetime.now()
            if (self.config_cache and self.cache_timestamp and 
                (current_time - self.cache_timestamp).seconds < 10):
                return self.config_cache
            
            # อ่านข้อมูลจาก Google Sheets พร้อม retry mechanism
            all_records = self._get_records_with_retry()
            config = {}
            
            for record in all_records:
                key = record.get('Config Key', '')
                value = record.get('Config Value', '')
                data_type = record.get('Data Type', 'string')
                
                # แปลง key และ data_type เป็น string ก่อน
                key = str(key).strip() if key is not None else ''
                data_type = str(data_type).strip() if data_type is not None else 'string'
                value = str(value).strip() if value is not None else ''
                
                if not key:
                    continue
                
                # แปลงข้อมูลตาม data type
                if data_type == 'json' and value:
                    try:
                        config[key] = json.loads(value)
                    except json.JSONDecodeError:
                        print(f"⚠️ ไม่สามารถแปลง JSON สำหรับ {key}: {value}")
                        config[key] = {}
                elif data_type == 'integer' and value:
                    try:
                        config[key] = int(value)
                    except ValueError:
                        config[key] = None
                elif data_type == 'float' and value:
                    try:
                        config[key] = float(value)
                    except ValueError:
                        config[key] = None
                else:
                    config[key] = value if value else None
            
            # ตั้งค่าเริ่มต้นหากไม่มีข้อมูล
            if not config.get('voice_channels'):
                config['voice_channels'] = {}
            if not config.get('music_settings'):
                config['music_settings'] = {
                    "use_fallback": True,
                    "max_retries": 3,
                    "retry_delay": 2,
                    "default_volume": 0.5,
                    "max_queue_size": 50
                }
            
            # อัปเดต cache
            self.config_cache = config
            self.cache_timestamp = current_time
            
            return config
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการอ่านจาก Google Sheets: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """ส่งค่า config เริ่มต้น"""
        return {
            "voice_channels": {},
            "command_channels": [],
            "notification_channels": [],
            # รองรับรูปแบบเก่าเพื่อความเข้ากันได้
            "command_channel": None,
            "notification_channel": None,
            "music_settings": {
                "use_fallback": True,
                "max_retries": 3,
                "retry_delay": 2,
                "default_volume": 0.5,
                "max_queue_size": 50
            }
        }
    
    def update_config_value(self, key, value):
        """อัปเดตค่า config เฉพาะใน Google Sheets"""
        if not self.worksheet:
            print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
            return False
        
        try:
            # กำหนด data type
            data_type = 'string'
            if isinstance(value, dict) or isinstance(value, list):
                data_type = 'json'
                value = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, int):
                data_type = 'integer'
                value = str(value)
            elif isinstance(value, float):
                data_type = 'float'
                value = str(value)
            else:
                value = str(value) if value is not None else ''
            
            # ล้าง cache ก่อนค้นหา
            self.config_cache = None
            self.cache_timestamp = None
            
            # ค้นหาแถวที่มี key นี้ (ใช้ retry mechanism)
            all_records = self._get_records_with_retry()
            row_index = None
            
            for i, record in enumerate(all_records):
                if record.get('Config Key', '').strip() == key:
                    row_index = i + 2  # +2 เพราะ header อยู่แถว 1 และ index เริ่มต้นที่ 1
                    break
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if row_index:
                # อัปเดตแถวที่มีอยู่ (ใช้ retry mechanism)
                self._update_with_retry(f'B{row_index}:D{row_index}', [[value, data_type, timestamp]])
            else:
                # เพิ่มแถวใหม่ (ใช้ retry mechanism)
                new_row = [key, value, data_type, timestamp, f'Auto-created for {key}']
                self._append_row_with_retry(new_row)
            
            print(f"✅ อัปเดต {key} ใน Google Sheets สำเร็จ")
            
            # รอให้ Google Sheets update แล้วค่อยใช้งาน
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการอัปเดต {key}: {e}")
            return False
    
    def update_voice_channel(self, channel_id, empty_name, occupied_name):
        """อัปเดตการตั้งค่า voice channel ใน Google Sheets"""
        try:
            # อ่าน voice_channels ปัจจุบัน
            config = self.get_config_from_sheets()
            voice_channels = config.get('voice_channels', {})
            
            # อัปเดต voice channel
            voice_channels[str(channel_id)] = {
                'empty_name': empty_name,
                'occupied_name': occupied_name
            }
            
            # บันทึกกลับไปยัง Google Sheets
            return self.update_config_value('voice_channels', voice_channels)
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการอัปเดต voice channel: {e}")
            return False
    
    def remove_voice_channel(self, channel_id):
        """ลบการตั้งค่า voice channel จาก Google Sheets"""
        try:
            # อ่าน voice_channels ปัจจุบัน
            config = self.get_config_from_sheets()
            voice_channels = config.get('voice_channels', {})
            
            # ลบ voice channel
            if str(channel_id) in voice_channels:
                del voice_channels[str(channel_id)]
                return self.update_config_value('voice_channels', voice_channels)
            
            return True
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการลบ voice channel: {e}")
            return False
    
    def get_voice_channel_config(self, channel_id):
        """ดึงการตั้งค่าของ voice channel เฉพาะ"""
        config = self.get_config_from_sheets()
        return config.get("voice_channels", {}).get(str(channel_id))
    
    def clear_cache(self):
        """ล้าง cache เพื่อบังคับให้อ่านข้อมูลใหม่"""
        self.config_cache = None
        self.cache_timestamp = None

    def _get_records_with_retry(self, max_retries=None):
        """อ่านข้อมูลจาก Google Sheets พร้อม retry mechanism สำหรับการโหลดช้า"""
        if max_retries is None:
            max_retries = self.max_retries
            
        for attempt in range(max_retries):
            try:
                print(f"🔄 กำลังโหลดข้อมูลจาก Google Sheets (ครั้งที่ {attempt + 1}/{max_retries})...")
                
                # ตั้งค่า socket timeout เพื่อป้องกันการค้าง
                old_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(self.api_timeout)
                
                try:
                    all_records = self.worksheet.get_all_records()
                    print("✅ โหลดข้อมูลจาก Google Sheets สำเร็จ")
                    return all_records
                finally:
                    # คืนค่า timeout เดิม
                    socket.setdefaulttimeout(old_timeout)
                    
            except (socket.timeout, TimeoutError) as e:
                print(f"⏰ Timeout ในการโหลดข้อมูล (ครั้งที่ {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ รอ {self.retry_delay} วินาทีก่อนลองใหม่...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ โหลดข้อมูลไม่สำเร็จหลังจากลองหลายครั้ง")
                    raise
                    
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการโหลดข้อมูล (ครั้งที่ {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ รอ {self.retry_delay} วินาทีก่อนลองใหม่...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ โหลดข้อมูลไม่สำเร็จหลังจากลองหลายครั้ง")
                    raise
        
        return []

    def _update_with_retry(self, cell_range, values, max_retries=None):
        """อัปเดตข้อมูลใน Google Sheets พร้อม retry mechanism"""
        if max_retries is None:
            max_retries = self.max_retries
            
        for attempt in range(max_retries):
            try:
                print(f"🔄 กำลังอัปเดตข้อมูลใน Google Sheets (ครั้งที่ {attempt + 1}/{max_retries})...")
                
                # ตั้งค่า socket timeout
                old_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(self.api_timeout)
                
                try:
                    result = self.worksheet.update(cell_range, values)
                    print("✅ อัปเดตข้อมูลสำเร็จ")
                    return result
                finally:
                    socket.setdefaulttimeout(old_timeout)
                    
            except (socket.timeout, TimeoutError) as e:
                print(f"⏰ Timeout ในการอัปเดตข้อมูล (ครั้งที่ {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ รอ {self.retry_delay} วินาทีก่อนลองใหม่...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ อัปเดตข้อมูลไม่สำเร็จหลังจากลองหลายครั้ง")
                    raise
                    
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการอัปเดตข้อมูล (ครั้งที่ {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ รอ {self.retry_delay} วินาทีก่อนลองใหม่...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ อัปเดตข้อมูลไม่สำเร็จหลังจากลองหลายครั้ง")
                    raise
        
        return None

    def _append_row_with_retry(self, values, max_retries=None):
        """เพิ่มแถวใหม่ใน Google Sheets พร้อม retry mechanism"""
        if max_retries is None:
            max_retries = self.max_retries
            
        for attempt in range(max_retries):
            try:
                print(f"🔄 กำลังเพิ่มแถวใหม่ใน Google Sheets (ครั้งที่ {attempt + 1}/{max_retries})...")
                
                # ตั้งค่า socket timeout
                old_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(self.api_timeout)
                
                try:
                    result = self.worksheet.append_row(values)
                    print("✅ เพิ่มแถวใหม่สำเร็จ")
                    return result
                finally:
                    socket.setdefaulttimeout(old_timeout)
                    
            except (socket.timeout, TimeoutError) as e:
                print(f"⏰ Timeout ในการเพิ่มแถวใหม่ (ครั้งที่ {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ รอ {self.retry_delay} วินาทีก่อนลองใหม่...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ เพิ่มแถวใหม่ไม่สำเร็จหลังจากลองหลายครั้ง")
                    raise
                    
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการเพิ่มแถวใหม่ (ครั้งที่ {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ รอ {self.retry_delay} วินาทีก่อนลองใหม่...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ เพิ่มแถวใหม่ไม่สำเร็จหลังจากลองหลายครั้ง")
                    raise
        
        return None

# สร้าง instance ของ SheetsManager
sheets_manager = SheetsManager()

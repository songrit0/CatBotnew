"""
ล้างและตั้งค่า Google Sheets ใหม่
"""
from sheets_manager import sheets_manager
from datetime import datetime
import json

def clear_and_setup_sheets():
    """ล้างข้อมูลเก่าและตั้งค่า Google Sheets ใหม่"""
    print("🧹 ล้างและตั้งค่า Google Sheets ใหม่")
    print("=" * 50)
    
    try:
        # ล้างข้อมูลเก่าทั้งหมด
        print("1. ล้างข้อมูลเก่า...")
        sheets_manager.worksheet.clear()
        
        # ตั้งค่า header ใหม่
        print("2. ตั้งค่า header ใหม่...")
        headers = [
            'Config Key',
            'Config Value', 
            'Data Type',
            'Last Updated',
            'Notes'
        ]
        sheets_manager.worksheet.append_row(headers)
        
        # เพิ่มข้อมูลเริ่มต้น
        print("3. เพิ่มข้อมูลเริ่มต้น...")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        default_data = [
            ['voice_channels', '{}', 'json', timestamp, 'Voice channel configurations'],
            ['command_channel', '', 'string', timestamp, 'Command channel ID'],
            ['notification_channel', '', 'string', timestamp, 'Notification channel ID'],
            ['music_settings', '{"use_fallback": true, "max_retries": 3, "retry_delay": 2, "default_volume": 0.5, "max_queue_size": 50}', 'json', timestamp, 'Music player settings']
        ]
        
        for row in default_data:
            sheets_manager.worksheet.append_row(row)
            print(f"   ✅ เพิ่ม {row[0]}")
        
        # ล้าง cache
        sheets_manager.clear_cache()
        
        print("✅ ตั้งค่า Google Sheets ใหม่เสร็จสิ้น")
        
        # ทดสอบการอ่านข้อมูล
        print("\n🔍 ทดสอบการอ่านข้อมูลใหม่:")
        config = sheets_manager.get_config_from_sheets()
        print(f"✅ Config: {json.dumps(config, ensure_ascii=False, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    clear_and_setup_sheets()

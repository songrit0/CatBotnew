"""
Config Manager - จัดการการโหลดและบันทึกการตั้งค่า
ใช้ Google Sheets เป็นแหล่งเก็บข้อมูลหลัก ไม่ใช้ config.json แล้ว
"""
import json
import os
from datetime import datetime
from sheets_manager import sheets_manager

def load_config():
    """โหลดการตั้งค่าจาก Google Sheets"""
    try:
        config = sheets_manager.get_config_from_sheets()
        print("✅ โหลดการตั้งค่าจาก Google Sheets สำเร็จ")
        return config
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการโหลดการตั้งค่า: {e}")
        return create_default_config()

def save_config(config):
    """บันทึกการตั้งค่าไปยัง Google Sheets (ไม่ใช้ไฟล์ local แล้ว)"""
    try:
        # บันทึกแต่ละค่าใน config ลง Google Sheets
        success_count = 0
        total_keys = len(config)
        
        for key, value in config.items():
            if sheets_manager.update_config_value(key, value):
                success_count += 1
        
        if success_count == total_keys:
            print("✅ บันทึกการตั้งค่าลง Google Sheets สำเร็จ")
            return True
        else:
            print(f"⚠️ บันทึกสำเร็จ {success_count}/{total_keys} รายการ")
            return False
            
    except Exception as e:
        print(f"❌ ไม่สามารถบันทึกการตั้งค่าได้: {e}")
        return False

def create_default_config():
    """สร้างการตั้งค่าเริ่มต้นใน Google Sheets"""
    default_config = {
        "voice_channels": {},
        "command_channels": [],
        "notification_channels": [],
        "music_settings": {
            "use_fallback": True,
            "max_retries": 3,
            "retry_delay": 2,
            "default_volume": 0.5,
            "max_queue_size": 50
        }
    }
    
    # บันทึกลง Google Sheets
    if save_config(default_config):
        print("✅ สร้างการตั้งค่าเริ่มต้นใน Google Sheets สำเร็จ")
    else:
        print("⚠️ ไม่สามารถสร้างการตั้งค่าเริ่มต้นใน Google Sheets ได้")
    
    return default_config

def get_voice_channel_config(channel_id):
    """ดึงการตั้งค่าของ voice channel เฉพาะจาก Google Sheets"""
    return sheets_manager.get_voice_channel_config(channel_id)

def update_voice_channel_config(channel_id, empty_name, occupied_name):
    """อัปเดตการตั้งค่าของ voice channel ใน Google Sheets"""
    return sheets_manager.update_voice_channel(channel_id, empty_name, occupied_name)

def remove_voice_channel_config(channel_id):
    """ลบการตั้งค่าของ voice channel จาก Google Sheets"""
    return sheets_manager.remove_voice_channel(channel_id)

def update_command_channel(channel_id):
    """อัปเดต command channel ใน Google Sheets"""
    return sheets_manager.update_config_value('command_channels', str(channel_id) if channel_id else None)

def update_notification_channel(channel_id):
    """อัปเดต notification channel ใน Google Sheets"""
    return sheets_manager.update_config_value('notification_channels', str(channel_id) if channel_id else None)

def add_command_channel(channel_id):
    """เพิ่ม command channel ลงใน list"""
    config = load_config()
    command_channels = config.get("command_channels", [])
    
    if str(channel_id) not in command_channels:
        command_channels.append(str(channel_id))
        return sheets_manager.update_config_value('command_channels', command_channels)
    return True

def remove_command_channel(channel_id):
    """ลบ command channel จาก list"""
    config = load_config()
    command_channels = config.get("command_channels", [])
    
    if str(channel_id) in command_channels:
        command_channels.remove(str(channel_id))
        return sheets_manager.update_config_value('command_channels', command_channels)
    return True

def add_notification_channel(channel_id):
    """เพิ่ม notification channel ลงใน list"""
    config = load_config()
    notification_channels = config.get("notification_channels", [])
    
    if str(channel_id) not in notification_channels:
        notification_channels.append(str(channel_id))
        return sheets_manager.update_config_value('notification_channels', notification_channels)
    return True

def remove_notification_channel(channel_id):
    """ลบ notification channel จาก list"""
    config = load_config()
    notification_channels = config.get("notification_channels", [])
    
    if str(channel_id) in notification_channels:
        notification_channels.remove(str(channel_id))
        return sheets_manager.update_config_value('notification_channels', notification_channels)
    return True

def is_special_channel(channel_id):
    """ตรวจสอบว่าเป็นห้องพิเศษหรือไม่"""
    config = load_config()
    command_channels = config.get("command_channels", [])
    
    # รองรับทั้งรูปแบบเก่า (single channel) และใหม่ (multiple channels)
    if command_channels:
        return str(channel_id) in command_channels
    
    # รองรับรูปแบบเก่าเพื่อความเข้ากันได้
    command_channel_id = config.get("command_channel")
    if command_channel_id:
        return channel_id == int(command_channel_id)
    
    return False

def refresh_config_cache():
    """รีเฟรช cache ของ config จาก Google Sheets"""
    sheets_manager.clear_cache()
    print("🔄 รีเฟรช cache การตั้งค่าจาก Google Sheets")

def backup_config_to_sheets():
    """สำรองข้อมูล config ปัจจุบันลง Google Sheets"""
    try:
        config = load_config()
        success = save_config(config)
        if success:
            print("✅ สำรองข้อมูล config ลง Google Sheets สำเร็จ")
        else:
            print("❌ ไม่สามารถสำรองข้อมูล config ได้")
        return success
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสำรองข้อมูล: {e}")
        return False

def restore_config_from_sheets():
    """กู้คืนข้อมูล config จาก Google Sheets"""
    try:
        config = sheets_manager.get_config_from_sheets()
        print("✅ กู้คืนข้อมูล config จาก Google Sheets สำเร็จ")
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการกู้คืนข้อมูล: {e}")
        return False

def sync_config_with_sheets():
    """ซิงค์ข้อมูล config ระหว่าง local และ Google Sheets"""
    try:
        # ล้าง cache ก่อน
        refresh_config_cache()
        
        # โหลดข้อมูลจาก Google Sheets
        config = load_config()
        
        print("✅ ซิงค์ข้อมูล config กับ Google Sheets สำเร็จ")
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการซิงค์ข้อมูล: {e}")
        return False

def migrate_from_json():
    """ย้ายข้อมูลจาก config.json ไปยัง Google Sheets (ใช้ครั้งเดียว)"""
    try:
        if not os.path.exists('config.json'):
            print("ℹ️ ไม่พบไฟล์ config.json เพื่อย้ายข้อมูล")
            return True
        
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        print("🔄 กำลังย้ายข้อมูลจาก config.json ไปยัง Google Sheets...")
        
        # ย้ายข้อมูลไปยัง Google Sheets
        success = save_config(config_data)
        
        if success:
            # สำรองไฟล์เดิม
            backup_filename = f'config_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            os.rename('config.json', backup_filename)
            print(f"✅ ย้ายข้อมูลสำเร็จ ไฟล์เดิมถูกสำรองเป็น {backup_filename}")
            return True
        else:
            print("❌ ไม่สามารถย้ายข้อมูลได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการย้ายข้อมูล: {e}")
        return False

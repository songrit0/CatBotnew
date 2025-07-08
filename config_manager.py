"""
Config Manager - จัดการการโหลดและบันทึกการตั้งค่า
"""
import json
import os

def load_config():
    """โหลดการตั้งค่าจาก config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ ไม่พบไฟล์ config.json")
        return create_default_config()
    except json.JSONDecodeError:
        print("❌ ไฟล์ config.json มีรูปแบบไม่ถูกต้อง")
        return create_default_config()

def save_config(config):
    """บันทึกการตั้งค่าไปยัง config.json"""
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ ไม่สามารถบันทึกการตั้งค่าได้: {e}")
        return False

def create_default_config():
    """สร้างการตั้งค่าเริ่มต้น"""
    default_config = {
        "voice_channels": {},
        "command_channel": None,
        "notification_channel": None
    }
    save_config(default_config)
    return default_config

def get_voice_channel_config(channel_id):
    """ดึงการตั้งค่าของ voice channel เฉพาะ"""
    config = load_config()
    return config.get("voice_channels", {}).get(str(channel_id))

def update_voice_channel_config(channel_id, empty_name, occupied_name):
    """อัปเดตการตั้งค่าของ voice channel"""
    config = load_config()
    config["voice_channels"][str(channel_id)] = {
        "empty_name": empty_name,
        "occupied_name": occupied_name
    }
    return save_config(config)

def remove_voice_channel_config(channel_id):
    """ลบการตั้งค่าของ voice channel"""
    config = load_config()
    if str(channel_id) in config["voice_channels"]:
        del config["voice_channels"][str(channel_id)]
        return save_config(config)
    return False

def is_special_channel(channel_id):
    """ตรวจสอบว่าเป็นห้องพิเศษหรือไม่"""
    config = load_config()
    command_channel_id = config.get("command_channel")
    if command_channel_id:
        return channel_id == int(command_channel_id)
    return False

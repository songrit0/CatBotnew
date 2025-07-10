"""
เพิ่มข้อมูลทดสอบลง Google Sheets ใหม่
"""
from config_manager import (
    update_voice_channel_config,
    update_command_channel,
    update_notification_channel,
    load_config
)
import json

def add_demo_data():
    """เพิ่มข้อมูลทดสอบ"""
    print("🎯 เพิ่มข้อมูลทดสอบลง Google Sheets")
    print("=" * 50)
    
    # เพิ่ม voice channels ตัวอย่าง
    voice_channels = [
        ("1391757507256516678", "ห้องว่าง", "ห้องไม่ว่าง"),
        ("1391673586346885180", "Live offline", "Live online"),
        ("1234567890123456789", "ห้องเสียงทั่วไป (ว่าง)", "ห้องเสียงทั่วไป (มีคน)"),
    ]
    
    for channel_id, empty_name, occupied_name in voice_channels:
        success = update_voice_channel_config(channel_id, empty_name, occupied_name)
        if success:
            print(f"✅ เพิ่ม voice channel {channel_id}: {empty_name} / {occupied_name}")
        else:
            print(f"❌ ไม่สามารถเพิ่ม voice channel {channel_id} ได้")
    
    # ตั้งค่า command channel
    command_channel = "1391779625423863838"
    success = update_command_channel(command_channel)
    if success:
        print(f"✅ ตั้งค่า command channel: {command_channel}")
    else:
        print(f"❌ ไม่สามารถตั้งค่า command channel ได้")
    
    # ตั้งค่า notification channel
    notification_channel = "1391779625423863838"
    success = update_notification_channel(notification_channel)
    if success:
        print(f"✅ ตั้งค่า notification channel: {notification_channel}")
    else:
        print(f"❌ ไม่สามารถตั้งค่า notification channel ได้")
    
    print("\n🔍 ตรวจสอบข้อมูลที่บันทึก:")
    config = load_config()
    print(f"📊 ข้อมูลใน Google Sheets:")
    print(json.dumps(config, ensure_ascii=False, indent=2))
    
    print(f"\n📈 สรุป:")
    print(f"   - Voice Channels: {len(config.get('voice_channels', {}))}")
    print(f"   - Command Channel: {config.get('command_channel')}")
    print(f"   - Notification Channel: {config.get('notification_channel')}")
    print(f"   - Music Settings: {'✅ มี' if config.get('music_settings') else '❌ ไม่มี'}")

if __name__ == "__main__":
    add_demo_data()

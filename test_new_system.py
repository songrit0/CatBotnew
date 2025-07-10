"""
ทดสอบระบบใหม่ที่ใช้ Google Sheets เป็นแหล่งเก็บข้อมูลหลัก
"""
import sys
import os
from sheets_manager import sheets_manager
from config_manager import (
    load_config, 
    save_config,
    get_voice_channel_config,
    update_voice_channel_config,
    remove_voice_channel_config,
    update_command_channel,
    update_notification_channel,
    migrate_from_json,
    refresh_config_cache
)

def test_sheets_connection():
    """ทดสอบการเชื่อมต่อ Google Sheets"""
    print("=" * 50)
    print("🔍 ทดสอบการเชื่อมต่อ Google Sheets")
    print("=" * 50)
    
    if sheets_manager.client and sheets_manager.worksheet:
        print("✅ เชื่อมต่อ Google Sheets สำเร็จ")
        print(f"📊 Spreadsheet ID: {sheets_manager.sheets_id}")
        print(f"📋 Sheet Name: {sheets_manager.sheet_name}")
        return True
    else:
        print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
        return False

def test_data_migration():
    """ทดสอบการย้ายข้อมูลจาก config.json"""
    print("\n" + "=" * 50)
    print("📦 ทดสอบการย้ายข้อมูลจาก config.json")
    print("=" * 50)
    
    success = migrate_from_json()
    if success:
        print("✅ ย้ายข้อมูลจาก config.json สำเร็จ")
    else:
        print("❌ ไม่สามารถย้ายข้อมูลได้ (อาจไม่มีไฟล์หรือมีปัญหา)")
    
    return success

def test_config_loading():
    """ทดสอบการโหลด config จาก Google Sheets"""
    print("\n" + "=" * 50)
    print("📖 ทดสอบการโหลด config จาก Google Sheets")
    print("=" * 50)
    
    try:
        config = load_config()
        print(f"✅ โหลด config สำเร็จ")
        print(f"📊 Voice Channels: {len(config.get('voice_channels', {}))}")
        print(f"📋 Command Channel: {config.get('command_channel', 'ไม่ได้ตั้งค่า')}")
        print(f"📢 Notification Channel: {config.get('notification_channel', 'ไม่ได้ตั้งค่า')}")
        print(f"🎵 Music Settings: {bool(config.get('music_settings'))}")
        return True
    except Exception as e:
        print(f"❌ ไม่สามารถโหลด config ได้: {e}")
        return False

def test_voice_channel_operations():
    """ทดสอบการจัดการ voice channel"""
    print("\n" + "=" * 50)
    print("🔊 ทดสอบการจัดการ voice channel")
    print("=" * 50)
    
    test_channel_id = "9876543210987654321"
    test_empty_name = "ห้องทดสอบว่าง (ใหม่)"
    test_occupied_name = "ห้องทดสอบไม่ว่าง (ใหม่)"
    
    try:
        # ทดสอบการเพิ่ม/อัปเดต voice channel
        print("1. ทดสอบการเพิ่ม voice channel...")
        success = update_voice_channel_config(test_channel_id, test_empty_name, test_occupied_name)
        if success:
            print(f"✅ เพิ่ม voice channel {test_channel_id} สำเร็จ")
        else:
            print(f"❌ ไม่สามารถเพิ่ม voice channel ได้")
            return False
        
        # ทดสอบการอ่าน voice channel
        print("2. ทดสอบการอ่าน voice channel...")
        channel_config = get_voice_channel_config(test_channel_id)
        if channel_config:
            print(f"✅ อ่าน voice channel สำเร็จ: {channel_config}")
        else:
            print(f"❌ ไม่พบ voice channel")
            return False
        
        # ทดสอบการลบ voice channel
        print("3. ทดสอบการลบ voice channel...")
        success = remove_voice_channel_config(test_channel_id)
        if success:
            print(f"✅ ลบ voice channel {test_channel_id} สำเร็จ")
        else:
            print(f"❌ ไม่สามารถลบ voice channel ได้")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ voice channel: {e}")
        return False

def test_channel_settings():
    """ทดสอบการตั้งค่า command และ notification channel"""
    print("\n" + "=" * 50)
    print("⚙️ ทดสอบการตั้งค่า channel")
    print("=" * 50)
    
    test_command_channel = "1111111111111111111"
    test_notification_channel = "2222222222222222222"
    
    try:
        # ทดสอบการตั้งค่า command channel
        print("1. ทดสอบการตั้งค่า command channel...")
        success = update_command_channel(test_command_channel)
        if success:
            print(f"✅ ตั้งค่า command channel สำเร็จ")
        else:
            print(f"❌ ไม่สามารถตั้งค่า command channel ได้")
            return False
        
        # ทดสอบการตั้งค่า notification channel
        print("2. ทดสอบการตั้งค่า notification channel...")
        success = update_notification_channel(test_notification_channel)
        if success:
            print(f"✅ ตั้งค่า notification channel สำเร็จ")
        else:
            print(f"❌ ไม่สามารถตั้งค่า notification channel ได้")
            return False
        
        # ตรวจสอบการโหลดข้อมูลใหม่
        print("3. ทดสอบการโหลดข้อมูลหลังการอัปเดต...")
        refresh_config_cache()  # ล้าง cache
        config = load_config()
        
        if (config.get('command_channel') == test_command_channel and 
            config.get('notification_channel') == test_notification_channel):
            print("✅ ข้อมูลถูกบันทึกและโหลดสำเร็จ")
            return True
        else:
            print("❌ ข้อมูลไม่ตรงกับที่บันทึก")
            return False
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบการตั้งค่า channel: {e}")
        return False

def test_cache_system():
    """ทดสอบระบบ cache"""
    print("\n" + "=" * 50)
    print("💾 ทดสอบระบบ cache")
    print("=" * 50)
    
    try:
        # โหลดข้อมูลครั้งแรก
        print("1. โหลดข้อมูลครั้งแรก...")
        config1 = load_config()
        
        # โหลดข้อมูลครั้งที่สอง (ควรใช้ cache)
        print("2. โหลดข้อมูลครั้งที่สอง (ใช้ cache)...")
        config2 = load_config()
        
        if config1 == config2:
            print("✅ Cache ทำงานถูกต้อง")
        else:
            print("⚠️ Cache อาจมีปัญหา")
        
        # ล้าง cache และโหลดใหม่
        print("3. ล้าง cache และโหลดใหม่...")
        refresh_config_cache()
        config3 = load_config()
        
        if config1 == config3:
            print("✅ การล้าง cache ทำงานถูกต้อง")
            return True
        else:
            print("⚠️ การล้าง cache อาจมีปัญหา")
            return False
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ cache: {e}")
        return False

def main():
    """เรียกใช้การทดสอบทั้งหมด"""
    print("🤖 Cat Bot - ทดสอบระบบ Google Sheets (ไม่ใช้ config.json)")
    print("=" * 70)
    
    # ตรวจสอบไฟล์ที่จำเป็น
    required_files = ['.env']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ ไม่พบไฟล์ที่จำเป็น: {', '.join(missing_files)}")
        print("📋 โปรดตรวจสอบว่าไฟล์เหล่านี้อยู่ในโฟลเดอร์เดียวกัน")
        return
    
    print("✅ พบไฟล์ที่จำเป็นครบถ้วน")
    
    # เรียกใช้การทดสอบ
    tests = [
        test_sheets_connection,
        test_data_migration,
        test_config_loading,
        test_voice_channel_operations,
        test_channel_settings,
        test_cache_system
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
            results.append(False)
    
    # สรุปผลการทดสอบ
    print("\n" + "=" * 70)
    print("📊 สรุปผลการทดสอบ")
    print("=" * 70)
    
    test_names = [
        "การเชื่อมต่อ Google Sheets",
        "การย้ายข้อมูลจาก config.json",
        "การโหลด config จาก Google Sheets",
        "การจัดการ voice channel",
        "การตั้งค่า channel",
        "ระบบ cache"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ ผ่าน" if result else "❌ ไม่ผ่าน"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n🎯 ผลการทดสอบ: {passed}/{total} ผ่าน")
    
    if passed == total:
        print("🎉 การทดสอบทั้งหมดผ่าน! ระบบ Google Sheets พร้อมใช้งาน")
        print("💡 ระบบจะไม่ใช้ config.json อีกต่อไป ข้อมูลทั้งหมดจะเก็บใน Google Sheets")
    else:
        print("⚠️ มีการทดสอบบางส่วนที่ไม่ผ่าน โปรดตรวจสอบการตั้งค่า")

if __name__ == "__main__":
    main()

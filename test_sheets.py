"""
ทดสอบการเชื่อมต่อและการทำงานของ Google Sheets
"""
import sys
import os
from sheets_manager import sheets_manager
from config_manager import (
    load_config, 
    save_config, 
    backup_config_to_sheets, 
    restore_config_from_sheets,
    sync_config_with_sheets
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

def test_config_backup():
    """ทดสอบการสำรองข้อมูล config ลง Google Sheets"""
    print("\n" + "=" * 50)
    print("💾 ทดสอบการสำรองข้อมูล config")
    print("=" * 50)
    
    success = backup_config_to_sheets()
    if success:
        print("✅ สำรองข้อมูล config ลง Google Sheets สำเร็จ")
    else:
        print("❌ ไม่สามารถสำรองข้อมูล config ได้")
    
    return success

def test_config_restore():
    """ทดสอบการกู้คืนข้อมูล config จาก Google Sheets"""
    print("\n" + "=" * 50)
    print("🔄 ทดสอบการกู้คืนข้อมูล config")
    print("=" * 50)
    
    # สำรองไฟล์ config เดิมก่อน
    original_config = load_config()
    
    # ทดสอบกู้คืน
    success = restore_config_from_sheets()
    if success:
        print("✅ กู้คืนข้อมูล config จาก Google Sheets สำเร็จ")
        
        # ตรวจสอบว่าข้อมูลถูกต้อง
        restored_config = load_config()
        print(f"📊 ข้อมูลที่กู้คืน: {len(restored_config.get('voice_channels', {}))} voice channels")
    else:
        print("❌ ไม่สามารถกู้คืนข้อมูล config ได้")
    
    return success

def test_config_sync():
    """ทดสอบการซิงค์ข้อมูล config"""
    print("\n" + "=" * 50)
    print("🔄 ทดสอบการซิงค์ข้อมูล config")
    print("=" * 50)
    
    success = sync_config_with_sheets()
    if success:
        print("✅ ซิงค์ข้อมูล config สำเร็จ")
    else:
        print("❌ ไม่สามารถซิงค์ข้อมูล config ได้")
    
    return success

def test_voice_channel_update():
    """ทดสอบการอัปเดต voice channel"""
    print("\n" + "=" * 50)
    print("🔊 ทดสอบการอัปเดต voice channel")
    print("=" * 50)
    
    from config_manager import update_voice_channel_config
    
    test_channel_id = "1234567890123456789"
    test_empty_name = "ห้องทดสอบว่าง"
    test_occupied_name = "ห้องทดสอบไม่ว่าง"
    
    success = update_voice_channel_config(test_channel_id, test_empty_name, test_occupied_name)
    if success:
        print(f"✅ อัปเดต voice channel {test_channel_id} สำเร็จ")
        print(f"📝 ชื่อเมื่อว่าง: {test_empty_name}")
        print(f"📝 ชื่อเมื่อไม่ว่าง: {test_occupied_name}")
    else:
        print("❌ ไม่สามารถอัปเดต voice channel ได้")
    
    return success

def main():
    """เรียกใช้การทดสอบทั้งหมด"""
    print("🤖 Cat Bot - ทดสอบ Google Sheets Integration")
    print("=" * 60)
    
    # ตรวจสอบไฟล์ที่จำเป็น
    required_files = ['.env', 'config.json']
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
        test_config_backup,
        test_config_restore,
        test_config_sync,
        test_voice_channel_update
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
    print("\n" + "=" * 60)
    print("📊 สรุปผลการทดสอบ")
    print("=" * 60)
    
    test_names = [
        "การเชื่อมต่อ Google Sheets",
        "การสำรองข้อมูล config", 
        "การกู้คืนข้อมูล config",
        "การซิงค์ข้อมูล config",
        "การอัปเดต voice channel"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ ผ่าน" if result else "❌ ไม่ผ่าน"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n🎯 ผลการทดสอบ: {passed}/{total} ผ่าน")
    
    if passed == total:
        print("🎉 การทดสอบทั้งหมดผ่าน! Google Sheets integration พร้อมใช้งาน")
    else:
        print("⚠️ มีการทดสอบบางส่วนที่ไม่ผ่าน โปรดตรวจสอบการตั้งค่า")

if __name__ == "__main__":
    main()

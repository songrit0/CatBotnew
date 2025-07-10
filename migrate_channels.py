"""
Migration Script - อัปเดต Google Sheets ให้รองรับ command_channels และ notification_channels แบบหลายห้อง
"""
from sheets_manager import sheets_manager
from config_manager import load_config
import json

def migrate_to_multiple_channels():
    """อัปเดต Google Sheets ให้รองรับหลายห้อง"""
    print("🔄 เริ่มต้นการอัปเดต Google Sheets...")
    
    try:
        # โหลด config ปัจจุบัน
        config = load_config()
        
        # ตรวจสอบว่ามีข้อมูลรูปแบบเก่าหรือไม่
        command_channel = config.get("command_channel")
        notification_channel = config.get("notification_channel")
        
        # เพิ่ม command_channels ใหม่
        command_channels = config.get("command_channels", [])
        if command_channel and command_channel not in command_channels:
            command_channels.append(command_channel)
        
        # เพิ่ม notification_channels ใหม่
        notification_channels = config.get("notification_channels", [])
        if notification_channel and notification_channel not in notification_channels:
            notification_channels.append(notification_channel)
        
        # อัปเดตไปยัง Google Sheets
        success_count = 0
        
        # อัปเดต command_channels
        if sheets_manager.update_config_value('command_channels', command_channels):
            print(f"✅ อัปเดต command_channels: {command_channels}")
            success_count += 1
        else:
            print("❌ ไม่สามารถอัปเดต command_channels ได้")
        
        # อัปเดต notification_channels
        if sheets_manager.update_config_value('notification_channels', notification_channels):
            print(f"✅ อัปเดต notification_channels: {notification_channels}")
            success_count += 1
        else:
            print("❌ ไม่สามารถอัปเดต notification_channels ได้")
        
        if success_count == 2:
            print("✅ อัปเดต Google Sheets สำเร็จทั้งหมด")
            
            # แสดงผลลัพธ์
            print("\n📋 การตั้งค่าใหม่:")
            print(f"   - Command Channels: {command_channels}")
            print(f"   - Notification Channels: {notification_channels}")
            
            return True
        else:
            print(f"⚠️ อัปเดตสำเร็จเพียง {success_count}/2 รายการ")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอัปเดต: {e}")
        return False

def verify_migration():
    """ตรวจสอบการอัปเดต"""
    print("\n🔍 ตรวจสอบการอัปเดต...")
    
    try:
        config = load_config()
        
        print("📋 การตั้งค่าปัจจุบัน:")
        print(f"   - Command Channels: {config.get('command_channels', [])}")
        print(f"   - Notification Channels: {config.get('notification_channels', [])}")
        print(f"   - Command Channel (เก่า): {config.get('command_channel')}")
        print(f"   - Notification Channel (เก่า): {config.get('notification_channel')}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔄 Migration Script - อัปเดตระบบหลายห้อง")
    print("=" * 50)
    
    # ทำการอัปเดต
    if migrate_to_multiple_channels():
        # ตรวจสอบผลลัพธ์
        verify_migration()
        print("\n✅ การอัปเดตเสร็จสมบูรณ์!")
        print("\n📌 คำสั่งใหม่ที่สามารถใช้ได้:")
        print("   - !add_command_channel [#channel]")
        print("   - !remove_command_channel [#channel]")
        print("   - !add_notification_channel [#channel]")
        print("   - !remove_notification_channel [#channel]")
        print("   - !list_channels")
    else:
        print("\n❌ การอัปเดตไม่สำเร็จ กรุณาตรวจสอบข้อผิดพลาด")

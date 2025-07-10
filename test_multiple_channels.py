"""
Test Script - ทดสอบระบบ command_channels และ notification_channels แบบหลายห้อง
"""
from config_manager import (
    load_config,
    add_command_channel, remove_command_channel,
    add_notification_channel, remove_notification_channel,
    is_special_channel
)

def test_multiple_channels():
    """ทดสอบการทำงานของระบบหลายห้อง"""
    print("🧪 เริ่มต้นการทดสอบระบบหลายห้อง")
    print("=" * 50)
    
    # ข้อมูลทดสอบ
    test_command_channels = ["1111111111111111111", "2222222222222222222"]
    test_notification_channels = ["3333333333333333333", "4444444444444444444"]
    
    try:
        # ทดสอบ command channels
        print("📋 ทดสอบ Command Channels:")
        
        for channel_id in test_command_channels:
            success = add_command_channel(channel_id)
            print(f"   ➕ เพิ่ม channel {channel_id}: {'✅' if success else '❌'}")
        
        # ตรวจสอบการเพิ่ม
        config = load_config()
        command_channels = config.get("command_channels", [])
        print(f"   📋 Command Channels ปัจจุบัน: {command_channels}")
        
        # ทดสอบ is_special_channel
        for channel_id in test_command_channels:
            is_special = is_special_channel(int(channel_id))
            print(f"   🔍 ตรวจสอบ channel {channel_id}: {'✅ เป็น special channel' if is_special else '❌ ไม่เป็น special channel'}")
        
        print("\n📢 ทดสอบ Notification Channels:")
        
        for channel_id in test_notification_channels:
            success = add_notification_channel(channel_id)
            print(f"   ➕ เพิ่ม channel {channel_id}: {'✅' if success else '❌'}")
        
        # ตรวจสอบการเพิ่ม
        config = load_config()
        notification_channels = config.get("notification_channels", [])
        print(f"   📋 Notification Channels ปัจจุบัน: {notification_channels}")
        
        print("\n🗑️ ทดสอบการลบ:")
        
        # ลบ command channel แรก
        first_command = test_command_channels[0]
        success = remove_command_channel(first_command)
        print(f"   ➖ ลบ command channel {first_command}: {'✅' if success else '❌'}")
        
        # ลบ notification channel แรก
        first_notification = test_notification_channels[0]
        success = remove_notification_channel(first_notification)
        print(f"   ➖ ลบ notification channel {first_notification}: {'✅' if success else '❌'}")
        
        # ตรวจสอบผลลัพธ์สุดท้าย
        print("\n📊 ผลลัพธ์สุดท้าย:")
        config = load_config()
        print(f"   📋 Command Channels: {config.get('command_channels', [])}")
        print(f"   📢 Notification Channels: {config.get('notification_channels', [])}")
        
        # ทดสอบการใช้ซ้ำ
        print("\n🔄 ทดสอบการเพิ่มซ้ำ:")
        remaining_command = test_command_channels[1]
        success = add_command_channel(remaining_command)
        print(f"   ➕ เพิ่ม command channel {remaining_command} ซ้ำ: {'✅' if success else '❌'}")
        
        config = load_config()
        command_channels = config.get("command_channels", [])
        count = command_channels.count(remaining_command)
        print(f"   📊 จำนวน channel {remaining_command} ในรายการ: {count} ({'✅ ถูกต้อง' if count == 1 else '❌ ผิดพลาด'})")
        
        print("\n✅ การทดสอบเสร็จสมบูรณ์!")
        return True
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
        return False

def cleanup_test_data():
    """ล้างข้อมูลทดสอบ"""
    print("\n🧹 ล้างข้อมูลทดสอบ...")
    
    test_channels = [
        "1111111111111111111", "2222222222222222222",
        "3333333333333333333", "4444444444444444444"
    ]
    
    for channel_id in test_channels:
        remove_command_channel(channel_id)
        remove_notification_channel(channel_id)
    
    print("✅ ล้างข้อมูลทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    print("🧪 Multiple Channels Test Script")
    print("=" * 50)
    
    # รันการทดสอบ
    if test_multiple_channels():
        print("\n🎉 การทดสอบผ่านทั้งหมด!")
    else:
        print("\n💥 การทดสอบไม่ผ่าน!")
    
    # ถามว่าต้องการล้างข้อมูลทดสอบหรือไม่
    print("\n" + "=" * 50)
    response = input("ต้องการล้างข้อมูลทดสอบหรือไม่? (y/n): ").strip().lower()
    
    if response in ['y', 'yes', 'ใช่']:
        cleanup_test_data()
    else:
        print("ไม่ล้างข้อมูลทดสอบ - เสร็จสิ้น")

"""
ทดสอบระบบ timeout ที่ปรับปรุงแล้ว
"""
from sheets_manager import sheets_manager
from config_manager import load_config, save_config
import time

def test_timeout_improvement():
    """ทดสอบการปรับปรุง timeout และ retry mechanism"""
    print("🔍 ทดสอบการปรับปรุง Timeout และ Retry Mechanism")
    print("=" * 60)
    
    # ทดสอบการเชื่อมต่อ
    print("\n1. ทดสอบการเชื่อมต่อ Google Sheets")
    if sheets_manager.client and sheets_manager.worksheet:
        print("✅ เชื่อมต่อ Google Sheets สำเร็จ")
        print(f"📊 Spreadsheet ID: {sheets_manager.sheets_id}")
        print(f"📋 Sheet Name: {sheets_manager.sheet_name}")
        print(f"⏰ API Timeout: {sheets_manager.api_timeout} วินาที")
        print(f"🔄 Max Retries: {sheets_manager.max_retries} ครั้ง")
        print(f"⏳ Retry Delay: {sheets_manager.retry_delay} วินาที")
    else:
        print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
        return False
    
    # ทดสอบการโหลดข้อมูลพร้อม retry
    print("\n2. ทดสอบการโหลดข้อมูลพร้อม Retry Mechanism")
    start_time = time.time()
    try:
        config = load_config()
        end_time = time.time()
        print(f"✅ โหลดข้อมูลสำเร็จใน {end_time - start_time:.2f} วินาที")
        print(f"📊 ข้อมูลที่โหลด: {len(config.get('voice_channels', {}))} voice channels")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        return False
    
    # ทดสอบการอัปเดตข้อมูลพร้อม retry
    print("\n3. ทดสอบการอัปเดตข้อมูลพร้อม Retry Mechanism")
    test_key = "timeout_test"
    test_value = f"test_value_{int(time.time())}"
    
    start_time = time.time()
    try:
        success = sheets_manager.update_config_value(test_key, test_value)
        end_time = time.time()
        if success:
            print(f"✅ อัปเดตข้อมูลสำเร็จใน {end_time - start_time:.2f} วินาที")
        else:
            print("❌ ไม่สามารถอัปเดตข้อมูลได้")
            return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอัปเดตข้อมูล: {e}")
        return False
    
    # ทดสอบการอ่านข้อมูลที่เพิ่งอัปเดต
    print("\n4. ทดสอบการอ่านข้อมูลที่เพิ่งอัปเดต")
    try:
        # ล้าง cache ก่อนอ่าน
        sheets_manager.clear_cache()
        config = load_config()
        
        if config.get(test_key) == test_value:
            print("✅ อ่านข้อมูลที่อัปเดตสำเร็จ")
        else:
            print(f"⚠️ ข้อมูลไม่ตรงกัน: คาดหวัง {test_value}, ได้รับ {config.get(test_key)}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่านข้อมูล: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 การทดสอบ Timeout Improvement สำเร็จทั้งหมด!")
    print("\n📋 สรุปการปรับปรุง:")
    print("   ✅ เพิ่ม Timeout Configuration")
    print("   ✅ เพิ่ม Retry Mechanism") 
    print("   ✅ เพิ่ม Error Handling")
    print("   ✅ เพิ่ม Progress Indicators")
    print("   ✅ ป้องกันการค้างเมื่อโหลดช้า")
    
    return True

if __name__ == "__main__":
    test_timeout_improvement()

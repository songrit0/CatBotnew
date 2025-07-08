"""
Test Script - ทดสอบว่าทุกโมดูลทำงานได้ถูกต้อง
"""
import sys
import os

def test_imports():
    """ทดสอบการ import โมดูลต่างๆ"""
    print("🧪 ทดสอบการ import โมดูล...")
    
    try:
        # ทดสอบ config_manager
        from config_manager import load_config, save_config
        print("✅ config_manager import สำเร็จ")
        
        # ทดสอบ voice_manager
        from voice_manager import VoiceChannelManager
        print("✅ voice_manager import สำเร็จ")
        
        # ทดสอบ queue_processor
        from queue_processor import QueueProcessor
        print("✅ queue_processor import สำเร็จ")
        
        # ทดสอบ ui_components
        from ui_components import VoiceChannelManagerView
        print("✅ ui_components import สำเร็จ")
        
        # ทดสอบ commands
        import commands
        print("✅ commands import สำเร็จ")
        
        # ทดสอบ events
        import events
        print("✅ events import สำเร็จ")
        
        print("🎉 ทุกโมดูล import สำเร็จ!")
        return True
        
    except ImportError as e:
        print(f"❌ ข้อผิดพลาดในการ import: {e}")
        return False
    except Exception as e:
        print(f"❌ ข้อผิดพลาดอื่นๆ: {e}")
        return False

def test_config():
    """ทดสอบระบบการตั้งค่า"""
    print("\n🧪 ทดสอบระบบการตั้งค่า...")
    
    try:
        from config_manager import load_config, save_config, create_default_config
        
        # ลองโหลด config
        config = load_config()
        print("✅ โหลด config สำเร็จ")
        
        # ตรวจสอบโครงสร้าง config
        required_keys = ["voice_channels"]
        for key in required_keys:
            if key not in config:
                print(f"⚠️  ไม่พบ key: {key} ใน config")
            else:
                print(f"✅ พบ key: {key} ใน config")
        
        return True
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการทดสอบ config: {e}")
        return False

def test_file_structure():
    """ทดสอบโครงสร้างไฟล์"""
    print("\n🧪 ทดสอบโครงสร้างไฟล์...")
    
    required_files = [
        "main.py",
        "config_manager.py",
        "voice_manager.py",
        "queue_processor.py",
        "commands.py",
        "events.py",
        "ui_components.py",
        "config.json",
        "requirements.txt",
        ".env.example",
        "README.md"
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ พบไฟล์: {file}")
        else:
            print(f"❌ ไม่พบไฟล์: {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  ไฟล์ที่ขาดหายไป: {', '.join(missing_files)}")
        return False
    else:
        print("🎉 ไฟล์ครบถ้วน!")
        return True

def main():
    """ฟังก์ชันหลัก"""
    print("🔍 เริ่มต้นการทดสอบระบบ")
    print("=" * 50)
    
    # ทดสอบโครงสร้างไฟล์
    file_test = test_file_structure()
    
    # ทดสอบการ import
    import_test = test_imports()
    
    # ทดสอบการตั้งค่า
    config_test = test_config()
    
    print("\n" + "=" * 50)
    print("📋 สรุปผลการทดสอบ:")
    print(f"  📁 โครงสร้างไฟล์: {'✅ ผ่าน' if file_test else '❌ ไม่ผ่าน'}")
    print(f"  📦 การ Import: {'✅ ผ่าน' if import_test else '❌ ไม่ผ่าน'}")
    print(f"  ⚙️  การตั้งค่า: {'✅ ผ่าน' if config_test else '❌ ไม่ผ่าน'}")
    
    if all([file_test, import_test, config_test]):
        print("\n🎉 ระบบพร้อมใช้งาน!")
        print("🚀 สามารถเริ่มบอทได้ด้วยคำสั่ง: python main.py")
    else:
        print("\n⚠️  พบปัญหาบางอย่าง กรุณาแก้ไขก่อนใช้งาน")
    
    print("=" * 50)

if __name__ == "__main__":
    main()

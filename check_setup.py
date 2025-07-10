"""
ตรวจสอบการตั้งค่าและวินิจฉัยปัญหา
"""
import os
from dotenv import load_dotenv

def check_discord_token():
    """ตรวจสอบ Discord Token"""
    print("🔍 ตรวจสอบ Discord Token")
    print("=" * 40)
    
    # โหลด environment variables
    load_dotenv()
    
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ ไม่พบ DISCORD_TOKEN ในไฟล์ .env")
        return False
    
    if token == "":
        print("⚠️ DISCORD_TOKEN ว่างเปล่า")
        print("📋 กรุณาใส่ Discord Bot Token ที่ถูกต้องในไฟล์ .env")
        print("📖 ดูคำแนะนำในไฟล์ DISCORD_TOKEN_GUIDE.md")
        return False
    
    # ตรวจสอบรูปแบบ Token
    if token.startswith('http'):
        print("❌ DISCORD_TOKEN เป็น URL ไม่ใช่ Token ที่ถูกต้อง")
        print(f"   ปัจจุบัน: {token[:50]}...")
        print("📋 Token ที่ถูกต้องจะเป็น: MTxxxxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxxxx")
        return False
    
    if len(token) < 50:
        print("❌ DISCORD_TOKEN สั้นเกินไป")
        print(f"   ปัจจุบันมี {len(token)} ตัวอักษร (ควรมี 70+ ตัวอักษร)")
        return False
    
    if not ('.' in token):
        print("❌ DISCORD_TOKEN ไม่มีรูปแบบที่ถูกต้อง (ควรมีจุด . คั่น)")
        return False
    
    print("✅ DISCORD_TOKEN มีรูปแบบที่ถูกต้อง")
    print(f"   เริ่มต้น: {token[:10]}...")
    print(f"   ความยาว: {len(token)} ตัวอักษร")
    return True

def check_google_sheets():
    """ตรวจสอบการตั้งค่า Google Sheets"""
    print("\n🔍 ตรวจสอบ Google Sheets")
    print("=" * 40)
    
    # โหลด environment variables
    load_dotenv()
    
    sheets_id = os.getenv('GOOGLE_SHEETS_ID')
    sheet_name = os.getenv('GOOGLE_SHEET_NAME')
    
    if not sheets_id:
        print("❌ ไม่พบ GOOGLE_SHEETS_ID ในไฟล์ .env")
        return False
    
    if not sheet_name:
        print("❌ ไม่พบ GOOGLE_SHEET_NAME ในไฟล์ .env")
        return False
    
    print(f"✅ GOOGLE_SHEETS_ID: {sheets_id}")
    print(f"✅ GOOGLE_SHEET_NAME: {sheet_name}")
    
    # ตรวจสอบไฟล์ credentials
    if not os.path.exists('credentials.json'):
        print("❌ ไม่พบไฟล์ credentials.json")
        return False
    
    print("✅ พบไฟล์ credentials.json")
    
    # ทดสอบการเชื่อมต่อ
    try:
        from sheets_manager import sheets_manager
        if sheets_manager.client and sheets_manager.worksheet:
            print("✅ เชื่อมต่อ Google Sheets สำเร็จ")
            return True
        else:
            print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
            return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {e}")
        return False

def check_files():
    """ตรวจสอบไฟล์ที่จำเป็น"""
    print("\n🔍 ตรวจสอบไฟล์ที่จำเป็น")
    print("=" * 40)
    
    required_files = [
        '.env',
        'credentials.json',
        'main.py',
        'config_manager.py',
        'sheets_manager.py',
        'voice_manager.py',
        'commands.py',
        'events.py',
        'music_commands.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ ไฟล์ที่ขาดหาย: {', '.join(missing_files)}")
        return False
    
    print("\n✅ ไฟล์ที่จำเป็นครบถ้วน")
    return True

def main():
    """เรียกใช้การตรวจสอบทั้งหมด"""
    print("🤖 Cat Bot - ตรวจสอบการตั้งค่า")
    print("=" * 50)
    
    results = {
        'discord_token': check_discord_token(),
        'google_sheets': check_google_sheets(),
        'files': check_files()
    }
    
    print("\n" + "=" * 50)
    print("📊 สรุปผลการตรวจสอบ")
    print("=" * 50)
    
    all_passed = True
    
    for check_name, result in results.items():
        status = "✅ ผ่าน" if result else "❌ ไม่ผ่าน"
        check_display = {
            'discord_token': 'Discord Token',
            'google_sheets': 'Google Sheets',
            'files': 'ไฟล์ที่จำเป็น'
        }
        print(f"{check_display[check_name]}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 การตรวจสอบทั้งหมดผ่าน! พร้อมเริ่มบอท")
        print("🚀 รันคำสั่ง: python main.py")
    else:
        print("⚠️ พบปัญหาในการตั้งค่า")
        print("\n📋 แนวทางแก้ไข:")
        
        if not results['discord_token']:
            print("1. แก้ไข DISCORD_TOKEN ในไฟล์ .env")
            print("   📖 อ่านคำแนะนำใน DISCORD_TOKEN_GUIDE.md")
        
        if not results['google_sheets']:
            print("2. ตรวจสอบการตั้งค่า Google Sheets")
            print("   📖 อ่านคำแนะนำใน SHEETS_GUIDE.md")
        
        if not results['files']:
            print("3. ตรวจสอบไฟล์ที่ขาดหาย")

if __name__ == "__main__":
    main()

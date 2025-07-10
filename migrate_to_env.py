"""
Migration script: Move credentials from credentials.json to .env
สคริปต์สำหรับย้าย credentials จากไฟล์ JSON ไปยัง .env
"""
import json
import os
from pathlib import Path

def migrate_credentials_to_env():
    """ย้าย credentials จาก credentials.json ไป .env"""
    
    # ตรวจสอบว่ามีไฟล์ credentials.json หรือไม่
    if not os.path.exists('credentials.json'):
        print("❌ ไม่พบไฟล์ credentials.json")
        return False
    
    try:
        # อ่านข้อมูลจาก credentials.json
        with open('credentials.json', 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        # อ่านไฟล์ .env ที่มีอยู่
        env_content = ""
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                env_content = f.read()
        
        # เพิ่มข้อมูล Google Service Account
        # แก้ไข private key เพื่อให้สามารถเก็บใน .env ได้
        private_key_escaped = credentials.get('private_key', '').replace('\n', '\\n')
        
        google_credentials = f"""
# Google Service Account Credentials
GOOGLE_SERVICE_ACCOUNT_TYPE="{credentials.get('type', '')}"
GOOGLE_PROJECT_ID="{credentials.get('project_id', '')}"
GOOGLE_PRIVATE_KEY_ID="{credentials.get('private_key_id', '')}"
GOOGLE_PRIVATE_KEY="{private_key_escaped}"
GOOGLE_CLIENT_EMAIL="{credentials.get('client_email', '')}"
GOOGLE_CLIENT_ID="{credentials.get('client_id', '')}"
GOOGLE_AUTH_URI="{credentials.get('auth_uri', '')}"
GOOGLE_TOKEN_URI="{credentials.get('token_uri', '')}"
GOOGLE_AUTH_PROVIDER_X509_CERT_URL="{credentials.get('auth_provider_x509_cert_url', '')}"
GOOGLE_CLIENT_X509_CERT_URL="{credentials.get('client_x509_cert_url', '')}"
GOOGLE_UNIVERSE_DOMAIN="{credentials.get('universe_domain', '')}"
"""
        
        # ตรวจสอบว่ามีข้อมูล Google ใน .env แล้วหรือไม่
        if 'GOOGLE_SERVICE_ACCOUNT_TYPE' not in env_content:
            env_content += google_credentials
            
            # เขียนข้อมูลกลับไป .env
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            print("✅ ย้าย credentials จาก credentials.json ไป .env สำเร็จ")
        else:
            print("ℹ️ ข้อมูล Google Service Account มีอยู่ใน .env แล้ว")
        
        # สำรองไฟล์ credentials.json
        backup_name = 'credentials.json.backup'
        if not os.path.exists(backup_name):
            import shutil
            shutil.copy2('credentials.json', backup_name)
            print(f"✅ สำรอง credentials.json เป็น {backup_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการย้าย credentials: {e}")
        return False

def remove_credentials_json():
    """ลบไฟล์ credentials.json หลังจากย้ายแล้ว"""
    try:
        if os.path.exists('credentials.json'):
            # ตรวจสอบว่ามีไฟล์สำรองแล้ว
            if os.path.exists('credentials.json.backup'):
                os.remove('credentials.json')
                print("✅ ลบไฟล์ credentials.json แล้ว (มีไฟล์สำรองอยู่)")
                return True
            else:
                print("⚠️ ไม่ลบไฟล์ credentials.json เพราะยังไม่มีไฟล์สำรอง")
                return False
        else:
            print("ℹ️ ไม่พบไฟล์ credentials.json")
            return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการลบไฟล์: {e}")
        return False

if __name__ == "__main__":
    print("🔄 เริ่มต้นการย้าย credentials จาก JSON ไป .env")
    print("=" * 50)
    
    if migrate_credentials_to_env():
        response = input("\n🗑️ ต้องการลบไฟล์ credentials.json หรือไม่? (y/N): ")
        if response.lower() in ['y', 'yes']:
            remove_credentials_json()
        else:
            print("ℹ️ เก็บไฟล์ credentials.json ไว้")
    
    print("\n✅ การย้ายข้อมูลเสร็จสิ้น")
    print("💡 อย่าลืมเพิ่ม credentials.json ใน .gitignore เพื่อความปลอดภัย")

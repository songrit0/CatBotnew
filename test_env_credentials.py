"""
Test script สำหรับทดสอบการอ่าน credentials จาก .env
"""
import os
import json
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# โหลด environment variables
load_dotenv()

def test_credentials():
    print("🔧 ทดสอบการอ่าน Google Credentials จาก .env")
    print("=" * 50)
    
    # อ่านข้อมูลจาก .env
    private_key = os.getenv('GOOGLE_PRIVATE_KEY', '')
    print(f"Private key length from env: {len(private_key)}")
    print(f"Private key starts with: {private_key[:50]}...")
    
    # แก้ไข newline
    if '\\n' in private_key:
        private_key = private_key.replace('\\n', '\n')
        print(f"After replacing \\n: {len(private_key)} chars")
    
    # สร้าง credentials object
    credentials_data = {
        "type": os.getenv('GOOGLE_SERVICE_ACCOUNT_TYPE'),
        "project_id": os.getenv('GOOGLE_PROJECT_ID'),
        "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
        "private_key": private_key,
        "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
        "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
        "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
        "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN')
    }
    
    print(f"Project ID: {credentials_data['project_id']}")
    print(f"Client Email: {credentials_data['client_email']}")
    
    # ทดสอบสร้าง credentials
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(
            credentials_data, 
            scopes=scope
        )
        print("✅ สร้าง credentials สำเร็จ!")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def compare_with_original():
    print("\n🔍 เปรียบเทียบกับไฟล์ credentials.json เดิม")
    print("=" * 50)
    
    try:
        # อ่านจาก credentials.json
        with open('credentials.json', 'r') as f:
            original_creds = json.load(f)
        
        # อ่านจาก .env
        env_private_key = os.getenv('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n')
        
        print(f"Original private key length: {len(original_creds['private_key'])}")
        print(f"Env private key length: {len(env_private_key)}")
        print(f"Keys match: {original_creds['private_key'] == env_private_key}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    if test_credentials():
        print("\n✅ ทดสอบสำเร็จ - สามารถใช้ .env แทน credentials.json ได้")
    else:
        print("\n❌ ทดสอบล้มเหลว - ยังไม่สามารถใช้ .env แทน credentials.json ได้")
    
    compare_with_original()

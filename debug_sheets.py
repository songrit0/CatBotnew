"""
ตรวจสอบข้อมูลใน Google Sheets โดยตรง
"""
from sheets_manager import sheets_manager
import json

def debug_sheets_data():
    """ตรวจสอบข้อมูลใน Google Sheets"""
    print("🔍 ตรวจสอบข้อมูลใน Google Sheets")
    print("=" * 50)
    
    try:
        # อ่านข้อมูลทั้งหมดจาก Google Sheets
        all_records = sheets_manager.worksheet.get_all_records()
        
        print(f"📊 พบข้อมูลทั้งหมด {len(all_records)} แถว")
        print()
        
        for i, record in enumerate(all_records):
            print(f"แถว {i+1}:")
            print(f"  Config Key: '{record.get('Config Key', '')}'")
            print(f"  Config Value: '{record.get('Config Value', '')}'")
            print(f"  Data Type: '{record.get('Data Type', '')}'")
            print(f"  Last Updated: '{record.get('Last Updated', '')}'")
            print(f"  Notes: '{record.get('Notes', '')}'")
            print()
        
        # ทดสอบการแปลงข้อมูล
        print("🔄 ทดสอบการแปลงข้อมูล:")
        config = sheets_manager.get_config_from_sheets()
        print(f"✅ Config ที่ได้: {json.dumps(config, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    debug_sheets_data()

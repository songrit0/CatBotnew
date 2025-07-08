"""
ทดสอบระบบ Music Fallback
"""
import asyncio
from music_fallback import MusicFallback

async def test_fallback():
    """ทดสอบระบบ fallback"""
    print("🔍 ทดสอบระบบ Music Fallback...")
    
    # ทดสอบการค้นหาด้วยชื่อเพลง
    test_queries = [
        "test song",
        "shape of you",
        "เพลงไทย",
        "popular music"
    ]
    
    for query in test_queries:
        print(f"\n🎵 ทดสอบค้นหา: {query}")
        try:
            result = await MusicFallback.search_with_fallback(query)
            if result:
                print(f"✅ พบเพลง: {result.get('title', 'ไม่ทราบชื่อ')}")
                print(f"📹 URL: {result.get('webpage_url', 'ไม่มี URL')}")
            else:
                print("❌ ไม่พบเพลง")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
    
    print("\n✅ การทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    asyncio.run(test_fallback())

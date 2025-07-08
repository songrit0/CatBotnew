"""
ไฟล์ทดสอบระบบเพลง - ตรวจสอบการทำงานของระบบเพลง
"""
import asyncio
import unittest
from unittest.mock import Mock, AsyncMock
import sys
import os

# เพิ่ม path สำหรับ import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from music_manager import MusicManager, Song, MusicQueue, YTDLSource

class TestMusicSystem(unittest.TestCase):
    """คลาสทดสอบระบบเพลง"""
    
    def setUp(self):
        """ตั้งค่าเริ่มต้นสำหรับการทดสอบ"""
        self.bot = Mock()
        self.music_manager = MusicManager(self.bot)
        self.guild_id = 12345
        
    def test_music_queue_basic_operations(self):
        """ทดสอบการทำงานพื้นฐานของคิวเพลง"""
        queue = MusicQueue()
        
        # ทดสอบคิวว่าง
        self.assertEqual(len(queue.queue), 0)
        self.assertIsNone(queue.current_song)
        self.assertIsNone(queue.get_next())
        
        # สร้างเพลงจำลอง
        mock_user = Mock()
        mock_user.mention = "@TestUser"
        song1 = Song("url1", "เพลงทดสอบ 1", "3:30", mock_user)
        song2 = Song("url2", "เพลงทดสอบ 2", "4:15", mock_user)
        
        # ทดสอบเพิ่มเพลง
        queue.add(song1)
        queue.add(song2)
        self.assertEqual(len(queue.queue), 2)
        
        # ทดสอบดึงเพลงถัดไป
        next_song = queue.get_next()
        self.assertEqual(next_song.title, "เพลงทดสอบ 1")
        self.assertEqual(len(queue.queue), 1)
        
        # ทดสอบ current_song
        queue.current_song = next_song
        self.assertEqual(queue.current_song.title, "เพลงทดสอบ 1")
        
    def test_loop_functionality(self):
        """ทดสอบฟังก์ชันลูป"""
        queue = MusicQueue()
        mock_user = Mock()
        mock_user.mention = "@TestUser"
        
        song1 = Song("url1", "เพลงทดสอบ 1", "3:30", mock_user)
        song2 = Song("url2", "เพลงทดสอบ 2", "4:15", mock_user)
        
        queue.add(song1)
        queue.add(song2)
        queue.current_song = song1
        
        # ทดสอบลูปเพลงปัจจุบัน
        queue.loop = True
        next_song = queue.get_next()
        self.assertEqual(next_song.title, "เพลงทดสอบ 1")  # ควรได้เพลงเดิม
        self.assertEqual(len(queue.queue), 2)  # คิวไม่เปลี่ยน
        
        # ทดสอบลูปคิว
        queue.loop = False
        queue.loop_queue = True
        queue.current_song = None  # ล้าง current_song เพื่อให้ดึงจากคิว
        next_song = queue.get_next()
        self.assertEqual(next_song.title, "เพลงทดสอบ 1")  # ควรได้เพลงแรกในคิว
        self.assertEqual(len(queue.queue), 2)  # เพลงถูกเอาออกแล้วใส่กลับ
        
    def test_queue_operations(self):
        """ทดสอบการจัดการคิว"""
        queue = MusicQueue()
        mock_user = Mock()
        mock_user.mention = "@TestUser"
        
        # เพิ่มเพลงหลายเพลง
        for i in range(5):
            song = Song(f"url{i}", f"เพลงทดสอบ {i+1}", "3:30", mock_user)
            queue.add(song)
        
        # ทดสอบลบเพลงจากคิว
        success = queue.remove(2)  # ลบเพลงที่ 3
        self.assertTrue(success)
        self.assertEqual(len(queue.queue), 4)
        
        # ทดสอบลบเพลงที่ไม่มี
        success = queue.remove(10)
        self.assertFalse(success)
        
        # ทดสอบล้างคิว
        queue.clear()
        self.assertEqual(len(queue.queue), 0)
        
    def test_music_manager_initialization(self):
        """ทดสอบการเริ่มต้น MusicManager"""
        self.assertEqual(len(self.music_manager.voice_clients), 0)
        self.assertEqual(len(self.music_manager.music_queues), 0)
        
        # ทดสอบการดึง queue ใหม่
        queue = self.music_manager.get_music_queue(self.guild_id)
        self.assertIsInstance(queue, MusicQueue)
        self.assertEqual(len(self.music_manager.music_queues), 1)
        
    def test_url_detection(self):
        """ทดสอบการตรวจสอบ URL"""
        # URL ที่ถูกต้อง
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtu.be/dQw4w9WgXcQ",
            "https://music.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            self.assertTrue(self.music_manager.is_url(url), f"URL {url} ควรจะถูกต้อง")
        
        # ข้อความที่ไม่ใช่ URL
        invalid_urls = [
            "ดาว พระเจ้า",
            "เพลงไทย",
            "test song name"
        ]
        
        for text in invalid_urls:
            self.assertFalse(self.music_manager.is_url(text), f"ข้อความ {text} ไม่ควรเป็น URL")

def run_async_tests():
    """รันการทดสอบแบบ async"""
    
    async def test_ytdl_source():
        """ทดสอบ YTDLSource (ต้องการการเชื่อมต่ออินเทอร์เน็ต)"""
        try:
            # ทดสอบด้วย URL ที่รู้จัก (อาจใช้เวลานาน)
            # search = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            # source = await YTDLSource.create_source(search, stream=True)
            # print(f"✅ สามารถสร้าง source สำหรับ: {source.title}")
            print("⚠️ ข้ามการทดสอบ YTDLSource เนื่องจากต้องการการเชื่อมต่ออินเทอร์เน็ต")
        except Exception as e:
            print(f"❌ ไม่สามารถสร้าง source ได้: {e}")
    
    # รันการทดสอบ async
    asyncio.run(test_ytdl_source())

if __name__ == "__main__":
    print("🧪 เริ่มทดสอบระบบเพลง...")
    print("=" * 50)
    
    # รัน unit tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    print("🧪 ทดสอบ Async functions...")
    
    # รัน async tests
    run_async_tests()
    
    print("=" * 50)
    print("✅ การทดสอบเสร็จสิ้น")

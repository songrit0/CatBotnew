"""
Music Fallback - ระบบ fallback สำหรับเมื่อ YouTube ไม่ทำงาน
"""
import yt_dlp
import asyncio
import re
from typing import Optional, Dict, Any

class MusicFallback:
    """คลาสสำหรับจัดการ fallback extractors"""
    
    @staticmethod
    def get_fallback_ytdl_options():
        """ตัวเลือก YTDL สำหรับ fallback"""
        return {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'source_address': '0.0.0.0',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '115',
                'Connection': 'keep-alive',
            },
            'age_limit': None,
            'skip_download': False,
            # เพิ่มตัวเลือกสำหรับ bypass
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['dash', 'hls']
                }
            },
            'sleep_interval': 1,
            'max_sleep_interval': 5,
        }
    
    @staticmethod
    async def search_with_fallback(search_term: str, loop=None) -> Optional[Dict[str, Any]]:
        """ค้นหาเพลงด้วย fallback methods"""
        loop = loop or asyncio.get_event_loop()
        
        # Method 1: ใช้ ytsearch แทน direct URL
        try:
            ytdl_opts = MusicFallback.get_fallback_ytdl_options()
            ytdl = yt_dlp.YoutubeDL(ytdl_opts)
            
            # ถ้าเป็น URL ให้แปลงเป็นการค้นหา
            if MusicFallback.is_url(search_term):
                video_id = MusicFallback.extract_video_id(search_term)
                if video_id:
                    search_query = f"ytsearch:{video_id}"
                else:
                    search_query = f"ytsearch:{search_term}"
            else:
                search_query = f"ytsearch:{search_term}"
            
            partial = lambda: ytdl.extract_info(search_query, download=False)
            data = await loop.run_in_executor(None, partial)
            
            if data and 'entries' in data and data['entries']:
                return data['entries'][0]
                
        except Exception as e:
            print(f"Fallback method 1 failed: {e}")
        
        # Method 2: ใช้ alternative search
        try:
            ytdl_opts = MusicFallback.get_fallback_ytdl_options()
            ytdl_opts['default_search'] = 'auto'
            ytdl = yt_dlp.YoutubeDL(ytdl_opts)
            
            partial = lambda: ytdl.extract_info(search_term, download=False)
            data = await loop.run_in_executor(None, partial)
            
            if data:
                if 'entries' in data and data['entries']:
                    return data['entries'][0]
                else:
                    return data
                    
        except Exception as e:
            print(f"Fallback method 2 failed: {e}")
        
        return None
    
    @staticmethod
    def is_url(text: str) -> bool:
        """ตรวจสอบว่าเป็น URL หรือไม่"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(text) is not None
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """ดึง video ID จาก YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def create_safe_search_query(original_query: str) -> str:
        """สร้าง search query ที่ปลอดภัย"""
        # ลบอักขระพิเศษที่อาจทำให้เกิดปัญหา
        safe_query = re.sub(r'[^\w\s-]', '', original_query)
        # จำกัดความยาว
        safe_query = safe_query[:100]
        return safe_query.strip()

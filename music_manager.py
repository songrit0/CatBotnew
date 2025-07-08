"""
Music Manager - ระบบจัดการเพลงจาก YouTube
"""
import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from typing import Optional, Dict, Any, List
import re
from music_fallback import MusicFallback

class Song:
    """คลาสสำหรับจัดเก็บข้อมูลเพลง"""
    
    def __init__(self, url: str, title: str, duration: str, requester: discord.Member):
        self.url = url
        self.title = title
        self.duration = duration
        self.requester = requester
        self.source = None

class MusicQueue:
    """คลาสสำหรับจัดการคิวเพลง"""
    
    def __init__(self):
        self.queue: List[Song] = []
        self.current_song: Optional[Song] = None
        self.loop = False
        self.loop_queue = False
        
    def add(self, song: Song):
        """เพิ่มเพลงในคิว"""
        self.queue.append(song)
        
    def get_next(self) -> Optional[Song]:
        """ดึงเพลงถัดไป"""
        if self.loop and self.current_song:
            return self.current_song
            
        if self.queue:
            song = self.queue.pop(0)
            if self.loop_queue:
                # เพิ่มเพลงกลับไปท้ายคิวสำหรับลูป
                self.queue.append(song)
            return song
        return None
        
    def skip(self) -> Optional[Song]:
        """ข้ามเพลงปัจจุบัน"""
        if self.queue:
            return self.queue.pop(0)
        return None
        
    def clear(self):
        """ล้างคิว"""
        self.queue.clear()
        
    def remove(self, index: int) -> bool:
        """ลบเพลงจากคิว"""
        if 0 <= index < len(self.queue):
            self.queue.pop(index)
            return True
        return False
        
    def shuffle(self):
        """สลับเพลงในคิว"""
        import random
        random.shuffle(self.queue)

class YTDLSource(discord.PCMVolumeTransformer):
    """คลาสสำหรับจัดการแหล่งข้อมูลเพลงจาก YouTube"""
    
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'extractaudio': True,
        'audioformat': 'mp3',
        'audioquality': '192K',
        # เพิ่ม User-Agent เพื่อหลีกเลี่ยงการตรวจจับ bot
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        # เพิ่ม headers เพื่อแก้ปัญหา bot detection
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '115',
            'Connection': 'keep-alive',
        },
        # เพิ่มการจำลอง browser behavior
        'cookiefile': None,
        'age_limit': None,
        'skip_download': False,
    }
    
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
        'executable': r'C:\Users\MARU\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe'
    }
    
    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
    
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')
        
    @classmethod
    async def create_source(cls, search: str, *, loop=None, stream=False):
        """สร้างแหล่งข้อมูลเพลง"""
        loop = loop or asyncio.get_event_loop()
        
        # สร้าง ytdl instance ใหม่พร้อม options ที่ปรับปรุง
        ytdl_opts = cls.YTDL_OPTIONS.copy()
        ytdl_opts['quiet'] = True
        ytdl_opts['no_warnings'] = True
        
        ytdl = yt_dlp.YoutubeDL(ytdl_opts)
        
        try:
            partial = lambda: ytdl.extract_info(search, download=not stream)
            data = await loop.run_in_executor(None, partial)
            
            if data is None:
                raise Exception(f'ไม่สามารถหาข้อมูลสำหรับ: {search}')
                
            if 'entries' in data:
                # ถ้าเป็น playlist ให้เอาเพลงแรก
                data = data['entries'][0]
                
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            
            return cls(discord.FFmpegPCMAudio(filename, **cls.FFMPEG_OPTIONS), data=data)
            
        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            if "Sign in to confirm you're not a bot" in error_msg:
                raise Exception("❌ YouTube ขอให้ยืนยันตัวตน กรุณาลองอีกครั้งในภายหลัง หรือใช้ลิงก์เพลงจากแหล่งอื่น")
            elif "Video unavailable" in error_msg:
                raise Exception("❌ วิดีโอนี้ไม่สามารถเข้าถึงได้ กรุณาลองเพลงอื่น")
            else:
                raise Exception(f"❌ ไม่สามารถโหลดเพลงได้: {error_msg}")
        except Exception as e:
            raise Exception(f"❌ เกิดข้อผิดพลาดในการประมวลผลเพลง: {str(e)}")

class MusicManager:
    """คลาสหลักสำหรับจัดการระบบเพลง"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients: Dict[int, discord.VoiceClient] = {}
        self.music_queues: Dict[int, MusicQueue] = {}
        
    def get_voice_client(self, guild_id: int) -> Optional[discord.VoiceClient]:
        """ดึง voice client สำหรับ guild"""
        return self.voice_clients.get(guild_id)
        
    def get_music_queue(self, guild_id: int) -> MusicQueue:
        """ดึง music queue สำหรับ guild"""
        if guild_id not in self.music_queues:
            self.music_queues[guild_id] = MusicQueue()
        return self.music_queues[guild_id]
        
    async def join_voice_channel(self, channel: discord.VoiceChannel) -> discord.VoiceClient:
        """เข้าร่วมห้องเสียง"""
        guild_id = channel.guild.id
        
        # ตรวจสอบว่าบอทอยู่ในห้องเสียงอื่นหรือไม่
        if guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            if voice_client.channel != channel:
                await voice_client.move_to(channel)
            return voice_client
        
        # เข้าร่วมห้องเสียงใหม่
        voice_client = await channel.connect()
        self.voice_clients[guild_id] = voice_client
        return voice_client
        
    async def leave_voice_channel(self, guild_id: int):
        """ออกจากห้องเสียง"""
        if guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            await voice_client.disconnect()
            del self.voice_clients[guild_id]
            
        # ล้างคิวเพลง
        if guild_id in self.music_queues:
            self.music_queues[guild_id].clear()
            
    async def play_next(self, guild_id: int):
        """เล่นเพลงถัดไป"""
        queue = self.get_music_queue(guild_id)
        voice_client = self.get_voice_client(guild_id)
        
        if not voice_client:
            return
            
        next_song = queue.get_next()
        if next_song:
            try:
                source = await YTDLSource.create_source(next_song.url, stream=True)
                next_song.source = source
                queue.current_song = next_song
                
                def after_playing(error):
                    if error:
                        print(f'เกิดข้อผิดพลาดในการเล่นเพลง: {error}')
                    asyncio.run_coroutine_threadsafe(self.play_next(guild_id), self.bot.loop)
                
                voice_client.play(source, after=after_playing)
                
            except Exception as e:
                print(f'ไม่สามารถเล่นเพลงได้: {e}')
                await self.play_next(guild_id)
        else:
            queue.current_song = None
            
    async def add_to_queue(self, guild_id: int, search: str, requester: discord.Member) -> Song:
        """เพิ่มเพลงในคิว"""
        try:
            # ลองใช้ระบบปกติก่อน
            data = await self._extract_info_with_fallback(search)
            
            if not data:
                raise Exception('ไม่สามารถหาข้อมูลเพลงได้')
                
            # สร้าง Song object
            duration = self._format_duration(data.get('duration', 0))
            song = Song(
                url=data.get('webpage_url', data.get('url', search)),
                title=data.get('title', 'ไม่ทราบชื่อ'),
                duration=duration,
                requester=requester
            )
            
            # เพิ่มเพลงในคิว
            queue = self.get_music_queue(guild_id)
            queue.add(song)
            
            return song
            
        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            if "Sign in to confirm you're not a bot" in error_msg:
                raise Exception("❌ YouTube ขอให้ยืนยันตัวตน กรุณาลองค้นหาด้วยชื่อเพลงแทนการใช้ลิงก์")
            elif "Video unavailable" in error_msg:
                raise Exception("❌ วิดีโอนี้ไม่สามารถเข้าถึงได้ กรุณาลองเพลงอื่น")
            elif "Private video" in error_msg:
                raise Exception("❌ วิดีโอนี้เป็นแบบส่วนตัว ไม่สามารถเล่นได้")
            else:
                raise Exception(f"❌ ไม่สามารถโหลดเพลงได้: กรุณาลองใหม่อีกครั้ง")
        except Exception as e:
            raise Exception(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    
    async def _extract_info_with_fallback(self, search: str) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลเพลงพร้อม fallback"""
        # ลองใช้ระบบปกติก่อน
        try:
            ytdl_opts = YTDLSource.YTDL_OPTIONS.copy()
            ytdl_opts['quiet'] = True
            ytdl_opts['no_warnings'] = True
            
            ytdl = yt_dlp.YoutubeDL(ytdl_opts)
            
            loop = asyncio.get_event_loop()
            partial = lambda: ytdl.extract_info(search, download=False)
            data = await loop.run_in_executor(None, partial)
            
            if data:
                if 'entries' in data:
                    return data['entries'][0] if data['entries'] else None
                return data
                
        except Exception as e:
            print(f"Primary extraction failed: {e}")
            
        # ใช้ fallback system
        print("Using fallback extraction method...")
        try:
            return await MusicFallback.search_with_fallback(search)
        except Exception as e:
            print(f"Fallback extraction failed: {e}")
            return None
            
        except Exception as e:
            raise Exception(f'ไม่สามารถเพิ่มเพลงได้: {e}')
            
    def _format_duration(self, seconds: int) -> str:
        """แปลงวินาทีเป็นรูปแบบ mm:ss"""
        if not seconds:
            return "ไม่ทราบ"
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    async def skip_song(self, guild_id: int) -> bool:
        """ข้ามเพลงปัจจุบัน"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            return True
        return False
        
    async def pause_song(self, guild_id: int) -> bool:
        """หยุดเพลงชั่วคราว"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            return True
        return False
        
    async def resume_song(self, guild_id: int) -> bool:
        """เล่นเพลงต่อ"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            return True
        return False
        
    async def stop_music(self, guild_id: int):
        """หยุดเพลงและล้างคิว"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client:
            if voice_client.is_playing() or voice_client.is_paused():
                voice_client.stop()
                
        queue = self.get_music_queue(guild_id)
        queue.clear()
        queue.current_song = None
        
    def set_volume(self, guild_id: int, volume: float) -> bool:
        """ตั้งค่าระดับเสียง"""
        voice_client = self.get_voice_client(guild_id)
        if voice_client and hasattr(voice_client.source, 'volume'):
            voice_client.source.volume = volume / 100
            return True
        return False
        
    def is_url(self, text: str) -> bool:
        """ตรวจสอบว่าเป็น URL หรือไม่"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(text) is not None

"""
CatBot - Discord Voice Channel Management Bot
ไฟล์หลักสำหรับเริ่มต้นบอท
"""
import discord
from discord.ext import commands
import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv

# Import modules
from config_manager import load_config
from voice_manager import VoiceChannelManager
from queue_processor import QueueProcessor
from commands import setup as setup_commands
from events import setup as setup_events
from music_commands import setup as setup_music_commands

class CatBot(commands.Bot):
    """คลาสหลักของบอท"""
    
    def __init__(self):
        # ตั้งค่า intents
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.guilds = True
        intents.message_content = True
        
        # สร้าง bot instance
        super().__init__(
            command_prefix='!', 
            intents=intents, 
            help_command=None  # ปิดใช้งาน help command เดิม
        )
        
        # สร้าง managers
        self.voice_manager = VoiceChannelManager(self)
        self.queue_processor = QueueProcessor(self, self.voice_manager)
    
    async def setup_hook(self):
        """ตั้งค่าเริ่มต้นเมื่อบอทเริ่มทำงาน"""
        print("🔧 กำลังตั้งค่าระบบ...")
        
        # โหลด Cogs
        await setup_commands(self, self.voice_manager)
        await setup_events(self, self.voice_manager, self.queue_processor)
        await setup_music_commands(self)  # เพิ่มระบบเพลง
        
        print("✅ ตั้งค่าระบบเสร็จสิ้น")

async def create_web_server():
    """สร้าง web server สำหรับ Render deployment"""
    async def health_check(request):
        return web.Response(text="Bot is running!")
    
    async def status(request):
        return web.json_response({
            "status": "online",
            "bot": "CatBot",
            "version": "1.0.0"
        })
    
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', status)
    
    port = int(os.environ.get('PORT', 8000))
    return app, port

async def main():
    """ฟังก์ชันหลักสำหรับเริ่มต้นบอท"""
    # โหลดตัวแปรจาก .env
    load_dotenv()
    
    # ตรวจสอบ token
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ ไม่พบ DISCORD_TOKEN ในไฟล์ .env")
        print("กรุณาสร้างไฟล์ .env และเพิ่ม DISCORD_TOKEN=your_bot_token")
        return
    
    # สร้าง bot instance
    bot = CatBot()
    
    # สร้าง web server สำหรับ Render
    app, port = await create_web_server()
    
    print("🚀 กำลังเริ่มต้นบอทและ web server...")
    print(f"🌐 Web server จะทำงานที่ port {port}")
    
    try:
        # เริ่ม web server และ bot พร้อมกัน
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        
        # เริ่ม web server
        await site.start()
        print(f"✅ Web server เริ่มทำงานแล้วที่ port {port}")
        
        # เริ่มต้นบอท
        async with bot:
            await bot.start(token)
    except KeyboardInterrupt:
        print("\n⏹️ ปิดบอทโดยผู้ใช้")
    except Exception as e:
        print(f"❌ ไม่สามารถเริ่มต้นบอทได้: {e}")
    finally:
        print("👋 บอทปิดแล้ว")

if __name__ == "__main__":
    # เรียกใช้งานบอท
    asyncio.run(main())

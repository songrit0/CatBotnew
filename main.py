"""
CatBot - Discord Voice Channel Management Bot
ไฟล์หลักสำหรับเริ่มต้นบอท
"""
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Import modules
from config_manager import load_config
from voice_manager import VoiceChannelManager
from queue_processor import QueueProcessor
from commands import setup as setup_commands
from events import setup as setup_events

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
        
        print("✅ ตั้งค่าระบบเสร็จสิ้น")

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
    
    print("🚀 กำลังเริ่มต้นบอท...")
    
    try:
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

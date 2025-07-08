"""
Bot Events - จัดการ Event ต่างๆ ของบอท
"""
import discord
from discord.ext import commands
from config_manager import load_config

class BotEvents(commands.Cog):
    """Cog สำหรับจัดการ Event ต่างๆ"""
    
    def __init__(self, bot, voice_manager, queue_processor):
        self.bot = bot
        self.voice_manager = voice_manager
        self.queue_processor = queue_processor
    
    @commands.Cog.listener()
    async def on_ready(self):
        """เมื่อบอทพร้อมใช้งาน"""
        print(f'{self.bot.user} ได้เชื่อมต่อแล้ว!')
        print(f'Bot ID: {self.bot.user.id}')
        
        config = load_config()
        print(f'กำลังติดตาม {len(config["voice_channels"])} ห้องเสียง')
        
        # เริ่มต้นระบบประมวลผลคิว
        await self.queue_processor.start()
        
        # ตรวจสอบห้องเสียงทั้งหมด
        await self._check_all_voice_channels(config)
        
        print("🤖 บอทพร้อมใช้งาน!")
    
    async def _check_all_voice_channels(self, config):
        """ตรวจสอบห้องเสียงทั้งหมดเมื่อเริ่มต้น"""
        for channel_id, settings in config["voice_channels"].items():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                human_count = sum(1 for member in channel.members if not member.bot)
                print(f"🔊 ห้อง: {channel.name} (ID: {channel_id})")
                print(f"   คนในห้อง: {human_count} คน")
                print(f"   ชื่อเมื่อว่าง: {settings['empty_name']}")
                print(f"   ชื่อเมื่อมีคน: {settings['occupied_name']}")
                print(f"   ไม่อัพเดตชื่อห้องเริ่มต้นเพื่อหลีกเลี่ยง Rate Limiting")
            else:
                print(f"❌ ไม่พบห้อง ID: {channel_id}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """เมื่อมีการเปลี่ยนแปลงสถานะในห้องเสียง"""
        print(f"🔄 Voice State Update: {member.display_name}")
        
        # แสดงข้อมูลการเปลี่ยนแปลง
        if before.channel != after.channel:
            if before.channel:
                print(f"   ออกจากห้อง: {before.channel.name}")
            if after.channel:
                print(f"   เข้าห้อง: {after.channel.name}")
        
        channels_to_check = set()
        
        # เพิ่มห้องที่ผู้ใช้เข้าไป
        if after.channel:
            channels_to_check.add(after.channel)
        
        # เพิ่มห้องที่ผู้ใช้ออกจาก
        if before.channel:
            channels_to_check.add(before.channel)
        
        # ตรวจสอบและอัพเดตห้องเสียงที่เกี่ยวข้อง
        await self._check_channels(channels_to_check, member.guild)
    
    async def _check_channels(self, channels_to_check, guild):
        """ตรวจสอบและอัพเดตห้องเสียงที่เกี่ยวข้อง"""
        for channel in channels_to_check:
            current_config = load_config()  # โหลด config ใหม่
            channel_id = str(channel.id)
            if channel_id in current_config["voice_channels"]:
                print(f"🔧 กำลังตรวจสอบห้อง: {channel.name}")
                await self.voice_manager.update_voice_channel_name(channel, guild)
            else:
                print(f"ℹ️ ห้อง {channel.name} ไม่ได้อยู่ในการตั้งค่า")

async def setup(bot, voice_manager, queue_processor):
    """ตั้งค่า Cog"""
    await bot.add_cog(BotEvents(bot, voice_manager, queue_processor))

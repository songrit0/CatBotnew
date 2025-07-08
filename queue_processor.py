"""
Queue Processor - จัดการการประมวลผลคิวการอัพเดต
"""
import asyncio
import discord
from datetime import datetime
from config_manager import load_config

class QueueProcessor:
    def __init__(self, bot, voice_manager):
        self.bot = bot
        self.voice_manager = voice_manager
        self.is_running = False
    
    async def start(self):
        """เริ่มต้นระบบประมวลผลคิว"""
        if self.is_running:
            return
        
        self.is_running = True
        self.bot.loop.create_task(self._process_queue())
        print("⏰ เริ่มต้นระบบจัดการคิวการอัพเดต")
    
    async def _process_queue(self):
        """ประมวลผลคิวการอัพเดตห้องเสียง"""
        while self.is_running:
            try:
                now = datetime.now()
                queue = self.voice_manager.get_queue_info()
                to_remove = []
                
                for channel_key, update_info in queue.items():
                    if now >= update_info['scheduled_time']:
                        await self._process_queue_item(channel_key, update_info, now)
                        to_remove.append(channel_key)
                
                # ลบรายการที่ประมวลผลแล้ว
                for key in to_remove:
                    self.voice_manager.clear_queue_item(key)
                
                await asyncio.sleep(30)  # ตรวจสอบทุก 30 วินาที
                
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการประมวลผลคิว: {e}")
                await asyncio.sleep(30)
    
    async def _process_queue_item(self, channel_key, update_info, now):
        """ประมวลผลรายการคิวแต่ละรายการ"""
        channel = update_info['channel']
        guild = update_info.get('guild')
        
        print(f"⏰ ถึงเวลาอัพเดตห้อง {channel.name}")
        
        # ตรวจสอบสถานะห้องใหม่
        human_count = sum(1 for member in channel.members if not member.bot)
        
        # โหลด config ใหม่เพื่อรับการอัพเดต
        current_config = load_config()
        
        # อัพเดตชื่อที่ถูกต้องตามสถานะปัจจุบัน
        if human_count > 0:
            correct_name = current_config["voice_channels"][str(channel.id)]["occupied_name"]
        else:
            correct_name = current_config["voice_channels"][str(channel.id)]["empty_name"]
        
        if channel.name != correct_name:
            try:
                await channel.edit(name=correct_name)
                self.voice_manager.force_update_time(channel_key)
                print(f"✅ อัพเดตจากคิว: {correct_name}")
                
                # ส่งข้อความแจ้งเตือนว่าเปลี่ยนชื่อสำเร็จจากคิว
                await self._send_queue_success_notification(guild, channel, human_count)
                        
            except Exception as e:
                print(f"❌ อัพเดตจากคิวล้มเหลว: {e}")
    
    async def _send_queue_success_notification(self, guild, channel, human_count):
        """ส่งข้อความแจ้งเตือนเมื่ออัพเดตจากคิวสำเร็จ"""
        if not guild:
            return
            
        try:
            text_channel = await self._get_notification_channel(guild)
            if not text_channel:
                return
                
            embed = {
                "title": "✅ เปลี่ยนชื่อห้องเสียงสำเร็จ (จากคิว)",
                "description": f"ห้องเสียงถูกเปลี่ยนชื่อจากคิวเรียบร้อยแล้ว",
                "color": 0x00ff00,  # เขียว
                "fields": [
                    {"name": "🔊 ห้องเสียง", "value": f"{channel.name}", "inline": True},
                    {"name": "👥 จำนวนคน", "value": f"{human_count} คน", "inline": True}
                ]
            }
            
            await text_channel.send(embed=discord.Embed.from_dict(embed))
            print(f"📢 ส่งข้อความแจ้งเตือนการเปลี่ยนชื่อสำเร็จจากคิว")
            
        except Exception as e:
            print(f"❌ ไม่สามารถส่งข้อความแจ้งเตือนได้: {e}")
    
    async def _get_notification_channel(self, guild):
        """หาห้องแชทสำหรับส่งการแจ้งเตือน"""
        current_config = load_config()
        
        # ใช้ห้องแชทที่ระบุใน config หรือห้องแรกที่บอทเข้าถึงได้
        if "notification_channel" in current_config:
            text_channel = self.bot.get_channel(int(current_config["notification_channel"]))
            if text_channel and text_channel.permissions_for(guild.me).send_messages:
                return text_channel
        
        # ถ้าไม่มีห้องที่ระบุหรือไม่มีสิทธิ์ ให้หาห้องแรกที่เข้าถึงได้
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                return ch
        
        return None
    
    def stop(self):
        """หยุดระบบประมวลผลคิว"""
        self.is_running = False

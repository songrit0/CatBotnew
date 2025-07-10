"""
Voice Channel Manager - จัดการการอัปเดตชื่อห้องเสียง
"""
import discord
from datetime import datetime, timedelta
from config_manager import load_config

class VoiceChannelManager:
    def __init__(self, bot):
        self.bot = bot
        self.last_channel_update = {}  # เก็บเวลาการอัพเดตครั้งล่าสุดของแต่ละห้อง
        self.channel_update_queue = {}  # คิวสำหรับการอัพเดตห้อง

    async def update_voice_channel_name(self, channel, guild=None):
        """อัพเดตชื่อห้องเสียงตามจำนวนคนที่อยู่ในห้อง"""
        current_config = load_config()
        channel_id = str(channel.id)
        
        # ตรวจสอบว่าห้องนี้อยู่ในการตั้งค่าหรือไม่
        if channel_id not in current_config["voice_channels"]:
            print(f"⚠️ ห้อง {channel.name} (ID: {channel_id}) ไม่ได้อยู่ในการตั้งค่า")
            return
        
        # นับจำนวนคนที่ไม่ใช่บอท
        human_count = sum(1 for member in channel.members if not member.bot)
        
        # แสดงรายชื่อสมาชิกในห้อง
        members_info = []
        for member in channel.members:
            if member.bot:
                members_info.append(f"🤖 {member.display_name} (Bot)")
            else:
                members_info.append(f"👤 {member.display_name}")
        
        print(f"📊 ห้อง {channel.name} (ID: {channel_id})")
        print(f"   สมาชิกทั้งหมด: {len(channel.members)} คน")
        print(f"   คนจริง: {human_count} คน")
        if members_info:
            print(f"   รายชื่อ: {', '.join(members_info)}")
        else:
            print(f"   ไม่มีใครในห้อง")
        
        # เลือกชื่อห้องตามจำนวนคน
        if human_count > 0:
            new_name = current_config["voice_channels"][channel_id]["occupied_name"]
            print(f"🔄 ห้องมีคน -> เปลี่ยนเป็น '{new_name}'")
        else:
            new_name = current_config["voice_channels"][channel_id]["empty_name"]
            print(f"🔄 ห้องว่าง -> เปลี่ยนเป็น '{new_name}'")
        
        # ตรวจสอบว่าชื่อห้องเหมือนเดิมหรือไม่
        if channel.name == new_name:
            print(f"ℹ️ ชื่อห้องเหมือนเดิมแล้ว: {channel.name}")
            print("─" * 50)
            return
        
        # ตรวจสอบ Rate Limiting
        await self._handle_rate_limiting(channel, new_name, guild, human_count)
    
    async def _handle_rate_limiting(self, channel, new_name, guild, human_count):
        """จัดการ Rate Limiting"""
        now = datetime.now()
        channel_key = str(channel.id)
        
        if channel_key in self.last_channel_update:
            time_diff = now - self.last_channel_update[channel_key]
            if time_diff < timedelta(minutes=5):  # รอ 5 นาที
                await self._handle_rate_limit_wait(channel, new_name, guild, now, time_diff, channel_key)
                return
        
        # อัพเดตชื่อห้อง
        await self._update_channel_name(channel, new_name, guild, human_count, now, channel_key)
    
    async def _handle_rate_limit_wait(self, channel, new_name, guild, now, time_diff, channel_key):
        """จัดการเมื่อต้องรอเนื่องจาก Rate Limiting"""
        remaining_time = timedelta(minutes=5) - time_diff
        remaining_seconds = int(remaining_time.total_seconds())
        
        print(f"⏳ ต้องรอ {remaining_seconds} วินาที ก่อนเปลี่ยนชื่อห้องอีกครั้ง")
        
        # ส่งข้อความแจ้งเตือนในแชท
        await self._send_rate_limit_notification(guild, channel, new_name, now, remaining_time)
        
        # เก็บคิวสำหรับการอัพเดตทีหลัง
        self.channel_update_queue[channel_key] = {
            'channel': channel,
            'new_name': new_name,
            'scheduled_time': now + timedelta(minutes=5, seconds=10),
            'guild': guild
        }
        print(f"📋 เพิ่มในคิว: จะเปลี่ยนชื่อเป็น '{new_name}' ในอีก {remaining_seconds + 10} วินาที")
        print("─" * 50)
    
    async def _update_channel_name(self, channel, new_name, guild, human_count, now, channel_key):
        """อัพเดตชื่อห้องจริง"""
        try:
            print(f"🔧 กำลังเปลี่ยนชื่อจาก '{channel.name}' เป็น '{new_name}'...")
            await channel.edit(name=new_name)
            self.last_channel_update[channel_key] = now
            print(f"✅ อัพเดตชื่อห้องเสร็จสิ้น: {new_name}")
            
            # ส่งข้อความแจ้งเตือนว่าเปลี่ยนชื่อสำเร็จ
            await self._send_success_notification(guild, channel, human_count)
                
        except discord.Forbidden:
            print(f"❌ ไม่มีสิทธิ์เปลี่ยนชื่อห้อง {channel.name}")
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                await self._handle_api_rate_limit(channel, new_name, guild, now, channel_key)
            else:
                print(f"❌ เกิดข้อผิดพลาด: {e}")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดไม่ทราบสาเหตุ: {e}")
        
        print("─" * 50)
    
    async def _handle_api_rate_limit(self, channel, new_name, guild, now, channel_key):
        """จัดการเมื่อถูก Rate Limited โดย Discord API"""
        print(f"⚠️ ถูก Rate Limited โดย Discord API")
        print(f"   จะลองอีกครั้งในภายหลัง...")
        # เก็บคิวสำหรับการอัพเดตทีหลัง
        self.channel_update_queue[channel_key] = {
            'channel': channel,
            'new_name': new_name,
            'scheduled_time': now + timedelta(minutes=5, seconds=10),
            'guild': guild
        }
    
    async def _send_rate_limit_notification(self, guild, channel, new_name, now, remaining_time):
        """ส่งข้อความแจ้งเตือนเมื่อถูก Rate Limit"""
        if not guild:
            return
            
        try:
            text_channel = await self._get_notification_channel(guild)
            if not text_channel:
                return
                
            embed = discord.Embed(
                title="⏳ การเปลี่ยนชื่อห้องเสียงถูกจำกัด",
                description=f"Discord จำกัดการเปลี่ยนชื่อห้องเสียงเป็น 2 ครั้งต่อ 10 นาที",
                color=discord.Color.orange()
            )
            embed.add_field(name="🔊 ห้องเสียง", value=f"{channel.name}", inline=True)
            embed.add_field(name="🎯 จะเปลี่ยนเป็น", value=f"{new_name}", inline=True)
            
            # คำนวณเวลาที่จะอัพเดต
            update_time = now + remaining_time
            timestamp = int(update_time.timestamp())
            embed.add_field(name="⏰ เหลือเวลา", value=f"<t:{timestamp}:R>", inline=True)
            embed.set_footer(text="บอทจะเปลี่ยนชื่อห้องโดยอัตโนมัติเมื่อถึงเวลา")
            
            await text_channel.send(embed=embed)
            print(f"📢 ส่งข้อความแจ้งเตือนในแชท {text_channel.name}")
            
        except Exception as e:
            print(f"❌ ไม่สามารถส่งข้อความแจ้งเตือนได้: {e}")
    
    async def _send_success_notification(self, guild, channel, human_count):
        """ส่งข้อความแจ้งเตือนเมื่อเปลี่ยนชื่อสำเร็จ"""
        if not guild:
            return
            
        try:
            text_channel = await self._get_notification_channel(guild)
            if not text_channel:
                return
                
            embed = discord.Embed(
                title="✅ เปลี่ยนชื่อห้องเสียงสำเร็จ",
                description=f"ห้องเสียงถูกเปลี่ยนชื่อเรียบร้อยแล้ว",
                color=discord.Color.green()
            )
            embed.add_field(name="🔊 ห้องเสียง", value=f"{channel.name}", inline=True)
            embed.add_field(name="👥 จำนวนคน", value=f"{human_count} คน", inline=True)
            
            await text_channel.send(embed=embed)
            print(f"📢 ส่งข้อความแจ้งเตือนการเปลี่ยนชื่อสำเร็จ")
            
        except Exception as e:
            print(f"❌ ไม่สามารถส่งข้อความแจ้งเตือนได้: {e}")
    
    async def _get_notification_channel(self, guild):
        """หาห้องแชทสำหรับส่งการแจ้งเตือน (รองรับหลายห้อง)"""
        current_config = load_config()
        
        # ลองใช้ notification_channels แบบใหม่ก่อน
        notification_channels = current_config.get("notification_channels", [])
        if notification_channels:
            for channel_id in notification_channels:
                text_channel = self.bot.get_channel(int(channel_id))
                if text_channel and text_channel.permissions_for(guild.me).send_messages:
                    return text_channel
        
        # รองรับรูปแบบเก่าเพื่อความเข้ากันได้
        if "notification_channel" in current_config:
            text_channel = self.bot.get_channel(int(current_config["notification_channel"]))
            if text_channel and text_channel.permissions_for(guild.me).send_messages:
                return text_channel
        
        # ถ้าไม่มีห้องที่ระบุหรือไม่มีสิทธิ์ ให้หาห้องแรกที่เข้าถึงได้
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                return ch
        
        return None
    
    def get_queue_info(self):
        """ดึงข้อมูลคิวการอัพเดต"""
        return self.channel_update_queue.copy()
    
    def clear_queue_item(self, channel_id):
        """ลบรายการจากคิว"""
        if channel_id in self.channel_update_queue:
            del self.channel_update_queue[channel_id]
    
    def force_update_time(self, channel_id):
        """บังคับอัพเดตเวลาการเปลี่ยนชื่อ"""
        self.last_channel_update[channel_id] = datetime.now()

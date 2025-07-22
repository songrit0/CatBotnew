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
        self.voice_times = {}  # {(user_id, channel_id): {'join': datetime, 'leave': datetime}}
        from sheets_manager import SheetsManager
        self.sheets = SheetsManager()

    async def _send_log(self, message, guild=None):
        """ส่ง log ไปยัง channel id 1397190290284089537 และ print"""
        print(message)
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_channel = self.bot.get_channel(1397190290284089537)
        # ```log_channel```
        if log_channel:
            try:
                await log_channel.send(f"```[{timestamp}] \n{message}```")
            except Exception as e:
                print(f"[Log Error] {e}")
    
    async def get_voice_rankings(self):
        """ส่งอันดับเวลารวมที่ออนไลน์ในห้องเสียงไปยัง channel id 1397197236605161482"""
        import discord
        from collections import defaultdict
        try:
            spreadsheet = self.sheets.client.open_by_key(self.sheets.sheets_id)
            ws = spreadsheet.worksheet('VoiceTime')
            all_rows = ws.get_all_values()
            headers = all_rows[0] if all_rows else []
            if not headers or 'User ID' not in headers or 'Total Duration (sec)' not in headers or 'Channel ID' not in headers:
                print("[Ranking] ไม่พบ header ที่ต้องการใน VoiceTime")
                return
            user_id_idx = headers.index('User ID')
            channel_id_idx = headers.index('Channel ID')
            total_idx = headers.index('Total Duration (sec)')
            name_map = {}
            # สร้าง mapping user_id -> name จาก member cache
            for guild in self.bot.guilds:
                for member in guild.members:
                    name_map[str(member.id)] = member.display_name
            channel_map = {}
            for guild in self.bot.guilds:
                for channel in guild.voice_channels:
                    channel_map[str(channel.id)] = channel.name
            # รวมเวลาต่อ user/channel
            ranking = defaultdict(lambda: {'total': 0, 'channel_id': '', 'user_id': ''})
            for row in all_rows[1:]:
                if len(row) > max(user_id_idx, channel_id_idx, total_idx):
                    user_id = row[user_id_idx]
                    channel_id = row[channel_id_idx]
                    try:
                        total = float(row[total_idx])
                    except Exception:
                        total = 0
                    key = (user_id, channel_id)
                    ranking[key]['total'] += total
                    ranking[key]['channel_id'] = channel_id
                    ranking[key]['user_id'] = user_id
            # จัดอันดับ
            sorted_rank = sorted(ranking.values(), key=lambda x: x['total'], reverse=True)
            lines = ["RANK | Total Duration (sec) | NAME"]
            for i, entry in enumerate(sorted_rank, 1):
                channelname = channel_map.get(entry['channel_id'], entry['channel_id'])
                # NAME ต้องเป็น display_name ของ user
                name = name_map.get(str(entry['user_id']))
                if not name:
                    # หากไม่พบใน name_map ให้ลองดึงจาก guilds
                    user_id_int = None
                    try:
                        user_id_int = int(entry['user_id'])
                    except Exception:
                        pass
                    name = None
                    if user_id_int:
                        for guild in self.bot.guilds:
                            member = guild.get_member(user_id_int)
                            if member:
                                name = member.display_name
                                break
                    if not name and user_id_int:
                        try:
                            user_obj = await self.bot.fetch_user(user_id_int)
                            name = user_obj.name
                        except Exception:
                            name = "Unknown"
                    if not name:
                        name = "Unknown"
                minutes = int(entry['total'] // 60)
                seconds = int(entry['total'] % 60)
                lines.append(f"{i:>2} | {minutes} นาที {seconds} วินาที | {name}")
              
            msg = "\n".join(lines)
            import datetime
            now_dt = datetime.datetime.now()
            now_str = now_dt.strftime('%Y-%m-%d %H:%M:%S')
            now_ts = int(now_dt.timestamp())
            msg += f"\n[อัพเดตล่าสุด: {now_str} ]\n"
            channel = self.bot.get_channel(1397197236605161482)
            if channel:
                # ลบข้อความ ranking เดิม
                try:
                    async for message in channel.history(limit=20):
                        if message.author == self.bot.user and "RANK | Total Duration (sec) | NAME" in message.content:
                            await message.delete()
                except Exception as e:
                    print(f"[Ranking] ลบข้อความเดิมไม่สำเร็จ: {e}")
                await channel.send(f"```\n{msg}\n``` \n[อัพเดตล่าสุด:(<t:{now_ts}:R>)]")
            else:
                print("[Ranking] ไม่พบ channel id 1397197236605161482")
        except Exception as e:
            print(f"[Ranking Error] {e}")

    async def rankings_background_task(self):
        """background task ส่งอันดับทุก 60 นาที"""
        import asyncio
        while True:
            await self.get_voice_rankings()
            await asyncio.sleep(3600)

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
        import asyncio
        self.bot.loop.create_task(self.rankings_background_task())
    
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
                await self._send_log(f"{member.display_name} ออกจากห้อง: {before.channel.name}", member.guild)
                # --- TIME TRACKING ---
                import datetime
                key = (member.id, before.channel.id)
                now = datetime.datetime.now()
                if key in self.voice_times and 'join' in self.voice_times[key]:
                    join_time = self.voice_times[key]['join']
                    duration = (now - join_time).total_seconds()
                    # Save to Google Sheets
                    await self._save_voice_time(member.id, before.channel.id, join_time, now, duration)
                    self.voice_times[key]['leave'] = now
                    del self.voice_times[key]  # clear after save
                else:
                    # No join time, just log leave
                    await self._save_voice_time(member.id, before.channel.id, None, now, 0)
            if after.channel:
                print(f"   เข้าห้อง: {after.channel.name}")
                await self._send_log(f"{member.display_name} เข้าห้อง: {after.channel.name}", member.guild)
                # --- TIME TRACKING ---
                import datetime
                key = (member.id, after.channel.id)
                now = datetime.datetime.now()
                self.voice_times[key] = {'join': now}

        channels_to_check = set()
        
        # เพิ่มห้องที่ผู้ใช้เข้าไป
        if after.channel:
            channels_to_check.add(after.channel)
        
        # เพิ่มห้องที่ผู้ใช้ออกจาก
        if before.channel:
            channels_to_check.add(before.channel)
        
        # ตรวจสอบและอัพเดตห้องเสียงที่เกี่ยวข้อง
        await self._check_channels(channels_to_check, member.guild)
        # เรียก rankings ทุกครั้งที่มีการเปลี่ยนแปลง
        await self.get_voice_rankings()

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

    async def _save_voice_time(self, user_id, channel_id, join_time, leave_time, duration):
        """บันทึกข้อมูลเวลาเข้า/ออกห้องเสียงลง Google Sheets"""
        import datetime
        import asyncio
        join_str = join_time.strftime('%Y-%m-%d %H:%M:%S') if join_time else ''
        leave_str = leave_time.strftime('%Y-%m-%d %H:%M:%S') if leave_time else ''
        await self._send_log(f"บันทึกเวลา user:{user_id} channel:{channel_id} join:{join_str} leave:{leave_str} duration:{duration}s", guild=None)
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self.sheets.update_or_append_voice_time, user_id, channel_id, join_str, leave_str, duration)
            print(f"[Sheets] บันทึกเวลา user:{user_id} channel:{channel_id} duration:{duration}s")
        except Exception as e:
            print(f"[Sheets Error] {e}")

async def setup(bot, voice_manager, queue_processor):
    """ตั้งค่า Cog"""
    await bot.add_cog(BotEvents(bot, voice_manager, queue_processor))

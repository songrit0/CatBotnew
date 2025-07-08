"""
Bot Commands - คำสั่งต่างๆ ของบอท
"""
import discord
from discord.ext import commands
from datetime import datetime
from config_manager import load_config, is_special_channel
from ui_components import VoiceChannelManagerView

class BotCommands(commands.Cog):
    """Cog สำหรับคำสั่งต่างๆ ของบอท"""
    
    def __init__(self, bot, voice_manager):
        self.bot = bot
        self.voice_manager = voice_manager
    
    def is_special_channel_check(self, ctx):
        """ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง"""
        return is_special_channel(ctx.channel.id)
    
    @commands.command(name='queue')
    async def show_queue(self, ctx):
        """แสดงคิวการอัพเดตห้องเสียง"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        queue = self.voice_manager.get_queue_info()
        
        if not queue:
            await ctx.send("📋 ไม่มีการอัพเดตในคิว")
            return
        
        embed = discord.Embed(
            title="📋 คิวการอัพเดตห้องเสียง",
            description="รายการห้องที่รอการอัพเดต",
            color=discord.Color.yellow()
        )
        
        for channel_key, update_info in queue.items():
            channel = update_info['channel']
            new_name = update_info['new_name']
            scheduled_time = update_info['scheduled_time']
            
            timestamp = int(scheduled_time.timestamp())
            
            embed.add_field(
                name=f"🔊 {channel.name}",
                value=f"จะเปลี่ยนเป็น: {new_name}\n"
                      f"เวลาที่กำหนด: <t:{timestamp}:R>",
                inline=False
            )
        
        embed.set_footer(text=f"ผู้ใช้: {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.command(name='forcenow')
    @commands.has_permissions(manage_channels=True)
    async def force_update_now(self, ctx, channel_id: str = None):
        """บังคับอัพเดตห้องเสียงทันที"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        if channel_id is None:
            await ctx.send("❌ กรุณาระบุ Channel ID")
            return
        
        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            await ctx.send(f"❌ ไม่พบห้อง ID: {channel_id}")
            return
        
        current_config = load_config()
        
        # ลบจากคิวถ้ามี
        self.voice_manager.clear_queue_item(channel_id)
        
        # อัพเดตทันที
        human_count = sum(1 for member in channel.members if not member.bot)
        if human_count > 0:
            new_name = current_config["voice_channels"][channel_id]["occupied_name"]
        else:
            new_name = current_config["voice_channels"][channel_id]["empty_name"]
        
        try:
            await channel.edit(name=new_name)
            self.voice_manager.force_update_time(channel_id)
            await ctx.send(f"✅ อัพเดตห้อง {channel.name} เป็น '{new_name}' เสร็จสิ้น")
        except Exception as e:
            await ctx.send(f"❌ ไม่สามารถอัพเดตได้: {e}")
    
    @commands.command(name='debug')
    async def debug_channels(self, ctx):
        """คำสั่งสำหรับ debug ปัญหา"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        embed = discord.Embed(
            title="🔍 Debug Information",
            description="ข้อมูลการ debug",
            color=discord.Color.orange()
        )
        
        # แสดงข้อมูลการตั้งค่า
        current_config = load_config()
        config_info = []
        for channel_id, settings in current_config["voice_channels"].items():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                human_count = sum(1 for member in channel.members if not member.bot)
                total_members = len(channel.members)
                config_info.append(f"ID: {channel_id}")
                config_info.append(f"ชื่อปัจจุบัน: {channel.name}")
                config_info.append(f"คนทั้งหมด: {total_members}")
                config_info.append(f"คนจริง: {human_count}")
                config_info.append(f"ชื่อเมื่อว่าง: {settings['empty_name']}")
                config_info.append(f"ชื่อเมื่อมีคน: {settings['occupied_name']}")
                config_info.append("─" * 30)
            else:
                config_info.append(f"❌ ไม่พบห้อง ID: {channel_id}")
        
        embed.add_field(
            name="📊 สถานะห้องเสียง",
            value="\n".join(config_info) if config_info else "ไม่มีข้อมูล",
            inline=False
        )
        
        # แสดงข้อมูลระบบจัดการคิว
        queue = self.voice_manager.get_queue_info()
        queue_info = []
        if queue:
            queue_info.append(f"จำนวนคิว: {len(queue)}")
            for channel_key, update_info in queue.items():
                channel = update_info['channel']
                scheduled_time = update_info['scheduled_time']
                remaining_time = scheduled_time - datetime.now()
                remaining_seconds = int(remaining_time.total_seconds())
                queue_info.append(f"- {channel.name}: {remaining_seconds}s")
        else:
            queue_info.append("ไม่มีคิว")
        
        embed.add_field(
            name="🔄 ระบบจัดการคิว",
            value="\n".join(queue_info),
            inline=False
        )
        
        embed.set_footer(text=f"ผู้ใช้: {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.command(name='test')
    async def test_update(self, ctx, channel_id: str = None):
        """ทดสอบการอัพเดตห้องเสียงด้วยตนเอง"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        current_config = load_config()
        if channel_id is None:
            # ใช้ห้องแรกในการตั้งค่า
            if not current_config["voice_channels"]:
                await ctx.send("❌ ไม่มี voice channels ที่ตั้งค่าไว้")
                return
            channel_id = list(current_config["voice_channels"].keys())[0]
        
        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            await ctx.send(f"❌ ไม่พบห้อง ID: {channel_id}")
            return
        
        await ctx.send(f"🔄 กำลังทดสอบอัพเดตห้อง {channel.name}...")
        await self.voice_manager.update_voice_channel_name(channel)
        await ctx.send("✅ ทดสอบเสร็จสิ้น")
    
    @commands.command(name='check')
    async def check_channels(self, ctx):
        """คำสั่งตรวจสอบสถานะห้องเสียงทั้งหมด"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        current_config = load_config()
        embed = discord.Embed(
            title="สถานะห้องเสียง",
            description="ข้อมูลห้องเสียงที่กำลังติดตาม",
            color=discord.Color.blue()
        )
        
        for channel_id, settings in current_config["voice_channels"].items():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                human_count = sum(1 for member in channel.members if not member.bot)
                embed.add_field(
                    name=f"🔊 {channel.name}",
                    value=f"คนในห้อง: {human_count} คน\n"
                         f"ชื่อเมื่อว่าง: {settings['empty_name']}\n"
                         f"ชื่อเมื่อมีคน: {settings['occupied_name']}",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='update')
    @commands.has_permissions(manage_channels=True)
    async def force_update(self, ctx):
        """บังคับอัพเดตชื่อห้องเสียงทั้งหมด"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        current_config = load_config()
        updated_count = 0
        for channel_id in current_config["voice_channels"].keys():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await self.voice_manager.update_voice_channel_name(channel)
                updated_count += 1
        
        await ctx.send(f"✅ อัพเดตห้องเสียงเสร็จสิ้น ({updated_count} ห้อง)")
    
    @commands.command(name='listauth')
    async def list_authorized(self, ctx):
        """แสดงข้อมูลสิทธิ์การใช้คำสั่ง"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        if not ctx.guild:
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในเซิร์ฟเวอร์เท่านั้น")
            return
        
        embed = discord.Embed(
            title="👥 สิทธิ์การใช้คำสั่ง",
            description="คำสั่งทั้งหมดใช้ได้กับทุกคนในห้องนี้",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔹 ผู้ที่สามารถใช้คำสั่งได้",
            value="👥 ทุกคนในห้องนี้\n🚫 ไม่จำเป็นต้องเป็น Administrator",
            inline=False
        )
        
        embed.set_footer(text="ระบบเปิดให้ทุกคนใช้งานในห้องนี้")
        await ctx.send(embed=embed)
    
    @commands.command(name='info')
    async def show_info(self, ctx):
        """แสดงข้อมูลห้องเสียง"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        current_config = load_config()
        
        embed = discord.Embed(
            title="📊 ข้อมูลห้องเสียงทั้งหมด",
            description="สถานะของห้องเสียงที่บอทกำลังติดตาม",
            color=discord.Color.blue()
        )
        
        # แสดงข้อมูลห้องเสียงทั้งหมด
        for channel_id, settings in current_config["voice_channels"].items():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                human_count = sum(1 for member in channel.members if not member.bot)
                
                # นับจำนวนคนในห้อง
                member_names = []
                for member in channel.members:
                    if not member.bot:
                        member_names.append(f"👤 {member.display_name}")
                
                status = "🟢 มีคน" if human_count > 0 else "🔴 ว่าง"
                
                field_value = f"**สถานะ:** {status}\n"
                field_value += f"**จำนวนคน:** {human_count} คน\n"
                field_value += f"**ชื่อเมื่อว่าง:** {settings['empty_name']}\n"
                field_value += f"**ชื่อเมื่อมีคน:** {settings['occupied_name']}\n"
                
                if member_names:
                    field_value += f"**สมาชิก:** {', '.join(member_names[:5])}"
                    if len(member_names) > 5:
                        field_value += f" และอีก {len(member_names) - 5} คน"
                
                embed.add_field(
                    name=f"🔊 {channel.name}",
                    value=field_value,
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"❌ ห้อง ID: {channel_id}",
                    value="ไม่พบห้องนี้",
                    inline=False
                )
        
        # แสดงข้อมูลคิว
        queue = self.voice_manager.get_queue_info()
        if queue:
            queue_info = []
            for channel_key, update_info in queue.items():
                channel = update_info['channel']
                new_name = update_info['new_name']
                scheduled_time = update_info['scheduled_time']
                
                remaining_time = scheduled_time - datetime.now()
                remaining_seconds = int(remaining_time.total_seconds())
                
                if remaining_seconds > 0:
                    queue_info.append(f"🔄 {channel.name} → {new_name} (อีก {remaining_seconds} วินาที)")
            
            if queue_info:
                embed.add_field(
                    name="⏳ คิวการอัพเดต",
                    value="\n".join(queue_info),
                    inline=False
                )
        
        embed.set_footer(text="ข้อมูล ณ เวลาปัจจุบัน")
        await ctx.send(embed=embed)
    
    @commands.command(name='status')
    async def show_status(self, ctx):
        """แสดงสถานะบอทและระบบ"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        current_config = load_config()
        
        embed = discord.Embed(
            title="🤖 สถานะบอท",
            description="ข้อมูลการทำงานของบอท",
            color=discord.Color.green()
        )
        
        # ข้อมูลพื้นฐาน
        embed.add_field(
            name="📊 ข้อมูลพื้นฐาน",
            value=f"**ชื่อบอท:** {self.bot.user.name}\n**ID:** {self.bot.user.id}\n**Latency:** {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        # จำนวนเซิร์ฟเวอร์และสมาชิก
        embed.add_field(
            name="🌐 การเชื่อมต่อ",
            value=f"**เซิร์ฟเวอร์:** {len(self.bot.guilds)} เซิร์ฟเวอร์\n**สมาชิก:** {sum(guild.member_count for guild in self.bot.guilds)} คน",
            inline=True
        )
        
        # ข้อมูลห้องเสียง
        voice_channels_count = len(current_config["voice_channels"])
        queue_count = len(self.voice_manager.get_queue_info())
        embed.add_field(
            name="🔊 ห้องเสียง",
            value=f"**กำลังติดตาม:** {voice_channels_count} ห้อง\n**คิวการอัพเดต:** {queue_count} รายการ",
            inline=True
        )
        
        embed.set_footer(text="บอททำงานปกติ")
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def show_help(self, ctx):
        """แสดงคำสั่งที่ใช้ได้"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return
        
        embed = discord.Embed(
            title="📋 คำสั่งที่ใช้ได้",
            description="คำสั่งทั้งหมดที่สามารถใช้ในห้องนี้",
            color=discord.Color.purple()
        )
        
        # คำสั่งสำหรับทุกคน
        embed.add_field(
            name="👥 คำสั่งสำหรับทุกคน",
            value="**!info** - แสดงข้อมูลห้องเสียงทั้งหมด\n**!status** - แสดงสถานะบอท\n**!help** - แสดงคำสั่งนี้\n**!queue** - แสดงคิวการอัพเดต\n**!debug** - แสดงข้อมูลดีบัก\n**!test** - ทดสอบระบบ\n**!check** - ตรวจสอบสถานะห้อง\n**!listauth** - แสดงข้อมูลสิทธิ์",
            inline=False
        )
        
        # คำสั่งสำหรับ Administrator
        embed.add_field(
            name="👑 คำสั่งสำหรับ Administrator",
            value="**!forcenow** - บังคับอัพเดตทันที\n**!update** - อัพเดตห้องเสียง",
            inline=False
        )
        
        # คำสั่งจัดการระบบ
        embed.add_field(
            name="⚙️ คำสั่งจัดการระบบ",
            value="**!manage** - จัดการการตั้งค่า voice channels (ทุกคนใช้ได้)",
            inline=False
        )
        
        embed.set_footer(text="คำสั่งส่วนใหญ่ใช้ได้กับทุกคนในห้องนี้")
        
        # สร้างปุ่มคำสั่งต่างๆ
        view = discord.ui.View(timeout=300)  # 5 นาที
        
        # แถวที่ 1 - คำสั่งพื้นฐาน
        info_button = discord.ui.Button(
            label="📊 Info", 
            style=discord.ButtonStyle.primary,
            custom_id="cmd_info"
        )
        status_button = discord.ui.Button(
            label="🤖 Status", 
            style=discord.ButtonStyle.primary,
            custom_id="cmd_status"
        )
        queue_button = discord.ui.Button(
            label="📋 Queue", 
            style=discord.ButtonStyle.secondary,
            custom_id="cmd_queue"
        )
        check_button = discord.ui.Button(
            label="🔍 Check", 
            style=discord.ButtonStyle.secondary,
            custom_id="cmd_check"
        )
        
        # แถวที่ 2 - คำสั่งเพิ่มเติม
        debug_button = discord.ui.Button(
            label="🔧 Debug", 
            style=discord.ButtonStyle.secondary,
            custom_id="cmd_debug"
        )
        test_button = discord.ui.Button(
            label="🧪 Test", 
            style=discord.ButtonStyle.secondary,
            custom_id="cmd_test"
        )
        manage_button = discord.ui.Button(
            label="⚙️ Manage", 
            style=discord.ButtonStyle.success,
            custom_id="cmd_manage"
        )
        listauth_button = discord.ui.Button(
            label="👥 Auth", 
            style=discord.ButtonStyle.secondary,
            custom_id="cmd_listauth"
        )
        
        # เพิ่มการตอบสนองเมื่อกดปุ่ม
        async def button_callback(interaction):
            # ตรวจสอบว่าผู้กดปุ่มเป็นคนเดียวกับที่ใช้คำสั่ง
            if interaction.user != ctx.author:
                await interaction.response.send_message("❌ คุณไม่สามารถใช้ปุ่มนี้ได้", ephemeral=True)
                return
                
            command_map = {
                "cmd_info": "info",
                "cmd_status": "status", 
                "cmd_queue": "queue",
                "cmd_check": "check",
                "cmd_debug": "debug",
                "cmd_test": "test",
                "cmd_listauth": "listauth",
                "cmd_manage": "manage"
            }
            
            command_name = command_map.get(interaction.data['custom_id'])
            if command_name:
                await interaction.response.send_message(f"🔄 กำลังเรียกใช้คำสั่ง `!{command_name}`...", ephemeral=True)
                
                # เรียกใช้คำสั่งตามปุ่มที่กด
                if command_name == "info":
                    await self.show_info(ctx)
                elif command_name == "status":
                    await self.show_status(ctx)
                elif command_name == "queue":
                    await self.show_queue(ctx)
                elif command_name == "check":
                    await self.check_channels(ctx)
                elif command_name == "debug":
                    await self.debug_channels(ctx)
                elif command_name == "test":
                    await self.test_update(ctx)
                elif command_name == "listauth":
                    await self.list_authorized(ctx)
                elif command_name == "manage":
                    await self.manage_voice_channels(ctx)
        
        # กำหนด callback ให้ปุ่มทั้งหมด
        info_button.callback = button_callback
        status_button.callback = button_callback
        queue_button.callback = button_callback
        check_button.callback = button_callback
        debug_button.callback = button_callback
        test_button.callback = button_callback
        listauth_button.callback = button_callback
        manage_button.callback = button_callback
        
        # เพิ่มปุ่มใน view (แถวละ 4 ปุ่ม)
        view.add_item(info_button)
        view.add_item(status_button)
        view.add_item(queue_button)
        view.add_item(check_button)
        view.add_item(debug_button)
        view.add_item(test_button)
        view.add_item(manage_button)
        view.add_item(listauth_button)
        
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name='manage', help='จัดการ voice channels')
    async def manage_voice_channels(self, ctx):
        """จัดการ voice channels"""
        if not self.is_special_channel_check(ctx):
            await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
            return

        # โหลด config ใหม่
        current_config = load_config()
        
        embed = discord.Embed(
            title="🔧 จัดการ Voice Channels",
            description="เลือกการจัดการที่ต้องการ:",
            color=discord.Color.blue()
        )
        
        view = VoiceChannelManagerView(ctx.author.id, current_config)
        await ctx.send(embed=embed, view=view)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """จัดการข้อผิดพลาดของคำสั่ง"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้")
        elif isinstance(error, commands.CommandNotFound):
            pass  # ไม่แสดงข้อผิดพลาดสำหรับคำสั่งที่ไม่พบ
        else:
            print(f"Error: {error}")

async def setup(bot, voice_manager):
    """ตั้งค่า Cog"""
    await bot.add_cog(BotCommands(bot, voice_manager))

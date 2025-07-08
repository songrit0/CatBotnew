"""
Music Commands - คำสั่งและปุ่มสำหรับระบบเพลง
"""
import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from music_manager import MusicManager, Song
from typing import Optional

class MusicControlView(View):
    """View สำหรับควบคุมเพลง"""
    
    def __init__(self, music_manager: MusicManager, guild_id: int):
        super().__init__(timeout=300)
        self.music_manager = music_manager
        self.guild_id = guild_id
        
    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.secondary, custom_id="pause")
    async def pause_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มหยุดชั่วคราว"""
        success = await self.music_manager.pause_song(self.guild_id)
        if success:
            button.label = "▶️"
            button.custom_id = "resume"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("⏸️ หยุดเพลงชั่วคราว", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่มีเพลงที่เล่นอยู่", ephemeral=True)
            
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, custom_id="resume")
    async def resume_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มเล่นต่อ"""
        success = await self.music_manager.resume_song(self.guild_id)
        if success:
            button.label = "⏸️"
            button.custom_id = "pause"
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("▶️ เล่นเพลงต่อ", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่มีเพลงที่หยุดอยู่", ephemeral=True)
            
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.primary, custom_id="skip")
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มข้ามเพลง"""
        queue = self.music_manager.get_music_queue(self.guild_id)
        current_song = queue.current_song
        
        success = await self.music_manager.skip_song(self.guild_id)
        if success:
            if current_song:
                await interaction.response.send_message(f"⏭️ ข้ามเพลง: **{current_song.title}**", ephemeral=True)
            else:
                await interaction.response.send_message("⏭️ ข้ามเพลง", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่มีเพลงที่เล่นอยู่", ephemeral=True)
            
    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.danger, custom_id="stop")
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มหยุดเพลง"""
        await self.music_manager.stop_music(self.guild_id)
        await interaction.response.send_message("⏹️ หยุดเพลงและล้างคิวแล้ว", ephemeral=True)
        
    @discord.ui.button(label="📋", style=discord.ButtonStyle.secondary, custom_id="queue")
    async def queue_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มดูคิว"""
        queue = self.music_manager.get_music_queue(self.guild_id)
        
        embed = discord.Embed(
            title="🎵 คิวเพลง",
            color=discord.Color.blue()
        )
        
        # เพลงที่เล่นอยู่
        if queue.current_song:
            embed.add_field(
                name="🎵 กำลังเล่น",
                value=f"**{queue.current_song.title}**\n"
                      f"ระยะเวลา: {queue.current_song.duration}\n"
                      f"ขอโดย: {queue.current_song.requester.mention}",
                inline=False
            )
        
        # คิวเพลง
        if queue.queue:
            queue_text = ""
            for i, song in enumerate(queue.queue[:10], 1):  # แสดงแค่ 10 เพลงแรก
                queue_text += f"{i}. **{song.title}** ({song.duration}) - {song.requester.mention}\n"
            
            if len(queue.queue) > 10:
                queue_text += f"\n... และอีก {len(queue.queue) - 10} เพลง"
                
            embed.add_field(
                name="📋 คิวถัดไป",
                value=queue_text,
                inline=False
            )
        else:
            embed.add_field(
                name="📋 คิวถัดไป",
                value="ไม่มีเพลงในคิว",
                inline=False
            )
            
        # สถานะลูป
        loop_status = ""
        if queue.loop:
            loop_status += "🔂 ลูปเพลงปัจจุบัน\n"
        if queue.loop_queue:
            loop_status += "🔁 ลูปคิว\n"
        if not loop_status:
            loop_status = "ไม่ได้เปิดลูป"
            
        embed.add_field(
            name="🔄 สถานะลูป",
            value=loop_status,
            inline=False
        )
        
        embed.set_footer(text=f"คิวทั้งหมด: {len(queue.queue)} เพลง")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class VolumeControlView(View):
    """View สำหรับควบคุมระดับเสียง"""
    
    def __init__(self, music_manager: MusicManager, guild_id: int, current_volume: int = 50):
        super().__init__(timeout=60)
        self.music_manager = music_manager
        self.guild_id = guild_id
        self.current_volume = current_volume
        
    @discord.ui.button(label="🔉", style=discord.ButtonStyle.secondary)
    async def volume_down(self, interaction: discord.Interaction, button: Button):
        """ลดระดับเสียง"""
        new_volume = max(0, self.current_volume - 10)
        success = self.music_manager.set_volume(self.guild_id, new_volume)
        if success:
            self.current_volume = new_volume
            await interaction.response.send_message(f"🔉 ระดับเสียง: {new_volume}%", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่สามารถปรับระดับเสียงได้", ephemeral=True)
            
    @discord.ui.button(label="🔊", style=discord.ButtonStyle.secondary)
    async def volume_up(self, interaction: discord.Interaction, button: Button):
        """เพิ่มระดับเสียง"""
        new_volume = min(100, self.current_volume + 10)
        success = self.music_manager.set_volume(self.guild_id, new_volume)
        if success:
            self.current_volume = new_volume
            await interaction.response.send_message(f"🔊 ระดับเสียง: {new_volume}%", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่สามารถปรับระดับเสียงได้", ephemeral=True)

class MusicCommands(commands.Cog):
    """Cog สำหรับคำสั่งเพลง"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_manager = MusicManager(bot)
        
    async def cog_before_invoke(self, ctx):
        """ตรวจสอบก่อนใช้คำสั่ง"""
        if not ctx.author.voice:
            raise commands.CommandError("❌ คุณต้องอยู่ในห้องเสียงก่อน")
            
    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, search: str):
        """เล่นเพลงจาก YouTube"""
        voice_channel = ctx.author.voice.channel
        
        # เข้าร่วมห้องเสียง
        try:
            voice_client = await self.music_manager.join_voice_channel(voice_channel)
        except Exception as e:
            await ctx.send(f"❌ ไม่สามารถเข้าร่วมห้องเสียงได้: {e}")
            return
            
        # ส่งข้อความกำลังค้นหา
        search_msg = await ctx.send(f"🔍 กำลังค้นหา: **{search}**...")
        
        try:
            # เพิ่มเพลงในคิว
            song = await self.music_manager.add_to_queue(
                ctx.guild.id, search, ctx.author
            )
            
            queue = self.music_manager.get_music_queue(ctx.guild.id)
            
            # สร้าง embed
            embed = discord.Embed(
                title="✅ เพิ่มเพลงในคิวแล้ว",
                description=f"**{song.title}**",
                color=discord.Color.green()
            )
            embed.add_field(name="ระยะเวลา", value=song.duration, inline=True)
            embed.add_field(name="ขอโดย", value=ctx.author.mention, inline=True)
            embed.add_field(name="ตำแหน่งในคิว", value=len(queue.queue), inline=True)
            
            # ถ้าไม่มีเพลงเล่นอยู่ ให้เริ่มเล่นทันที
            if not voice_client.is_playing() and not voice_client.is_paused():
                await self.music_manager.play_next(ctx.guild.id)
                embed.title = "🎵 เริ่มเล่นเพลง"
                embed.color = discord.Color.blue()
                
            # สร้างปุ่มควบคุม
            view = MusicControlView(self.music_manager, ctx.guild.id)
            
            await search_msg.edit(content=None, embed=embed, view=view)
            
        except Exception as e:
            error_message = str(e)
            
            # สร้างข้อความช่วยเหลือตามประเภทของข้อผิดพลาด
            if "Sign in to confirm you're not a bot" in error_message or "YouTube ขอให้ยืนยันตัวตน" in error_message:
                help_embed = discord.Embed(
                    title="🚫 YouTube ขอให้ยืนยันตัวตน",
                    description="วิธีแก้ไข:",
                    color=discord.Color.orange()
                )
                help_embed.add_field(
                    name="💡 แนะนำ", 
                    value="• ใช้ชื่อเพลงแทนลิงก์\n• ลองค้นหาด้วยคำอื่น\n• รอสักครู่แล้วลองใหม่", 
                    inline=False
                )
                help_embed.add_field(
                    name="✅ ตัวอย่าง", 
                    value="`!play shape of you ed sheeran`\n`!play เพลงไทยเพราะๆ`", 
                    inline=False
                )
                help_embed.set_footer(text="ดู YOUTUBE_FIX.md สำหรับข้อมูลเพิ่มเติม")
                
                await search_msg.edit(content=None, embed=help_embed)
            else:
                await search_msg.edit(content=f"❌ เกิดข้อผิดพลาด: {error_message}\n\n💡 **คำแนะนำ:** ลองใช้ชื่อเพลงแทนลิงก์")
            
    @commands.command(name='skip', aliases=['s'])
    async def skip(self, ctx):
        """ข้ามเพลงปัจจุบัน"""
        queue = self.music_manager.get_music_queue(ctx.guild.id)
        current_song = queue.current_song
        
        success = await self.music_manager.skip_song(ctx.guild.id)
        if success:
            if current_song:
                await ctx.send(f"⏭️ ข้ามเพลง: **{current_song.title}**")
            else:
                await ctx.send("⏭️ ข้ามเพลง")
        else:
            await ctx.send("❌ ไม่มีเพลงที่เล่นอยู่")
            
    @commands.command(name='stop')
    async def stop(self, ctx):
        """หยุดเพลงและล้างคิว"""
        await self.music_manager.stop_music(ctx.guild.id)
        await ctx.send("⏹️ หยุดเพลงและล้างคิวแล้ว")
        
    @commands.command(name='pause')
    async def pause(self, ctx):
        """หยุดเพลงชั่วคราว"""
        success = await self.music_manager.pause_song(ctx.guild.id)
        if success:
            await ctx.send("⏸️ หยุดเพลงชั่วคราว")
        else:
            await ctx.send("❌ ไม่มีเพลงที่เล่นอยู่")
            
    @commands.command(name='resume')
    async def resume(self, ctx):
        """เล่นเพลงต่อ"""
        success = await self.music_manager.resume_song(ctx.guild.id)
        if success:
            await ctx.send("▶️ เล่นเพลงต่อ")
        else:
            await ctx.send("❌ ไม่มีเพลงที่หยุดอยู่")
            
    @commands.command(name='queue', aliases=['q'])
    async def show_queue(self, ctx):
        """แสดงคิวเพลง"""
        queue = self.music_manager.get_music_queue(ctx.guild.id)
        
        embed = discord.Embed(
            title="🎵 คิวเพลง",
            color=discord.Color.blue()
        )
        
        # เพลงที่เล่นอยู่
        if queue.current_song:
            embed.add_field(
                name="🎵 กำลังเล่น",
                value=f"**{queue.current_song.title}**\n"
                      f"ระยะเวลา: {queue.current_song.duration}\n"
                      f"ขอโดย: {queue.current_song.requester.mention}",
                inline=False
            )
        
        # คิวเพลง
        if queue.queue:
            queue_text = ""
            for i, song in enumerate(queue.queue[:10], 1):
                queue_text += f"{i}. **{song.title}** ({song.duration}) - {song.requester.mention}\n"
            
            if len(queue.queue) > 10:
                queue_text += f"\n... และอีก {len(queue.queue) - 10} เพลง"
                
            embed.add_field(
                name="📋 คิวถัดไป",
                value=queue_text,
                inline=False
            )
        else:
            embed.add_field(
                name="📋 คิวถัดไป",
                value="ไม่มีเพลงในคิว",
                inline=False
            )
            
        embed.set_footer(text=f"คิวทั้งหมด: {len(queue.queue)} เพลง")
        
        # สร้างปุ่มควบคุม
        view = MusicControlView(self.music_manager, ctx.guild.id)
        
        await ctx.send(embed=embed, view=view)
        
    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx, volume: int = None):
        """ตั้งค่าระดับเสียง (0-100)"""
        if volume is None:
            # แสดงปุ่มควบคุมระดับเสียง
            view = VolumeControlView(self.music_manager, ctx.guild.id)
            await ctx.send("🔊 ใช้ปุ่มด้านล่างเพื่อปรับระดับเสียง", view=view)
            return
            
        if not 0 <= volume <= 100:
            await ctx.send("❌ ระดับเสียงต้องอยู่ระหว่าง 0-100")
            return
            
        success = self.music_manager.set_volume(ctx.guild.id, volume)
        if success:
            await ctx.send(f"🔊 ตั้งระดับเสียงเป็น {volume}%")
        else:
            await ctx.send("❌ ไม่สามารถปรับระดับเสียงได้")
            
    @commands.command(name='leave', aliases=['disconnect'])
    async def leave(self, ctx):
        """ออกจากห้องเสียง"""
        await self.music_manager.leave_voice_channel(ctx.guild.id)
        await ctx.send("👋 ออกจากห้องเสียงแล้ว")
        
    @commands.command(name='loop')
    async def loop(self, ctx, mode: str = None):
        """ตั้งค่าลูป (song/queue/off)"""
        queue = self.music_manager.get_music_queue(ctx.guild.id)
        
        if mode is None:
            # แสดงสถานะลูปปัจจุบัน
            status = "ไม่ได้เปิดลูป"
            if queue.loop:
                status = "🔂 ลูปเพลงปัจจุบัน"
            elif queue.loop_queue:
                status = "🔁 ลูปคิว"
                
            await ctx.send(f"🔄 สถานะลูป: {status}")
            return
            
        mode = mode.lower()
        
        if mode == "song":
            queue.loop = True
            queue.loop_queue = False
            await ctx.send("🔂 เปิดลูปเพลงปัจจุบัน")
        elif mode == "queue":
            queue.loop = False
            queue.loop_queue = True
            await ctx.send("🔁 เปิดลูปคิว")
        elif mode == "off":
            queue.loop = False
            queue.loop_queue = False
            await ctx.send("🔄 ปิดลูป")
        else:
            await ctx.send("❌ โหมดลูปที่รองรับ: song, queue, off")
            
    @commands.command(name='shuffle')
    async def shuffle(self, ctx):
        """สลับเพลงในคิว"""
        queue = self.music_manager.get_music_queue(ctx.guild.id)
        
        if not queue.queue:
            await ctx.send("❌ ไม่มีเพลงในคิวให้สลับ")
            return
            
        queue.shuffle()
        await ctx.send(f"🔀 สลับเพลงในคิวแล้ว ({len(queue.queue)} เพลง)")
        
    @commands.command(name='remove')
    async def remove(self, ctx, index: int):
        """ลบเพลงจากคิว"""
        queue = self.music_manager.get_music_queue(ctx.guild.id)
        
        if not queue.queue:
            await ctx.send("❌ ไม่มีเพลงในคิว")
            return
            
        if not 1 <= index <= len(queue.queue):
            await ctx.send(f"❌ ตำแหน่งต้องอยู่ระหว่าง 1-{len(queue.queue)}")
            return
            
        removed_song = queue.queue[index - 1]
        success = queue.remove(index - 1)
        
        if success:
            await ctx.send(f"🗑️ ลบเพลง **{removed_song.title}** ออกจากคิวแล้ว")
        else:
            await ctx.send("❌ ไม่สามารถลบเพลงได้")
            
    @commands.command(name='nowplaying', aliases=['np'])
    async def now_playing(self, ctx):
        """แสดงเพลงที่เล่นอยู่"""
        queue = self.music_manager.get_music_queue(ctx.guild.id)
        
        if not queue.current_song:
            await ctx.send("❌ ไม่มีเพลงที่เล่นอยู่")
            return
            
        song = queue.current_song
        
        embed = discord.Embed(
            title="🎵 กำลังเล่น",
            description=f"**{song.title}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="ระยะเวลา", value=song.duration, inline=True)
        embed.add_field(name="ขอโดย", value=song.requester.mention, inline=True)
        embed.add_field(name="URL", value=f"[คลิกที่นี่]({song.url})", inline=True)
        
        # สร้างปุ่มควบคุม
        view = MusicControlView(self.music_manager, ctx.guild.id)
        
        await ctx.send(embed=embed, view=view)
        
    @commands.command(name='musichelp', aliases=['mhelp'])
    async def music_help(self, ctx):
        """แสดงคำแนะนำเมื่อเจอปัญหาเพลง"""
        embed = discord.Embed(
            title="🎵 วิธีแก้ปัญหาเพลง",
            description="หากเจอปัญหาในการเล่นเพลง ลองวิธีเหล่านี้:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔍 วิธีค้นหาที่แนะนำ",
            value="""
            ✅ `!play shape of you ed sheeran`
            ✅ `!play เพลงไทยเพราะๆ`
            ✅ `!play official audio [ชื่อเพลง]`
            
            ❌ หลีกเลี่ยงลิงก์ YouTube โดยตรง
            """,
            inline=False
        )
        
        embed.add_field(
            name="⚠️ หากเจอข้อผิดพลาด",
            value="""
            • รอ 1-2 นาทีแล้วลองใหม่
            • เปลี่ยนคำค้นหา
            • ใช้ชื่อเพลงแทนลิงก์
            • ลอง `!play test` เพื่อทดสอบ
            """,
            inline=False
        )
        
        embed.add_field(
            name="🎯 คำสั่งที่มี",
            value="`!play` • `!skip` • `!queue` • `!stop` • `!music`",
            inline=False
        )
        
        embed.set_footer(text="หากยังมีปัญหา โปรดติดต่อ Admin")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """ตั้งค่า Cog"""
    await bot.add_cog(MusicCommands(bot))

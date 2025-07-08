"""
UI Components - คอมโพเนนต์ UI สำหรับ Discord (Views, Modals, Buttons)
"""
import discord
from discord.ui import View, Modal, TextInput, Button, Select
from config_manager import load_config, save_config

class VoiceChannelManagerView(View):
    """View หลักสำหรับจัดการ Voice Channels"""
    
    def __init__(self, user_id, config):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.config = config
        self.update_buttons()
    
    def update_buttons(self):
        """อัพเดตปุ่มต่างๆ"""
        self.clear_items()
        
        # ปุ่มสำหรับดูรายการ voice channels
        list_button = Button(
            label="📋 ดูรายการ (List)",
            style=discord.ButtonStyle.primary
        )
        list_button.callback = self.list_channels
        self.add_item(list_button)
        
        # ปุ่มสำหรับเพิ่ม voice channel ใหม่
        add_button = Button(
            label="➕ เพิ่มใหม่ (Add)",
            style=discord.ButtonStyle.green
        )
        add_button.callback = self.add_channel
        self.add_item(add_button)
        
        # ปุ่มสำหรับแก้ไข voice channel
        edit_button = Button(
            label="✏️ แก้ไข (Edit)",
            style=discord.ButtonStyle.secondary
        )
        edit_button.callback = self.edit_channel
        self.add_item(edit_button)
        
        # ปุ่มสำหรับลบ voice channel
        delete_button = Button(
            label="🗑️ ลบ (Delete)",
            style=discord.ButtonStyle.red
        )
        delete_button.callback = self.delete_channel
        self.add_item(delete_button)
    
    async def interaction_check(self, interaction):
        """ตรวจสอบสิทธิ์การใช้งาน"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("คุณไม่สามารถใช้งานปุ่มนี้ได้", ephemeral=True)
            return False
        return True
    
    async def list_channels(self, interaction):
        """แสดงรายการ Voice Channels"""
        await interaction.response.defer()
        
        # โหลด config ใหม่
        current_config = load_config()
        
        embed = discord.Embed(
            title="📋 รายการ Voice Channels",
            color=discord.Color.blue()
        )
        
        if not current_config['voice_channels']:
            embed.description = "ไม่มี voice channels ที่ตั้งค่าไว้"
        else:
            description = ""
            for i, (channel_id, channel_data) in enumerate(current_config['voice_channels'].items(), 1):
                description += f"**{i}.** <#{channel_id}>\n"
                description += f"   • ชื่อเมื่อว่าง: `{channel_data['empty_name']}`\n"
                description += f"   • ชื่อเมื่อมีคน: `{channel_data['occupied_name']}`\n\n"
            embed.description = description
        
        # อัปเดต config ใน view
        self.config = current_config
        
        await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
    
    async def add_channel(self, interaction):
        """เพิ่ม Voice Channel ใหม่"""
        await interaction.response.send_modal(AddChannelModal(self.user_id, self.config, self))
    
    async def edit_channel(self, interaction):
        """แก้ไข Voice Channel"""
        # โหลด config ใหม่
        current_config = load_config()
        
        if not current_config['voice_channels']:
            await interaction.response.send_message("ไม่มี voice channels ที่จะแก้ไข", ephemeral=True)
            return
        
        # อัปเดต config ใน view
        self.config = current_config
        
        await interaction.response.send_message(
            "เลือก voice channel ที่ต้องการแก้ไข:",
            view=EditChannelSelectView(self.user_id, self.config, self),
            ephemeral=True
        )
    
    async def delete_channel(self, interaction):
        """ลบ Voice Channel"""
        # โหลด config ใหม่
        current_config = load_config()
        
        if not current_config['voice_channels']:
            await interaction.response.send_message("ไม่มี voice channels ที่จะลบ", ephemeral=True)
            return
        
        # อัปเดต config ใน view
        self.config = current_config
        
        await interaction.response.send_message(
            "เลือก voice channel ที่ต้องการลบ:",
            view=DeleteChannelSelectView(self.user_id, self.config, self),
            ephemeral=True
        )

class AddChannelModal(Modal):
    """Modal สำหรับเพิ่ม Voice Channel ใหม่"""
    
    def __init__(self, user_id, config, parent_view):
        super().__init__(title="เพิ่ม Voice Channel ใหม่", timeout=300)
        self.user_id = user_id
        self.config = config
        self.parent_view = parent_view
        
        self.channel_id = TextInput(
            label="Channel ID",
            placeholder="กรอก ID ของ voice channel",
            required=True
        )
        self.add_item(self.channel_id)
        
        self.empty_name = TextInput(
            label="ชื่อเมื่อว่าง (Empty Name)",
            placeholder="ชื่อที่จะแสดงเมื่อไม่มีคนในห้อง",
            required=True
        )
        self.add_item(self.empty_name)
        
        self.occupied_name = TextInput(
            label="ชื่อเมื่อมีคน (Occupied Name)",
            placeholder="ชื่อที่จะแสดงเมื่อมีคนในห้อง",
            required=True
        )
        self.add_item(self.occupied_name)
    
    async def on_submit(self, interaction):
        """เมื่อส่งฟอร์ม"""
        try:
            channel_id = int(self.channel_id.value)
            empty_name = self.empty_name.value
            occupied_name = self.occupied_name.value
            
            # ตรวจสอบว่า channel มีอยู่จริง
            channel = interaction.guild.get_channel(channel_id)
            if not channel or not isinstance(channel, discord.VoiceChannel):
                await interaction.response.send_message("ไม่พบ voice channel ที่ระบุ", ephemeral=True)
                return
            
            # ตรวจสอบว่า channel นี้ถูกเพิ่มแล้วหรือไม่
            if str(channel_id) in self.config['voice_channels']:
                await interaction.response.send_message("Voice channel นี้ถูกเพิ่มแล้ว", ephemeral=True)
                return
            
            # เพิ่ม voice channel ใหม่
            self.config['voice_channels'][str(channel_id)] = {
                "empty_name": empty_name,
                "occupied_name": occupied_name
            }
            
            save_config(self.config)
            
            embed = discord.Embed(
                title="✅ เพิ่ม Voice Channel สำเร็จ",
                description=f"เพิ่ม <#{channel_id}> เรียบร้อยแล้ว\n• ชื่อเมื่อว่าง: `{empty_name}`\n• ชื่อเมื่อมีคน: `{occupied_name}`",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("Channel ID ต้องเป็นตัวเลขเท่านั้น", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"เกิดข้อผิดพลาด: {str(e)}", ephemeral=True)

class EditChannelSelectView(View):
    """View สำหรับเลือก Voice Channel ที่จะแก้ไข"""
    
    def __init__(self, user_id, config, parent_view):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.config = config
        self.parent_view = parent_view
        
        options = []
        for i, (channel_id, channel_data) in enumerate(config['voice_channels'].items()):
            options.append(discord.SelectOption(
                label=f"#{channel_id}",
                description=f"ว่าง: {channel_data['empty_name'][:50]}",
                value=channel_id
            ))
        
        select = Select(
            placeholder="เลือก voice channel ที่ต้องการแก้ไข",
            options=options
        )
        select.callback = self.select_channel
        self.add_item(select)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("คุณไม่สามารถใช้งานนี้ได้", ephemeral=True)
            return False
        return True
    
    async def select_channel(self, interaction):
        channel_id = interaction.data['values'][0]
        channel_data = self.config['voice_channels'][channel_id]
        
        await interaction.response.send_modal(
            EditChannelModal(self.user_id, self.config, self.parent_view, channel_id, channel_data)
        )

class EditChannelModal(Modal):
    """Modal สำหรับแก้ไข Voice Channel"""
    
    def __init__(self, user_id, config, parent_view, channel_id, channel_data):
        super().__init__(title="แก้ไข Voice Channel", timeout=300)
        self.user_id = user_id
        self.config = config
        self.parent_view = parent_view
        self.channel_id = channel_id
        self.channel_data = channel_data
        
        self.empty_name = TextInput(
            label="ชื่อเมื่อว่าง (Empty Name)",
            placeholder="ชื่อที่จะแสดงเมื่อไม่มีคนในห้อง (ใส่ 'skip' เพื่อข้าม)",
            default=channel_data['empty_name'],
            required=True
        )
        self.add_item(self.empty_name)
        
        self.occupied_name = TextInput(
            label="ชื่อเมื่อมีคน (Occupied Name)",
            placeholder="ชื่อที่จะแสดงเมื่อมีคนในห้อง (ใส่ 'skip' เพื่อข้าม)",
            default=channel_data['occupied_name'],
            required=True
        )
        self.add_item(self.occupied_name)
    
    async def on_submit(self, interaction):
        try:
            empty_name = self.empty_name.value
            occupied_name = self.occupied_name.value
            
            # อัปเดตข้อมูลเฉพาะฟิลด์ที่ไม่ใช่ 'skip'
            if empty_name.lower() != 'skip':
                self.config['voice_channels'][self.channel_id]['empty_name'] = empty_name
            
            if occupied_name.lower() != 'skip':
                self.config['voice_channels'][self.channel_id]['occupied_name'] = occupied_name
            
            save_config(self.config)
            
            updated_channel = self.config['voice_channels'][self.channel_id]
            embed = discord.Embed(
                title="✅ แก้ไข Voice Channel สำเร็จ",
                description=f"แก้ไข <#{self.channel_id}> เรียบร้อยแล้ว\n• ชื่อเมื่อว่าง: `{updated_channel['empty_name']}`\n• ชื่อเมื่อมีคน: `{updated_channel['occupied_name']}`",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"เกิดข้อผิดพลาด: {str(e)}", ephemeral=True)

class DeleteChannelSelectView(View):
    """View สำหรับเลือก Voice Channel ที่จะลบ"""
    
    def __init__(self, user_id, config, parent_view):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.config = config
        self.parent_view = parent_view
        
        options = []
        for i, (channel_id, channel_data) in enumerate(config['voice_channels'].items()):
            options.append(discord.SelectOption(
                label=f"#{channel_id}",
                description=f"ว่าง: {channel_data['empty_name'][:50]}",
                value=channel_id
            ))
        
        select = Select(
            placeholder="เลือก voice channel ที่ต้องการลบ",
            options=options
        )
        select.callback = self.select_channel
        self.add_item(select)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("คุณไม่สามารถใช้งานนี้ได้", ephemeral=True)
            return False
        return True
    
    async def select_channel(self, interaction):
        channel_id = interaction.data['values'][0]
        channel_data = self.config['voice_channels'][channel_id]
        
        await interaction.response.send_message(
            f"คุณต้องการลบ <#{channel_id}> หรือไม่?",
            view=DeleteConfirmView(self.user_id, self.config, self.parent_view, channel_id, channel_data),
            ephemeral=True
        )

class DeleteConfirmView(View):
    """View สำหรับยืนยันการลบ"""
    
    def __init__(self, user_id, config, parent_view, channel_id, channel_data):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.config = config
        self.parent_view = parent_view
        self.channel_id = channel_id
        self.channel_data = channel_data
        
        confirm_button = Button(
            label="✅ ยืนยันลบ",
            style=discord.ButtonStyle.red
        )
        confirm_button.callback = self.confirm_delete
        self.add_item(confirm_button)
        
        cancel_button = Button(
            label="❌ ยกเลิก",
            style=discord.ButtonStyle.grey
        )
        cancel_button.callback = self.cancel_delete
        self.add_item(cancel_button)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("คุณไม่สามารถใช้งานนี้ได้", ephemeral=True)
            return False
        return True
    
    async def confirm_delete(self, interaction):
        try:
            deleted_channel = self.config['voice_channels'].pop(self.channel_id)
            save_config(self.config)
            
            embed = discord.Embed(
                title="✅ ลบ Voice Channel สำเร็จ",
                description=f"ลบ <#{self.channel_id}> เรียบร้อยแล้ว",
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await interaction.response.send_message(f"เกิดข้อผิดพลาด: {str(e)}", ephemeral=True)
    
    async def cancel_delete(self, interaction):
        await interaction.response.edit_message(content="ยกเลิกการลบแล้ว", view=None)

class MusicPlayerView(View):
    """View สำหรับควบคุมเพลงพร้อมปุ่มต่างๆ"""
    
    def __init__(self, music_manager, guild_id: int):
        super().__init__(timeout=300)
        self.music_manager = music_manager
        self.guild_id = guild_id
        self.is_paused = False
        
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary, row=0)
    async def play_pause_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มเล่น/หยุดชั่วคราว"""
        if self.is_paused:
            success = await self.music_manager.resume_song(self.guild_id)
            if success:
                self.is_paused = False
                await interaction.response.send_message("▶️ เล่นเพลงต่อ", ephemeral=True)
            else:
                await interaction.response.send_message("❌ ไม่สามารถเล่นเพลงต่อได้", ephemeral=True)
        else:
            success = await self.music_manager.pause_song(self.guild_id)
            if success:
                self.is_paused = True
                await interaction.response.send_message("⏸️ หยุดเพลงชั่วคราว", ephemeral=True)
            else:
                await interaction.response.send_message("❌ ไม่มีเพลงที่เล่นอยู่", ephemeral=True)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, row=0)
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
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, row=0)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มหยุดเพลง"""
        await self.music_manager.stop_music(self.guild_id)
        await interaction.response.send_message("⏹️ หยุดเพลงและล้างคิวแล้ว", ephemeral=True)
    
    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary, row=0)
    async def shuffle_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มสลับเพลง"""
        queue = self.music_manager.get_music_queue(self.guild_id)
        
        if not queue.queue:
            await interaction.response.send_message("❌ ไม่มีเพลงในคิวให้สลับ", ephemeral=True)
            return
            
        queue.shuffle()
        await interaction.response.send_message(f"🔀 สลับเพลงในคิวแล้ว ({len(queue.queue)} เพลง)", ephemeral=True)
    
    @discord.ui.button(emoji="🔂", style=discord.ButtonStyle.secondary, row=0)
    async def loop_song_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มลูปเพลงปัจจุบัน"""
        queue = self.music_manager.get_music_queue(self.guild_id)
        
        if queue.loop:
            queue.loop = False
            button.style = discord.ButtonStyle.secondary
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("🔂 ปิดลูปเพลงปัจจุบัน", ephemeral=True)
        else:
            queue.loop = True
            queue.loop_queue = False
            button.style = discord.ButtonStyle.success
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("🔂 เปิดลูปเพลงปัจจุบัน", ephemeral=True)
    
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary, row=1)
    async def loop_queue_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มลูปคิว"""
        queue = self.music_manager.get_music_queue(self.guild_id)
        
        if queue.loop_queue:
            queue.loop_queue = False
            button.style = discord.ButtonStyle.secondary
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("🔁 ปิดลูปคิว", ephemeral=True)
        else:
            queue.loop_queue = True
            queue.loop = False
            button.style = discord.ButtonStyle.success
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("🔁 เปิดลูปคิว", ephemeral=True)
    
    @discord.ui.button(emoji="📋", style=discord.ButtonStyle.primary, row=1)
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
    
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.secondary, row=1)
    async def volume_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มควบคุมระดับเสียง"""
        view = VolumeControlView(self.music_manager, self.guild_id)
        await interaction.response.send_message("🔊 ใช้ปุ่มด้านล่างเพื่อปรับระดับเสียง", view=view, ephemeral=True)
    
    @discord.ui.button(emoji="👋", style=discord.ButtonStyle.danger, row=1)
    async def disconnect_button(self, interaction: discord.Interaction, button: Button):
        """ปุ่มออกจากห้องเสียง"""
        await self.music_manager.leave_voice_channel(self.guild_id)
        await interaction.response.send_message("👋 ออกจากห้องเสียงแล้ว", ephemeral=True)

class VolumeControlView(View):
    """View สำหรับควบคุมระดับเสียง"""
    
    def __init__(self, music_manager, guild_id: int, current_volume: int = 50):
        super().__init__(timeout=60)
        self.music_manager = music_manager
        self.guild_id = guild_id
        self.current_volume = current_volume
        
    @discord.ui.button(emoji="🔉", style=discord.ButtonStyle.secondary)
    async def volume_down(self, interaction: discord.Interaction, button: Button):
        """ลดระดับเสียง"""
        new_volume = max(0, self.current_volume - 10)
        success = self.music_manager.set_volume(self.guild_id, new_volume)
        if success:
            self.current_volume = new_volume
            await interaction.response.send_message(f"🔉 ระดับเสียง: {new_volume}%", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่สามารถปรับระดับเสียงได้", ephemeral=True)
            
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.secondary)
    async def volume_up(self, interaction: discord.Interaction, button: Button):
        """เพิ่มระดับเสียง"""
        new_volume = min(100, self.current_volume + 10)
        success = self.music_manager.set_volume(self.guild_id, new_volume)
        if success:
            self.current_volume = new_volume
            await interaction.response.send_message(f"🔊 ระดับเสียง: {new_volume}%", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่สามารถปรับระดับเสียงได้", ephemeral=True)
    
    @discord.ui.button(label="50%", style=discord.ButtonStyle.primary)
    async def volume_50(self, interaction: discord.Interaction, button: Button):
        """ตั้งระดับเสียง 50%"""
        success = self.music_manager.set_volume(self.guild_id, 50)
        if success:
            self.current_volume = 50
            await interaction.response.send_message("🔊 ระดับเสียง: 50%", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ไม่สามารถปรับระดับเสียงได้", ephemeral=True)

class QuickMusicView(View):
    """View สำหรับเล่นเพลงด่วน"""
    
    def __init__(self, music_manager, guild_id: int):
        super().__init__(timeout=300)
        self.music_manager = music_manager
        self.guild_id = guild_id
    
    @discord.ui.button(label="🎵 เล่นเพลงใหม่", style=discord.ButtonStyle.green, row=0)
    async def play_new_song(self, interaction: discord.Interaction, button: Button):
        """ปุ่มเล่นเพลงใหม่"""
        modal = PlaySongModal(self.music_manager, self.guild_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 ดูคิว", style=discord.ButtonStyle.primary, row=0)
    async def view_queue(self, interaction: discord.Interaction, button: Button):
        """ปุ่มดูคิว"""
        queue = self.music_manager.get_music_queue(self.guild_id)
        
        embed = discord.Embed(
            title="🎵 คิวเพลง",
            color=discord.Color.blue()
        )
        
        if queue.current_song:
            embed.add_field(
                name="🎵 กำลังเล่น",
                value=f"**{queue.current_song.title}**\n"
                      f"ระยะเวลา: {queue.current_song.duration}\n"
                      f"ขอโดย: {queue.current_song.requester.mention}",
                inline=False
            )
        
        if queue.queue:
            queue_text = ""
            for i, song in enumerate(queue.queue[:5], 1):
                queue_text += f"{i}. **{song.title}** ({song.duration})\n"
            
            if len(queue.queue) > 5:
                queue_text += f"\n... และอีก {len(queue.queue) - 5} เพลง"
                
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🎛️ ควบคุมเพลง", style=discord.ButtonStyle.secondary, row=0)
    async def music_controls(self, interaction: discord.Interaction, button: Button):
        """ปุ่มควบคุมเพลง"""
        view = MusicPlayerView(self.music_manager, self.guild_id)
        
        embed = discord.Embed(
            title="🎛️ ควบคุมเพลง",
            description="ใช้ปุ่มด้านล่างเพื่อควบคุมเพลง",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PlaySongModal(Modal):
    """Modal สำหรับใส่ชื่อเพลงหรือ URL"""
    
    def __init__(self, music_manager, guild_id: int):
        super().__init__(title="🎵 เล่นเพลงจาก YouTube")
        self.music_manager = music_manager
        self.guild_id = guild_id
        
        self.song_input = TextInput(
            label="ชื่อเพลงหรือ YouTube URL",
            placeholder="ใส่ชื่อเพลงหรือ URL ที่ต้องการเล่น...",
            style=discord.TextStyle.short,
            max_length=500,
            required=True
        )
        
        self.add_item(self.song_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """เมื่อผู้ใช้ submit modal"""
        search = self.song_input.value.strip()
        
        if not search:
            await interaction.response.send_message("❌ กรุณาใส่ชื่อเพลงหรือ URL", ephemeral=True)
            return
        
        # ตรวจสอบว่าผู้ใช้อยู่ในห้องเสียงหรือไม่
        if not interaction.user.voice:
            await interaction.response.send_message("❌ คุณต้องอยู่ในห้องเสียงก่อน", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # เข้าร่วมห้องเสียง
            voice_channel = interaction.user.voice.channel
            await self.music_manager.join_voice_channel(voice_channel)
            
            # เพิ่มเพลงในคิว
            song = await self.music_manager.add_to_queue(
                self.guild_id, search, interaction.user
            )
            
            queue = self.music_manager.get_music_queue(self.guild_id)
            voice_client = self.music_manager.get_voice_client(self.guild_id)
            
            # ถ้าไม่มีเพลงเล่นอยู่ ให้เริ่มเล่นทันที
            if not voice_client.is_playing() and not voice_client.is_paused():
                await self.music_manager.play_next(self.guild_id)
                
                embed = discord.Embed(
                    title="🎵 เริ่มเล่นเพลง",
                    description=f"**{song.title}**",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="✅ เพิ่มเพลงในคิวแล้ว",
                    description=f"**{song.title}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="ตำแหน่งในคิว", value=len(queue.queue), inline=True)
            
            embed.add_field(name="ระยะเวลา", value=song.duration, inline=True)
            embed.add_field(name="ขอโดย", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

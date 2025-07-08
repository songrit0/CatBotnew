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

import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# โหลดตัวแปรจาก .env
load_dotenv()

# โหลดการตั้งค่าจาก config.json
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# บันทึกการตั้งค่าไปยัง config.json
def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

config = load_config()

# ตัวแปรสำหรับจัดการ Rate Limiting
last_channel_update = {}  # เก็บเวลาการอัพเดตครั้งล่าสุดของแต่ละห้อง
channel_update_queue = {}  # คิวสำหรับการอัพเดตห้อง

# ตั้งค่า intents
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.message_content = True  # เพิ่มเพื่อให้บอทอ่านข้อความและคำสั่งได้

# สร้าง bot instance
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)  # ปิดใช้งาน help command เดิม

@bot.event
async def on_ready():
    print(f'{bot.user} ได้เชื่อมต่อแล้ว!')
    print(f'Bot ID: {bot.user.id}')
    print(f'กำลังติดตาม {len(config["voice_channels"])} ห้องเสียง')
    
    # เริ่มต้นระบบประมวลผลคิว
    bot.loop.create_task(process_update_queue())
    print("⏰ เริ่มต้นระบบจัดการคิวการอัพเดต (เฉพาะผู้ได้รับอนุญาต)")
    
    # ตรวจสอบห้องเสียงทั้งหมด
    for channel_id, settings in config["voice_channels"].items():
        channel = bot.get_channel(int(channel_id))
        if channel:
            human_count = sum(1 for member in channel.members if not member.bot)
            print(f"🔊 ห้อง: {channel.name} (ID: {channel_id})")
            print(f"   คนในห้อง: {human_count} คน")
            print(f"   ชื่อเมื่อว่าง: {settings['empty_name']}")
            print(f"   ชื่อเมื่อมีคน: {settings['occupied_name']}")
            
            # ไม่อัพเดตชื่อห้องเริ่มต้น เพื่อหลีกเลี่ยง Rate Limiting
            print(f"   ไม่อัพเดตชื่อห้องเริ่มต้นเพื่อหลีกเลี่ยง Rate Limiting")
        else:
            print(f"❌ ไม่พบห้อง ID: {channel_id}")
    
    print("🤖 บอทพร้อมใช้งาน!")

@bot.event
async def on_voice_state_update(member, before, after):
    """
    เมื่อมีการเปลี่ยนแปลงสถานะในห้องเสียง
    """
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
    for channel in channels_to_check:
        current_config = load_config()  # โหลด config ใหม่
        channel_id = str(channel.id)
        if channel_id in current_config["voice_channels"]:
            print(f"🔧 กำลังตรวจสอบห้อง: {channel.name}")
            await update_voice_channel_name(channel, member.guild)
        else:
            print(f"ℹ️ ห้อง {channel.name} ไม่ได้อยู่ในการตั้งค่า")

async def update_voice_channel_name(channel, guild=None):
    """
    อัพเดตชื่อห้องเสียงตามจำนวนคนที่อยู่ในห้อง
    """
    current_config = load_config()  # โหลด config ใหม่ทุกครั้ง
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
    now = datetime.now()
    channel_key = str(channel.id)
    
    if channel_key in last_channel_update:
        time_diff = now - last_channel_update[channel_key]
        if time_diff < timedelta(minutes=5):  # รอ 5 นาที
            remaining_time = timedelta(minutes=5) - time_diff
            remaining_seconds = int(remaining_time.total_seconds())
            remaining_minutes = remaining_seconds // 60
            remaining_sec = remaining_seconds % 60
            
            print(f"⏳ ต้องรอ {remaining_seconds} วินาที ก่อนเปลี่ยนชื่อห้องอีกครั้ง")
            
            # ส่งข้อความแจ้งเตือนในแชท
            if guild:
                try:
                    # ใช้ห้องแชทที่ระบุใน config หรือห้องแรกที่บอทเข้าถึงได้
                    text_channel = None
                    
                    # ตรวจสอบว่ามีการตั้งค่าห้องแชทใน config หรือไม่
                    if "notification_channel" in current_config:
                        text_channel = bot.get_channel(int(current_config["notification_channel"]))
                        if text_channel and not text_channel.permissions_for(guild.me).send_messages:
                            text_channel = None
                    
                    # ถ้าไม่มีห้องที่ระบุหรือไม่มีสิทธิ์ ให้หาห้องแรกที่เข้าถึงได้
                    if not text_channel:
                        for ch in guild.text_channels:
                            if ch.permissions_for(guild.me).send_messages:
                                text_channel = ch
                                break
                    
                    if text_channel:
                        embed = discord.Embed(
                            title="⏳ การเปลี่ยนชื่อห้องเสียงถูกจำกัด",
                            description=f"Discord จำกัดการเปลี่ยนชื่อห้องเสียงเป็น 2 ครั้งต่อ 10 นาที",
                            color=discord.Color.orange()
                        )
                        embed.add_field(
                            name="🔊 ห้องเสียง",
                            value=f"{channel.name}",
                            inline=True
                        )
                        embed.add_field(
                            name="🎯 จะเปลี่ยนเป็น",
                            value=f"{new_name}",
                            inline=True
                        )
                        # คำนวณเวลาที่จะอัพเดต
                        update_time = now + remaining_time
                        timestamp = int(update_time.timestamp())
                        
                        embed.add_field(
                            name="⏰ เหลือเวลา",
                            value=f"<t:{timestamp}:R>",
                            inline=True
                        )
                        embed.set_footer(text="บอทจะเปลี่ยนชื่อห้องโดยอัตโนมัติเมื่อถึงเวลา")
                        
                        await text_channel.send(embed=embed)
                        print(f"📢 ส่งข้อความแจ้งเตือนในแชท {text_channel.name}")
                        
                except Exception as e:
                    print(f"❌ ไม่สามารถส่งข้อความแจ้งเตือนได้: {e}")
            
            # เก็บคิวสำหรับการอัพเดตทีหลัง
            channel_update_queue[channel_key] = {
                'channel': channel,
                'new_name': new_name,
                'scheduled_time': now + timedelta(minutes=5, seconds=10),
                'guild': guild
            }
            print(f"📋 เพิ่มในคิว: จะเปลี่ยนชื่อเป็น '{new_name}' ในอีก {remaining_seconds + 10} วินาที")
            print("─" * 50)
            return
    
    # อัพเดตชื่อห้อง
    try:
        print(f"🔧 กำลังเปลี่ยนชื่อจาก '{channel.name}' เป็น '{new_name}'...")
        await channel.edit(name=new_name)
        last_channel_update[channel_key] = now
        print(f"✅ อัพเดตชื่อห้องเสร็จสิ้น: {new_name}")
        
        # ส่งข้อความแจ้งเตือนว่าเปลี่ยนชื่อสำเร็จ
        if guild:
            try:
                text_channel = None
                
                # ใช้ห้องแชทที่ระบุใน config หรือห้องแรกที่บอทเข้าถึงได้
                if "notification_channel" in current_config:
                    text_channel = bot.get_channel(int(current_config["notification_channel"]))
                    if text_channel and not text_channel.permissions_for(guild.me).send_messages:
                        text_channel = None
                
                # ถ้าไม่มีห้องที่ระบุหรือไม่มีสิทธิ์ ให้หาห้องแรกที่เข้าถึงได้
                if not text_channel:
                    for ch in guild.text_channels:
                        if ch.permissions_for(guild.me).send_messages:
                            text_channel = ch
                            break
                
                if text_channel:
                    embed = discord.Embed(
                        title="✅ เปลี่ยนชื่อห้องเสียงสำเร็จ",
                        description=f"ห้องเสียงถูกเปลี่ยนชื่อเรียบร้อยแล้ว",
                        color=discord.Color.green()
                    )
                    embed.add_field(
                        name="🔊 ห้องเสียง",
                        value=f"{channel.name}",
                        inline=True
                    )
                    embed.add_field(
                        name="👥 จำนวนคน",
                        value=f"{human_count} คน",
                        inline=True
                    )
                    
                    await text_channel.send(embed=embed)
                    print(f"📢 ส่งข้อความแจ้งเตือนการเปลี่ยนชื่อสำเร็จ")
                    
            except Exception as e:
                print(f"❌ ไม่สามารถส่งข้อความแจ้งเตือนได้: {e}")
                
    except discord.Forbidden:
        print(f"❌ ไม่มีสิทธิ์เปลี่ยนชื่อห้อง {channel.name}")
    except discord.HTTPException as e:
        if e.status == 429:  # Rate limited
            print(f"⚠️ ถูก Rate Limited โดย Discord API")
            print(f"   จะลองอีกครั้งในภายหลัง...")
            # เก็บคิวสำหรับการอัพเดตทีหลัง
            channel_update_queue[channel_key] = {
                'channel': channel,
                'new_name': new_name,
                'scheduled_time': now + timedelta(minutes=5, seconds=10),
                'guild': guild
            }
        else:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดไม่ทราบสาเหตุ: {e}")
    
    print("─" * 50)

def is_authorized(ctx):
    """
    ตรวจสอบว่าผู้ใช้มีสิทธิ์ใช้คำสั่งระบบจัดการคิวหรือไม่
    เฉพาะ Administrator เท่านั้น
    """
    # ตรวจสอบว่าเป็นเจ้าของบอท
    if ctx.author.id == ctx.bot.owner_id:
        return True
    
    # ตรวจสอบสิทธิ์ Administrator
    if ctx.author.guild_permissions.administrator:
        return True
    
    return False

async def process_update_queue():
    """
    ประมวลผลคิวการอัพเดตห้องเสียง
    """
    while True:
        try:
            now = datetime.now()
            to_remove = []
            
            for channel_key, update_info in channel_update_queue.items():
                if now >= update_info['scheduled_time']:
                    channel = update_info['channel']
                    new_name = update_info['new_name']
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
                            last_channel_update[channel_key] = now
                            print(f"✅ อัพเดตจากคิว: {correct_name}")
                            
                            # ส่งข้อความแจ้งเตือนว่าเปลี่ยนชื่อสำเร็จจากคิว
                            if guild:
                                try:
                                    text_channel = None
                                    
                                    # ใช้ห้องแชทที่ระบุใน config หรือห้องแรกที่บอทเข้าถึงได้
                                    if "notification_channel" in current_config:
                                        text_channel = bot.get_channel(int(current_config["notification_channel"]))
                                        if text_channel and not text_channel.permissions_for(guild.me).send_messages:
                                            text_channel = None
                                    
                                    # ถ้าไม่มีห้องที่ระบุหรือไม่มีสิทธิ์ ให้หาห้องแรกที่เข้าถึงได้
                                    if not text_channel:
                                        for ch in guild.text_channels:
                                            if ch.permissions_for(guild.me).send_messages:
                                                text_channel = ch
                                                break
                                    
                                    if text_channel:
                                        embed = discord.Embed(
                                            title="✅ เปลี่ยนชื่อห้องเสียงสำเร็จ (จากคิว)",
                                            description=f"ห้องเสียงถูกเปลี่ยนชื่อจากคิวเรียบร้อยแล้ว",
                                            color=discord.Color.green()
                                        )
                                        embed.add_field(
                                            name="🔊 ห้องเสียง",
                                            value=f"{channel.name}",
                                            inline=True
                                        )
                                        embed.add_field(
                                            name="👥 จำนวนคน",
                                            value=f"{human_count} คน",
                                            inline=True
                                        )
                                        
                                        await text_channel.send(embed=embed)
                                        print(f"📢 ส่งข้อความแจ้งเตือนการเปลี่ยนชื่อสำเร็จจากคิว")
                                        
                                except Exception as e:
                                    print(f"❌ ไม่สามารถส่งข้อความแจ้งเตือนได้: {e}")
                                    
                        except Exception as e:
                            print(f"❌ อัพเดตจากคิวล้มเหลว: {e}")
                    
                    to_remove.append(channel_key)
            
            # ลบรายการที่ประมวลผลแล้ว
            for key in to_remove:
                del channel_update_queue[key]
            
            await asyncio.sleep(30)  # ตรวจสอบทุก 30 วินาที
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการประมวลผลคิว: {e}")
            await asyncio.sleep(30)

@bot.command(name='queue')
async def show_queue(ctx):
    """
    แสดงคิวการอัพเดตห้องเสียง (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
        await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
        return
    
    if not channel_update_queue:
        await ctx.send("📋 ไม่มีการอัพเดตในคิว")
        return
    
    embed = discord.Embed(
        title="📋 คิวการอัพเดตห้องเสียง",
        description="รายการห้องที่รอการอัพเดต",
        color=discord.Color.yellow()
    )
    
    for channel_key, update_info in channel_update_queue.items():
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

@bot.command(name='forcenow')
@commands.has_permissions(manage_channels=True)
async def force_update_now(ctx, channel_id: str = None):
    """
    บังคับอัพเดตห้องเสียงทันที (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config และ Administrator)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
        await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
        return
    if channel_id is None:
        await ctx.send("❌ กรุณาระบุ Channel ID")
        return
    
    channel = bot.get_channel(int(channel_id))
    if not channel:
        await ctx.send(f"❌ ไม่พบห้อง ID: {channel_id}")
        return
    
    current_config = load_config()  # โหลด config ใหม่
    
    # ลบจากคิวถ้ามี
    if channel_id in channel_update_queue:
        del channel_update_queue[channel_id]
    
    # อัพเดตทันที
    human_count = sum(1 for member in channel.members if not member.bot)
    if human_count > 0:
        new_name = current_config["voice_channels"][channel_id]["occupied_name"]
    else:
        new_name = current_config["voice_channels"][channel_id]["empty_name"]
    
    try:
        await channel.edit(name=new_name)
        last_channel_update[channel_id] = datetime.now()
        await ctx.send(f"✅ อัพเดตห้อง {channel.name} เป็น '{new_name}' เสร็จสิ้น")
    except Exception as e:
        await ctx.send(f"❌ ไม่สามารถอัพเดตได้: {e}")

@bot.command(name='debug')
async def debug_channels(ctx):
    """
    คำสั่งสำหรับ debug ปัญหา (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
        await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
        return
    
    embed = discord.Embed(
        title="🔍 Debug Information",
        description="ข้อมูลการ debug",
        color=discord.Color.orange()
    )
    
    # แสดงข้อมูลการตั้งค่า
    current_config = load_config()  # โหลด config ใหม่
    config_info = []
    for channel_id, settings in current_config["voice_channels"].items():
        channel = bot.get_channel(int(channel_id))
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
    queue_info = []
    if channel_update_queue:
        queue_info.append(f"จำนวนคิว: {len(channel_update_queue)}")
        for channel_key, update_info in channel_update_queue.items():
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

@bot.command(name='test')
async def test_update(ctx, channel_id: str = None):
    """
    ทดสอบการอัพเดตห้องเสียงด้วยตนเอง (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
        await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
        return
    
    current_config = load_config()  # โหลด config ใหม่
    if channel_id is None:
        # ใช้ห้องแรกในการตั้งค่า
        channel_id = list(current_config["voice_channels"].keys())[0]
    
    channel = bot.get_channel(int(channel_id))
    if not channel:
        await ctx.send(f"❌ ไม่พบห้อง ID: {channel_id}")
        return
    
    await ctx.send(f"🔄 กำลังทดสอบอัพเดตห้อง {channel.name}...")
    await update_voice_channel_name(channel)
    await ctx.send("✅ ทดสอบเสร็จสิ้น")

@bot.command(name='check')
async def check_channels(ctx):
    """
    คำสั่งตรวจสอบสถานะห้องเสียงทั้งหมด (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
        await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
        return
    
    current_config = load_config()  # โหลด config ใหม่
    embed = discord.Embed(
        title="สถานะห้องเสียง",
        description="ข้อมูลห้องเสียงที่กำลังติดตาม",
        color=discord.Color.blue()
    )
    
    for channel_id, settings in current_config["voice_channels"].items():
        channel = bot.get_channel(int(channel_id))
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

@bot.command(name='update')
@commands.has_permissions(manage_channels=True)
async def force_update(ctx):
    """
    บังคับอัพเดตชื่อห้องเสียงทั้งหมด (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config และ Administrator)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
        await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
        return
    
    current_config = load_config()  # โหลด config ใหม่
    updated_count = 0
    for channel_id in current_config["voice_channels"].keys():
        channel = bot.get_channel(int(channel_id))
        if channel:
            await update_voice_channel_name(channel)
            updated_count += 1
    
    await ctx.send(f"✅ อัพเดตห้องเสียงเสร็จสิ้น ({updated_count} ห้อง)")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้")
    elif isinstance(error, commands.CommandNotFound):
        pass  # ไม่แสดงข้อผิดพลาดสำหรับคำสั่งที่ไม่พบ
    else:
        print(f"Error: {error}")

@bot.command(name='listauth')
async def list_authorized(ctx):
    """
    แสดงข้อมูลสิทธิ์การใช้คำสั่ง (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
        await ctx.send("❌ คำสั่งนี้ใช้ได้เฉพาะในห้องที่กำหนดเท่านั้น")
        return
    
    # ตรวจสอบว่าคำสั่งถูกใช้ในเซิร์ฟเวอร์
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
        value="👥 ทุกคนในห้องนี้\n� ไม่จำเป็นต้องเป็น Administrator",
        inline=False
    )
    
    embed.set_footer(text="ระบบเปิดให้ทุกคนใช้งานในห้องนี้")
    await ctx.send(embed=embed)

@bot.command(name='showroom')
async def show_room_info(ctx):
    """
    แสดงข้อมูลห้องเสียงที่กำหนดใน config
    """
    current_config = load_config()
    target_channel_id = current_config.get("command_channel")
    
    if not target_channel_id:
        await ctx.send("❌ ไม่ได้กำหนดห้องคำสั่งใน config")
        return
        
    channel = bot.get_channel(int(target_channel_id))
    
    if not channel:
        await ctx.send(f"❌ ไม่พบห้อง ID: {target_channel_id}")
        return
    
    # นับจำนวนคนที่ไม่ใช่บอท
    human_count = sum(1 for member in channel.members if not member.bot)
    total_members = len(channel.members)
    
    # แสดงรายชื่อสมาชิกในห้อง
    members_info = []
    bots_info = []
    
    for member in channel.members:
        if member.bot:
            bots_info.append(f"🤖 {member.display_name}")
        else:
            members_info.append(f"👤 {member.display_name}")
    
    embed = discord.Embed(
        title=f"🔊 ข้อมูลห้องเสียง: {channel.name}",
        description=f"ID: `{target_channel_id}`",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📊 สถิติ",
        value=f"คนทั้งหมด: **{total_members}** คน\n"
              f"คนจริง: **{human_count}** คน\n"
              f"บอท: **{total_members - human_count}** ตัว",
        inline=False
    )
    
    if members_info:
        embed.add_field(
            name="👥 สมาชิกในห้อง",
            value="\n".join(members_info),
            inline=True
        )
    else:
        embed.add_field(
            name="👥 สมาชิกในห้อง",
            value="ไม่มีใครในห้อง",
            inline=True
        )
    
    if bots_info:
        embed.add_field(
            name="🤖 บอทในห้อง",
            value="\n".join(bots_info),
            inline=True
        )
    
    # แสดงการตั้งค่าจาก config
    current_config = load_config()
    if target_channel_id in current_config["voice_channels"]:
        settings = current_config["voice_channels"][target_channel_id]
        embed.add_field(
            name="⚙️ การตั้งค่า",
            value=f"ชื่อเมื่อว่าง: `{settings['empty_name']}`\n"
                  f"ชื่อเมื่อมีคน: `{settings['occupied_name']}`",
            inline=False
        )
    
    # แสดงข้อมูลสิทธิ์ของห้อง
    permissions = channel.permissions_for(ctx.guild.me)
    embed.add_field(
        name="🔐 สิทธิ์บอท",
        value=f"จัดการช่อง: {'✅' if permissions.manage_channels else '❌'}\n"
              f"ส่งข้อความ: {'✅' if permissions.send_messages else '❌'}\n"
              f"เข้าร่วมเสียง: {'✅' if permissions.connect else '❌'}",
        inline=False
    )
    
    embed.set_footer(text=f"ขอข้อมูลโดย: {ctx.author.display_name}")
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)

@bot.command(name='info')
async def show_info(ctx):
    """
    แสดงข้อมูลห้องเสียง (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
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
        channel = bot.get_channel(int(channel_id))
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
    if channel_update_queue:
        queue_info = []
        for channel_key, update_info in channel_update_queue.items():
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

@bot.command(name='status')
async def show_status(ctx):
    """
    แสดงสถานะบอทและระบบ (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
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
        value=f"**ชื่อบอท:** {bot.user.name}\n**ID:** {bot.user.id}\n**Latency:** {round(bot.latency * 1000)}ms",
        inline=True
    )
    
    # จำนวนเซิร์ฟเวอร์และสมาชิก
    embed.add_field(
        name="🌐 การเชื่อมต่อ",
        value=f"**เซิร์ฟเวอร์:** {len(bot.guilds)} เซิร์ฟเวอร์\n**สมาชิก:** {sum(guild.member_count for guild in bot.guilds)} คน",
        inline=True
    )
    
    # ข้อมูลห้องเสียง
    voice_channels_count = len(current_config["voice_channels"])
    embed.add_field(
        name="🔊 ห้องเสียง",
        value=f"**กำลังติดตาม:** {voice_channels_count} ห้อง\n**คิวการอัพเดต:** {len(channel_update_queue)} รายการ",
        inline=True
    )
    
    # ข้อมูลการอัพเดตล่าสุด
    if last_channel_update:
        latest_update = max(last_channel_update.values())
        time_since_update = datetime.now() - latest_update
        minutes_ago = int(time_since_update.total_seconds() // 60)
        
        embed.add_field(
            name="⏰ การอัพเดตล่าสุด",
            value=f"**เมื่อ:** {minutes_ago} นาทีที่แล้ว",
            inline=True
        )
    
    embed.set_footer(text="บอททำงานปกติ")
    await ctx.send(embed=embed)

@bot.command(name='help')
async def show_help(ctx):
    """
    แสดงคำสั่งที่ใช้ได้ (ใช้ได้เฉพาะในห้องคำสั่งที่กำหนดใน config)
    """
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
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
        label="📊 Info (ข้อมูล)", 
        style=discord.ButtonStyle.primary,
        custom_id="cmd_info"
    )
    status_button = discord.ui.Button(
        label="🤖 Status (สถานะ)", 
        style=discord.ButtonStyle.primary,
        custom_id="cmd_status"
    )
    queue_button = discord.ui.Button(
        label="📋 Queue (คิว)", 
        style=discord.ButtonStyle.secondary,
        custom_id="cmd_queue"
    )
    check_button = discord.ui.Button(
        label="🔍 Check (ตรวจสอบ)", 
        style=discord.ButtonStyle.secondary,
        custom_id="cmd_check"
    )
    debug_button = discord.ui.Button(
        label="🔧 Debug (ดีบัก)", 
        style=discord.ButtonStyle.secondary,
        custom_id="cmd_debug"
    )
    
    # แถวที่ 2 - คำสั่งเพิ่มเติม
    test_button = discord.ui.Button(
        label="🧪 Test (ทดสอบ)", 
        style=discord.ButtonStyle.secondary,
        custom_id="cmd_test"
    )
    listauth_button = discord.ui.Button(
        label="👥 List Auth (สิทธิ์)", 
        style=discord.ButtonStyle.secondary,
        custom_id="cmd_listauth"
    )
    manage_button = discord.ui.Button(
        label="⚙️ Manage (จัดการ)", 
        style=discord.ButtonStyle.success,
        custom_id="cmd_manage"
    )
    
    # เพิ่มการตอบสนองเมื่อกดปุ่ม
    async def button_callback(interaction):
        # ตรวจสอบว่าผู้กดปุ่มเป็นคนเดียวกับที่ใช้คำสั่ง
        if interaction.user != ctx.author:
            await interaction.response.send_message("❌ คุณไม่สามารถใช้ปุ่มนี้ได้", ephemeral=True)
            return
            
        command_map = {
            "cmd_info": "!info",
            "cmd_status": "!status", 
            "cmd_queue": "!queue",
            "cmd_check": "!check",
            "cmd_debug": "!debug",
            "cmd_test": "!test",
            "cmd_listauth": "!listauth",
            "cmd_manage": "!manage"
        }
        
        command = command_map.get(interaction.data['custom_id'])
        if command:
            await interaction.response.send_message(f"🔄 กำลังเรียกใช้คำสั่ง `{command}`...", ephemeral=True)
            
            # เรียกใช้คำสั่งตามปุ่มที่กด
            if command == "!info":
                await show_info(ctx)
            elif command == "!status":
                await show_status(ctx)
            elif command == "!queue":
                await show_queue(ctx)
            elif command == "!check":
                await check_channels(ctx)
            elif command == "!debug":
                await debug_channels(ctx)
            elif command == "!test":
                await test_update(ctx)
            elif command == "!listauth":
                await list_authorized(ctx)
            elif command == "!manage":
                await manage_voice_channels(ctx)
    
    # กำหนด callback ให้ปุ่มทั้งหมด
    info_button.callback = button_callback
    status_button.callback = button_callback
    queue_button.callback = button_callback
    check_button.callback = button_callback
    debug_button.callback = button_callback
    test_button.callback = button_callback
    listauth_button.callback = button_callback
    manage_button.callback = button_callback
    
    # เพิ่มปุ่มใน view
    view.add_item(info_button)
    view.add_item(status_button)
    view.add_item(queue_button)
    view.add_item(check_button)
    view.add_item(debug_button)
    view.add_item(test_button)
    view.add_item(listauth_button)
    view.add_item(manage_button)
    
    await ctx.send(embed=embed, view=view)

# คำสั่งพิเศษสำหรับห้องที่กำหนดใน config เท่านั้น
def is_special_channel(ctx):
    """
    ตรวจสอบว่าคำสั่งถูกใช้ในห้องพิเศษหรือไม่
    """
    current_config = load_config()
    command_channel_id = current_config.get("command_channel")
    if command_channel_id:
        return ctx.channel.id == int(command_channel_id)
    return False

# View สำหรับจัดการ voice channels
class VoiceChannelManagerView(discord.ui.View):
    def __init__(self, user_id, config):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.config = config
        self.update_buttons()
    
    def update_buttons(self):
        self.clear_items()
        
        # ปุ่มสำหรับดูรายการ voice channels
        list_button = discord.ui.Button(
            label="📋 ดูรายการ (List)",
            style=discord.ButtonStyle.primary
        )
        list_button.callback = self.list_channels
        self.add_item(list_button)
        
        # ปุ่มสำหรับเพิ่ม voice channel ใหม่
        add_button = discord.ui.Button(
            label="➕ เพิ่มใหม่ (Add)",
            style=discord.ButtonStyle.green
        )
        add_button.callback = self.add_channel
        self.add_item(add_button)
        
        # ปุ่มสำหรับแก้ไข voice channel
        edit_button = discord.ui.Button(
            label="✏️ แก้ไข (Edit)",
            style=discord.ButtonStyle.secondary
        )
        edit_button.callback = self.edit_channel
        self.add_item(edit_button)
        
        # ปุ่มสำหรับลบ voice channel
        delete_button = discord.ui.Button(
            label="🗑️ ลบ (Delete)",
            style=discord.ButtonStyle.red
        )
        delete_button.callback = self.delete_channel
        self.add_item(delete_button)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("คุณไม่สามารถใช้งานปุ่มนี้ได้", ephemeral=True)
            return False
        return True
    
    async def list_channels(self, interaction):
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
        await interaction.response.send_modal(AddChannelModal(self.user_id, self.config, self))
    
    async def edit_channel(self, interaction):
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

# Modal สำหรับเพิ่ม voice channel ใหม่
class AddChannelModal(discord.ui.Modal):
    def __init__(self, user_id, config, parent_view):
        super().__init__(title="เพิ่ม Voice Channel ใหม่", timeout=300)
        self.user_id = user_id
        self.config = config
        self.parent_view = parent_view
        
        self.channel_id = discord.ui.TextInput(
            label="Channel ID",
            placeholder="กรอก ID ของ voice channel",
            required=True
        )
        self.add_item(self.channel_id)
        
        self.empty_name = discord.ui.TextInput(
            label="ชื่อเมื่อว่าง (Empty Name)",
            placeholder="ชื่อที่จะแสดงเมื่อไม่มีคนในห้อง",
            required=True
        )
        self.add_item(self.empty_name)
        
        self.occupied_name = discord.ui.TextInput(
            label="ชื่อเมื่อมีคน (Occupied Name)",
            placeholder="ชื่อที่จะแสดงเมื่อมีคนในห้อง",
            required=True
        )
        self.add_item(self.occupied_name)
    
    async def on_submit(self, interaction):
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

# Select view สำหรับแก้ไข voice channel
class EditChannelSelectView(discord.ui.View):
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
        
        select = discord.ui.Select(
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

# Modal สำหรับแก้ไข voice channel
class EditChannelModal(discord.ui.Modal):
    def __init__(self, user_id, config, parent_view, channel_id, channel_data):
        super().__init__(title="แก้ไข Voice Channel", timeout=300)
        self.user_id = user_id
        self.config = config
        self.parent_view = parent_view
        self.channel_id = channel_id
        self.channel_data = channel_data
        
        self.empty_name = discord.ui.TextInput(
            label="ชื่อเมื่อว่าง (Empty Name)",
            placeholder="ชื่อที่จะแสดงเมื่อไม่มีคนในห้อง (ใส่ 'skip' เพื่อข้าม)",
            default=channel_data['empty_name'],
            required=True
        )
        self.add_item(self.empty_name)
        
        self.occupied_name = discord.ui.TextInput(
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

# Select view สำหรับลบ voice channel
class DeleteChannelSelectView(discord.ui.View):
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
        
        select = discord.ui.Select(
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

# View สำหรับยืนยันการลบ
class DeleteConfirmView(discord.ui.View):
    def __init__(self, user_id, config, parent_view, channel_id, channel_data):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.config = config
        self.parent_view = parent_view
        self.channel_id = channel_id
        self.channel_data = channel_data
        
        confirm_button = discord.ui.Button(
            label="✅ ยืนยันลบ",
            style=discord.ButtonStyle.red
        )
        confirm_button.callback = self.confirm_delete
        self.add_item(confirm_button)
        
        cancel_button = discord.ui.Button(
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

@bot.command(name='manage', help='จัดการ voice channels')
async def manage_voice_channels(ctx):
    # ตรวจสอบว่าคำสั่งถูกใช้ในห้องที่ถูกต้อง
    if not is_special_channel(ctx):
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

# รันบอท
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ ไม่พบ DISCORD_TOKEN ในไฟล์ .env")
        exit(1)
    
    print("🚀 กำลังเริ่มต้นบอท...")
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ ไม่สามารถเริ่มต้นบอทได้: {e}")

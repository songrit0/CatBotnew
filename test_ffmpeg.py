"""
ไฟล์ทดสอบ FFmpeg สำหรับ Discord.py
"""
import discord
import os
import subprocess

def test_ffmpeg():
    """ทดสอบการทำงานของ FFmpeg"""
    print("🔍 ทดสอบ FFmpeg...")
    
    # ทดสอบ 1: ใน PATH
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg พบใน PATH")
            return True
    except Exception as e:
        print(f"❌ FFmpeg ไม่พบใน PATH: {e}")
    
    # ทดสอบ 2: ใน WinGet Links
    winget_path = r"C:\Users\MARU\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"
    if os.path.exists(winget_path):
        try:
            result = subprocess.run([winget_path, '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ FFmpeg พบใน: {winget_path}")
                return winget_path
        except Exception as e:
            print(f"❌ ไม่สามารถรัน FFmpeg: {e}")
    
    print("❌ ไม่พบ FFmpeg")
    return False

def test_discord_ffmpeg():
    """ทดสอบ Discord FFmpeg"""
    try:
        # ทดสอบโดยไม่ระบุ executable
        options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        
        source = discord.FFmpegPCMAudio("test.wav", **options)
        print("✅ Discord FFmpeg ทำงานได้ (ไม่ระบุ executable)")
        return True
        
    except Exception as e:
        print(f"❌ Discord FFmpeg ล้มเหลว: {e}")
        
        # ทดสอบโดยระบุ executable
        try:
            options_with_exe = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
                'executable': r'C:\Users\MARU\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe'
            }
            
            source = discord.FFmpegPCMAudio("test.wav", **options_with_exe)
            print("✅ Discord FFmpeg ทำงานได้ (ระบุ executable)")
            return True
            
        except Exception as e2:
            print(f"❌ Discord FFmpeg ล้มเหลวแม้ระบุ executable: {e2}")
            return False

if __name__ == "__main__":
    print("🧪 ทดสอบระบบ FFmpeg สำหรับ Discord.py")
    print("=" * 50)
    
    # ทดสอบ FFmpeg
    ffmpeg_result = test_ffmpeg()
    
    print("\n" + "=" * 50)
    
    # ทดสอบ Discord FFmpeg
    discord_result = test_discord_ffmpeg()
    
    print("\n" + "=" * 50)
    
    if ffmpeg_result and discord_result:
        print("🎉 ระบบพร้อมเล่นเพลง!")
    else:
        print("⚠️ ระบบยังไม่พร้อม ต้องแก้ไขปัญหา FFmpeg")
        
        # แนะนำการแก้ไข
        print("\n💡 วิธีแก้ไข:")
        print("1. ตรวจสอบว่า FFmpeg ติดตั้งแล้ว")
        print("2. เพิ่ม FFmpeg path ใน environment variables")
        print("3. รีสตาร์ท PowerShell/Terminal")
        print("4. ทดสอบด้วย: ffmpeg -version")

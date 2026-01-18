
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
目录设置和检查脚本
确保正确的目录结构：srt/用于字幕，videos/用于视频
"""

import os

def setup_directories():
    """设置必要的目录结构"""
    directories = {
        'srt': '字幕文件目录 (.srt文件)',
        'videos': '视频文件目录 (.mp4, .mkv等)',
        'intelligent_clips': '智能剪辑输出目录'
    }
    
    print("📁 设置目录结构...")
    print("="*50)
    
    for dir_name, description in directories.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/ - {description}")
        else:
            print(f"✓ 目录已存在: {dir_name}/ - {description}")
    
    print("\n📋 使用说明：")
    print("1. 将字幕文件(.srt)放入 srt/ 目录")
    print("2. 将对应视频文件放入 videos/ 目录") 
    print("3. 运行 python main.py 选择高级智能剪辑")
    print("4. 输出的短视频会保存在 intelligent_clips/ 目录")
    
    # 检查现有文件
    srt_files = [f for f in os.listdir('srt') if f.endswith('.srt')] if os.path.exists('srt') else []
    video_files = [f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))] if os.path.exists('videos') else []
    
    print(f"\n📊 当前状态：")
    print(f"• 字幕文件: {len(srt_files)} 个")
    print(f"• 视频文件: {len(video_files)} 个")
    
    if srt_files and video_files:
        print("✅ 文件准备就绪，可以开始智能剪辑！")
    elif not srt_files:
        print("⚠️ 请将字幕文件放入 srt/ 目录")
    elif not video_files:
        print("⚠️ 请将视频文件放入 videos/ 目录")

if __name__ == "__main__":
    setup_directories()

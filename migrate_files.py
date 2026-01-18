
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件迁移脚本 - 将字幕文件移动到srt目录
"""

import os
import shutil

def migrate_subtitle_files():
    """将字幕文件移动到srt目录"""
    print("🔄 开始迁移字幕文件到srt目录...")
    
    # 创建srt目录
    srt_dir = 'srt'
    if not os.path.exists(srt_dir):
        os.makedirs(srt_dir)
        print(f"✓ 创建目录: {srt_dir}/")
    
    # 查找根目录下的字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and any(pattern in file.lower() for pattern in ['s01e', 'e0', 'e1', 'ep', 'episode', '第', '集']):
            subtitle_files.append(file)
    
    if not subtitle_files:
        print("❌ 未找到需要迁移的字幕文件")
        return
    
    print(f"📁 找到 {len(subtitle_files)} 个字幕文件需要迁移")
    
    # 迁移文件
    migrated_count = 0
    for file in subtitle_files:
        try:
            source_path = file
            target_path = os.path.join(srt_dir, file)
            
            if os.path.exists(target_path):
                print(f"⚠ 文件已存在，跳过: {file}")
                continue
            
            shutil.move(source_path, target_path)
            print(f"✓ 迁移: {file} -> {target_path}")
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ 迁移失败 {file}: {e}")
    
    print(f"\n✅ 迁移完成！成功迁移 {migrated_count} 个文件")
    print(f"📁 字幕文件现在位于: {srt_dir}/")

def check_video_files():
    """检查videos目录"""
    print("\n🔍 检查videos目录...")
    
    videos_dir = 'videos'
    if not os.path.exists(videos_dir):
        os.makedirs(videos_dir)
        print(f"✓ 创建目录: {videos_dir}/")
    
    video_files = []
    for file in os.listdir(videos_dir):
        if file.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv')):
            video_files.append(file)
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    
    if not video_files:
        print("⚠ 请将视频文件放入videos目录")
    else:
        print("✓ 视频文件准备就绪")

if __name__ == "__main__":
    migrate_subtitle_files()
    check_video_files()
    
    print("\n🎬 文件结构更新完成！")
    print("现在可以运行 python main.py 开始智能剪辑")

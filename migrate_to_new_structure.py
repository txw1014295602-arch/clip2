
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
目录结构迁移工具 - 帮助用户迁移到新的srt和videos目录结构
"""

import os
import shutil
from typing import List, Tuple

def migrate_files():
    """迁移文件到新的目录结构"""
    print("🔄 开始迁移文件到新目录结构...")
    
    # 创建必要的目录
    directories = ['srt', 'videos', 'clips']
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/")
    
    # 迁移字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and any(pattern in file.lower() for pattern in ['s01e', 'ep', 'e0', 'e1', '第', '集']):
            subtitle_files.append(file)
    
    if subtitle_files:
        print(f"\n📝 发现 {len(subtitle_files)} 个字幕文件需要迁移...")
        for file in subtitle_files:
            src = file
            dst = os.path.join('srt', file)
            
            if not os.path.exists(dst):
                shutil.move(src, dst)
                print(f"  ✓ 迁移字幕: {file} -> srt/{file}")
            else:
                print(f"  ⚠ 跳过已存在: {file}")
    else:
        print("📝 未发现需要迁移的字幕文件")
    
    # 迁移视频文件
    video_files = []
    for file in os.listdir('.'):
        if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv')) and any(pattern in file.lower() for pattern in ['s01e', 'ep', 'e0', 'e1', '第', '集']):
            video_files.append(file)
    
    if video_files:
        print(f"\n🎬 发现 {len(video_files)} 个视频文件需要迁移...")
        for file in video_files:
            src = file
            dst = os.path.join('videos', file)
            
            if not os.path.exists(dst):
                shutil.move(src, dst)
                print(f"  ✓ 迁移视频: {file} -> videos/{file}")
            else:
                print(f"  ⚠ 跳过已存在: {file}")
    else:
        print("🎬 未发现需要迁移的视频文件")
    
    # 清理旧的输出目录
    old_output_dirs = ['professional_clips', 'smart_clips', 'output_clips']
    for old_dir in old_output_dirs:
        if os.path.exists(old_dir):
            print(f"\n🧹 处理旧输出目录: {old_dir}")
            
            # 移动文件到新的clips目录
            for file in os.listdir(old_dir):
                src = os.path.join(old_dir, file)
                dst = os.path.join('clips', file)
                
                if os.path.isfile(src) and not os.path.exists(dst):
                    shutil.move(src, dst)
                    print(f"  ✓ 迁移输出文件: {file}")
            
            # 删除空的旧目录
            try:
                if not os.listdir(old_dir):
                    os.rmdir(old_dir)
                    print(f"  ✓ 删除空目录: {old_dir}")
            except OSError:
                print(f"  ⚠ 无法删除目录: {old_dir} (可能不为空)")
    
    print("\n✅ 迁移完成！")
    print("📁 新的目录结构：")
    print("  srt/      - 字幕文件")
    print("  videos/   - 视频文件")
    print("  clips/    - 输出视频")

def show_current_structure():
    """显示当前目录结构"""
    print("\n📊 当前目录结构：")
    
    # 检查根目录文件
    root_subtitles = [f for f in os.listdir('.') if f.endswith(('.txt', '.srt'))]
    root_videos = [f for f in os.listdir('.') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if root_subtitles:
        print(f"📝 根目录字幕文件: {len(root_subtitles)} 个")
    
    if root_videos:
        print(f"🎬 根目录视频文件: {len(root_videos)} 个")
    
    # 检查新目录结构
    for dir_name in ['srt', 'videos', 'clips']:
        if os.path.exists(dir_name):
            files = os.listdir(dir_name)
            print(f"📁 {dir_name}/ 目录: {len(files)} 个文件")
        else:
            print(f"📁 {dir_name}/ 目录: 不存在")

def main():
    """主函数"""
    print("🔄 目录结构迁移工具")
    print("=" * 50)
    
    show_current_structure()
    
    print("\n此工具将帮助您:")
    print("• 将根目录的字幕文件移动到srt目录")
    print("• 将根目录的视频文件移动到videos目录")
    print("• 整理旧的输出目录到clips目录")
    
    choice = input("\n是否开始迁移? (y/N): ").lower()
    
    if choice == 'y':
        migrate_files()
    else:
        print("取消迁移操作")

if __name__ == "__main__":
    main()

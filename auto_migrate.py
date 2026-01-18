
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动文件迁移和环境检查脚本
"""

import os
import shutil
import subprocess
import sys

def auto_migrate_files():
    """自动迁移文件并检查环境"""
    print("🔄 自动迁移和环境检查...")
    
    # 创建必要目录
    dirs_to_create = ['srt', 'videos', 'smart_clips']
    for dir_name in dirs_to_create:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/")
    
    # 迁移根目录的字幕文件到srt目录
    migrated_count = 0
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and any(pattern in file.lower() for pattern in ['s01e', 'e0', 'e1', 'ep', 'episode', '第', '集']):
            source_path = file
            target_path = os.path.join('srt', file)
            
            if not os.path.exists(target_path):
                try:
                    shutil.move(source_path, target_path)
                    print(f"✓ 迁移: {file} -> srt/{file}")
                    migrated_count += 1
                except Exception as e:
                    print(f"❌ 迁移失败 {file}: {e}")
    
    if migrated_count > 0:
        print(f"✅ 成功迁移 {migrated_count} 个字幕文件")
    
    # 检查FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
        else:
            print("⚠ FFmpeg未正确安装")
    except FileNotFoundError:
        print("⚠ FFmpeg未安装，尝试自动安装...")
        try:
            # 在Replit环境中尝试安装FFmpeg
            result = subprocess.run(['nix-env', '-iA', 'nixpkgs.ffmpeg'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ FFmpeg自动安装成功")
            else:
                print("❌ FFmpeg自动安装失败")
        except:
            print("❌ 无法自动安装FFmpeg")
    
    # 检查Python依赖
    required_packages = ['requests', 'flask']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
    
    print("\n🎬 环境检查完成！")
    return True

if __name__ == "__main__":
    auto_migrate_files()

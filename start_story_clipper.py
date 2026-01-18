
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
故事线聚焦剪辑器启动脚本
"""

import os
import sys

def setup_directories():
    """设置目录结构"""
    directories = {
        'srt': '字幕文件目录 (.srt文件)',
        'videos': '视频文件目录 (.mp4, .mkv等)',
        'story_clips': '故事聚焦短视频输出目录'
    }
    
    print("📁 设置故事聚焦剪辑目录结构...")
    print("=" * 60)
    
    for dir_name, description in directories.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/ - {description}")
        else:
            print(f"✓ 目录已存在: {dir_name}/ - {description}")
    
    print()
    print("📋 使用说明：")
    print("1. 将字幕文件(.srt)放入 srt/ 目录")
    print("2. 将对应视频文件放入 videos/ 目录") 
    print("3. 系统将自动为每集制作2-3分钟的核心剧情短视频")
    print("4. 输出的短视频会保存在 story_clips/ 目录")
    print()
    
    # 检查当前状态
    srt_files = []
    video_files = []
    
    if os.path.exists('srt'):
        srt_files = [f for f in os.listdir('srt') if f.lower().endswith('.srt')]
    
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    print("📊 当前状态：")
    print(f"• 字幕文件: {len(srt_files)} 个")
    print(f"• 视频文件: {len(video_files)} 个")
    
    if not srt_files:
        print("⚠️ 请将字幕文件放入 srt/ 目录")
        return False
    
    if not video_files:
        print("⚠️ 请将视频文件放入 videos/ 目录")
        return False
    
    return True

def main():
    """主启动函数"""
    print("🚀 故事线聚焦的智能电视剧剪辑系统")
    print("=" * 60)
    
    # 设置目录
    if not setup_directories():
        print("\n请按照说明放入文件后重新运行")
        return
    
    print("\n🎬 启动故事聚焦剪辑分析...")
    
    try:
        # 导入并运行剪辑器
        from story_focused_clipper import main as run_clipper
        run_clipper()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保 story_focused_clipper.py 文件存在")
    except Exception as e:
        print(f"❌ 运行错误: {e}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整AI剪辑系统启动脚本
一键启动，满足所有需求
"""

import os
import sys

def setup_directories():
    """设置目录结构"""
    directories = {
        'srt': '字幕文件目录 (.srt文件)',
        'videos': '视频文件目录 (.mp4等)',
        'ai_clips': 'AI剪辑输出目录'
    }
    
    print("📁 设置目录结构...")
    for dir_name, description in directories.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/ - {description}")
        else:
            print(f"✓ 目录已存在: {dir_name}/")

def check_requirements():
    """检查系统要求"""
    print("\n🔍 检查系统要求...")
    
    # 检查FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
        else:
            print("❌ FFmpeg未正确安装")
            return False
    except FileNotFoundError:
        print("❌ 未找到FFmpeg，请先安装FFmpeg")
        return False
    
    # 检查字幕文件
    srt_files = []
    if os.path.exists('srt'):
        srt_files = [f for f in os.listdir('srt') if f.lower().endswith(('.srt', '.txt'))]
    
    if not srt_files:
        print("⚠️ srt/目录中暂无字幕文件")
        print("请将字幕文件放入srt/目录")
    else:
        print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    
    # 检查视频文件
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if not video_files:
        print("⚠️ videos/目录中暂无视频文件")
        print("请将视频文件放入videos/目录")
    else:
        print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    return True

def main():
    """主启动函数"""
    print("🚀 完整AI智能剪辑系统")
    print("=" * 50)
    print("功能特点：")
    print("• 每集多个精彩短视频，AI智能判断")
    print("• 实际剪辑生成视频文件")
    print("• videos/和srt/标准目录")
    print("• 自动生成旁白解说文件")
    print("=" * 50)
    
    # 设置目录
    setup_directories()
    
    # 检查要求
    if not check_requirements():
        print("\n❌ 系统要求不满足，请解决上述问题后重试")
        return
    
    print("\n🎯 使用说明：")
    print("1. 将字幕文件(.srt)放入 srt/ 目录")
    print("2. 将对应视频文件放入 videos/ 目录")
    print("3. 文件名要包含集数信息(如 E01, S01E01)")
    print("4. 运行系统开始智能剪辑")
    
    input("\n按回车键启动完整AI剪辑系统...")
    
    # 启动主系统
    try:
        from complete_ai_clipper import main as clipper_main
        clipper_main()
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保 complete_ai_clipper.py 文件存在")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()

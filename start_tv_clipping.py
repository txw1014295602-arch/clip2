
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧短视频剪辑 - 快速启动脚本
"""

import os
import subprocess
import sys

def check_ffmpeg():
    """检查FFmpeg安装"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ 未检测到FFmpeg")
    print("请安装FFmpeg:")
    print("• Ubuntu/Debian: sudo apt install ffmpeg")
    print("• macOS: brew install ffmpeg")
    print("• Windows: 从 https://ffmpeg.org 下载")
    return False

def check_directory_structure():
    """检查目录结构"""
    print("\n📁 检查目录结构...")
    
    # 检查字幕文件
    subtitle_files = [f for f in os.listdir('.') if f.endswith('.txt') and ('E' in f or 'S' in f or '集' in f)]
    
    if not subtitle_files:
        print("❌ 未找到字幕文件")
        print("请将字幕文件放在项目根目录，文件名包含集数信息")
        print("示例: E01.txt, S01E01.txt, 第1集.txt")
        return False
    
    print(f"✅ 找到 {len(subtitle_files)} 个字幕文件:")
    for f in subtitle_files[:5]:  # 显示前5个
        print(f"   {f}")
    if len(subtitle_files) > 5:
        print(f"   ... 还有 {len(subtitle_files) - 5} 个文件")
    
    # 检查视频目录
    videos_dir = 'videos'
    if not os.path.exists(videos_dir):
        print(f"⚠ 视频目录不存在: {videos_dir}")
        print("正在创建视频目录...")
        os.makedirs(videos_dir)
        print(f"✅ 已创建目录: {videos_dir}/")
        print("请将对应的视频文件放入此目录")
    else:
        video_files = [f for f in os.listdir(videos_dir) 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
        if video_files:
            print(f"✅ 找到 {len(video_files)} 个视频文件")
        else:
            print("⚠ videos目录中没有视频文件")
            print("请将视频文件放入videos/目录")
    
    return True

def main():
    """主函数"""
    print("🎬 电视剧短视频剪辑系统 - 快速启动")
    print("=" * 60)
    print("🎯 功能特点:")
    print("• 每集制作一个2-3分钟的核心短视频")
    print("• 自动识别主线剧情（四二八案、628旧案、听证会）")
    print("• 智能选择戏剧张力最强的片段")
    print("• 保持跨集剧情连贯性")
    print("• 自动修正字幕错别字（如"防衛"→"防卫"）")
    print("• 添加专业字幕和标题")
    print("=" * 60)
    
    # 检查环境
    if not check_ffmpeg():
        print("\n❌ 环境检查失败，请先安装FFmpeg")
        return
    
    if not check_directory_structure():
        print("\n❌ 目录结构检查失败，请检查文件准备")
        return
    
    print("\n🚀 环境检查通过，开始剪辑...")
    print("=" * 60)
    
    # 运行剪辑系统
    try:
        from tv_series_clipper import process_all_episodes
        process_all_episodes()
        
        print("\n🎉 剪辑完成！")
        print("📁 输出目录: series_clips/")
        print("📄 详细方案: series_plan.txt")
        
    except Exception as e:
        print(f"\n❌ 剪辑过程中出错: {e}")
        print("请检查字幕和视频文件是否正确")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单集短视频制作启动脚本
"""

import os
import sys

def check_requirements():
    """检查环境要求"""
    print("🔍 检查环境要求...")
    
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
    subtitle_files = [f for f in os.listdir('.') if f.endswith('.txt') and ('E' in f or 'S' in f)]
    if not subtitle_files:
        print("❌ 未找到字幕文件")
        print("请确保字幕文件命名包含集数信息，如：S01E01.txt")
        return False
    else:
        print(f"✅ 找到 {len(subtitle_files)} 个字幕文件")
    
    # 检查视频目录
    if not os.path.exists('videos'):
        print("⚠ videos目录不存在，将自动创建")
        os.makedirs('videos')
        print("📁 请将视频文件放入videos/目录中")
    else:
        video_files = [f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
        if video_files:
            print(f"✅ 找到 {len(video_files)} 个视频文件")
        else:
            print("⚠ videos目录中没有视频文件")
            print("📁 请将视频文件放入videos/目录中")
    
    return True

def main():
    """主函数"""
    print("🎬 电视剧单集短视频制作系统")
    print("=" * 60)
    print("📋 功能特点:")
    print("• 每集制作一个2-3分钟的核心短视频")
    print("• 自动识别主线剧情（四二八案、628旧案、听证会）")
    print("• 智能选择戏剧张力最强的片段")
    print("• 保持跨集剧情连贯性")
    print("• 自动修正字幕错别字")
    print("• 添加专业字幕和标题")
    print("=" * 60)
    
    if not check_requirements():
        print("\n❌ 环境检查失败，请解决上述问题后重新运行")
        return
    
    print("\n✅ 环境检查通过，开始制作...")
    
    try:
        from episode_clipper import process_all_episodes
        process_all_episodes()
        
        print("\n🎉 制作完成！")
        print("📁 短视频文件保存在: episode_clips/")
        print("📄 详细方案文档: series_plan.txt")
        print("💡 每个视频都有对应的说明文件")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保 episode_clipper.py 文件存在")
    except Exception as e:
        print(f"❌ 制作过程中出错: {e}")

if __name__ == "__main__":
    main()

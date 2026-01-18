
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完全智能AI电影分析剪辑系统 - 启动脚本
解决用户提出的所有5个核心问题
"""

import os
import sys
from complete_intelligent_movie_system import CompleteIntelligentMovieSystem
from interactive_config import InteractiveConfigManager

def check_system_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    # 检查必要目录
    required_dirs = ['movie_subtitles', 'movie_videos']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}/")
    
    # 检查字幕文件
    srt_files = [f for f in os.listdir('movie_subtitles') 
                 if f.lower().endswith(('.srt', '.txt'))]
    
    if not srt_files:
        print("❌ 未找到字幕文件")
        print(f"💡 请将电影字幕文件放入 movie_subtitles/ 目录")
        return False
    
    # 检查视频文件
    video_files = [f for f in os.listdir('movie_videos') 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if not video_files:
        print("❌ 未找到视频文件") 
        print(f"💡 请将电影视频文件放入 movie_videos/ 目录")
        return False
    
    print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    return True

def main():
    """主函数"""
    print("🎬 完全智能AI电影分析剪辑系统")
    print("=" * 60)
    print("🚀 解决方案特色:")
    print("• 问题1: 100% AI分析，无固定规则限制")
    print("• 问题2: 完整剧情上下文，避免台词割裂")
    print("• 问题3: 智能上下文衔接，保证连贯性")
    print("• 问题4: AI自主判断最佳剪辑内容")
    print("• 问题5: 全自动化处理流程")
    print("=" * 60)
    
    # 检查AI配置
    config_manager = InteractiveConfigManager()
    
    if not config_manager.get_config().get('enabled'):
        print("⚠️ AI未配置，开始配置向导...")
        if not config_manager.start_guided_setup():
            print("❌ AI配置失败，无法继续")
            return
    else:
        print("✅ AI配置已就绪")
    
    # 检查系统要求
    if not check_system_requirements():
        return
    
    # 确认开始处理
    print(f"\n🎯 准备开始智能分析剪辑")
    choice = input("是否开始处理？(Y/n): ").strip().lower()
    
    if choice in ['', 'y', 'yes', '是']:
        # 启动完全智能系统
        system = CompleteIntelligentMovieSystem()
        system.process_all_movies()
    else:
        print("👋 已取消")

if __name__ == "__main__":
    main()

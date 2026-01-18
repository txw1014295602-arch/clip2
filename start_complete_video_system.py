
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整视频分析剪辑系统启动脚本
满足用户需求6-10的所有要求
"""

import os
import sys
from complete_video_analysis_system import CompleteVideoAnalysisSystem
from interactive_config import InteractiveConfigManager

def check_system_setup():
    """检查系统设置"""
    print("🔍 检查系统设置...")
    
    # 检查必要目录
    required_dirs = ['srt', 'videos']
    missing_dirs = []
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}/")
        else:
            print(f"✅ 目录存在: {directory}/")
    
    # 检查字幕文件
    srt_files = [f for f in os.listdir('srt') if f.lower().endswith(('.srt', '.txt'))]
    if not srt_files:
        print("❌ srt/ 目录中未找到字幕文件")
        print("💡 请将字幕文件放入 srt/ 目录")
        return False
    else:
        print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    
    # 检查视频文件
    video_files = [f for f in os.listdir('videos') 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    if not video_files:
        print("❌ videos/ 目录中未找到视频文件")
        print("💡 请将视频文件放入 videos/ 目录")
        return False
    else:
        print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    return True

def main():
    """主函数"""
    print("🎬 完整视频分析剪辑系统")
    print("=" * 60)
    print("🎯 功能特色:")
    print("• 📁 视频：videos/ 字幕：srt/")
    print("• ✂️ 智能分析每个视频并实际剪辑")
    print("• 🎙️ 生成第一人称旁白文件")
    print("• 🔇 创建无声视频，专注AI叙述")
    print("• 🔗 多短视频剧情完整连贯")
    print("• 🔄 处理反转等复杂剧情关联")
    print("• 📺 视频与叙述实时同步变化")
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
    
    # 检查系统设置
    if not check_system_setup():
        return
    
    # 确认开始处理
    print(f"\n🎯 准备开始完整视频分析剪辑")
    print("📋 处理内容包括:")
    print("  1. 解析所有字幕文件，构建完整故事上下文")
    print("  2. AI深度分析每一集，识别关键片段") 
    print("  3. 创建无声视频片段（移除原始音频）")
    print("  4. 生成第一人称旁白文件，与视频内容同步")
    print("  5. 确保所有片段剧情连贯，可完整讲述故事")
    print("  6. 处理剧情反转等复杂情况的前后关联")
    
    choice = input("\n是否开始处理？(Y/n): ").strip().lower()
    
    if choice in ['', 'y', 'yes', '是']:
        # 启动完整系统
        system = CompleteVideoAnalysisSystem()
        system.process_complete_series()
    else:
        print("👋 已取消")

if __name__ == "__main__":
    main()

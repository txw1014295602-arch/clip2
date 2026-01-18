
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
稳定视频分析剪辑系统启动脚本
解决问题11-15：API稳定性、剪辑一致性、缓存机制、旁白生成
"""

import os
import sys
from stable_video_analysis_system import StableVideoAnalysisSystem
from interactive_config import InteractiveConfigManager

def check_system_requirements():
    """检查系统环境"""
    print("🔍 检查系统环境...")
    
    # 检查必要目录
    required_dirs = ['srt', 'videos']
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}/")
        else:
            print(f"✅ 目录存在: {directory}/")
    
    # 检查字幕文件
    srt_files = []
    if os.path.exists('srt'):
        srt_files = [f for f in os.listdir('srt') if f.lower().endswith(('.srt', '.txt'))]
    
    if not srt_files:
        print("❌ srt/ 目录中未找到字幕文件")
        print("💡 请将字幕文件放入 srt/ 目录")
        return False
    else:
        print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    
    # 检查视频文件
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                       if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if not video_files:
        print("⚠️ videos/ 目录中未找到视频文件")
        print("💡 如果只需要分析，可以不提供视频文件")
    else:
        print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    return True

def main():
    """主函数"""
    print("🎬 稳定视频分析剪辑系统")
    print("=" * 60)
    print("🎯 核心特性:")
    print("• 🔄 API结果缓存，避免重复调用")
    print("• 📝 剪辑结果缓存，保证一致性")
    print("• 🎙️ 智能旁白生成")
    print("• 📺 精彩片段字幕提示")
    print("• 🔁 多次执行结果一致")
    print("• 📁 批量处理所有SRT文件")
    print("=" * 60)
    
    # 检查系统要求
    if not check_system_requirements():
        return
    
    # 检查AI配置
    config_manager = InteractiveConfigManager()
    config = config_manager.get_config()
    
    if not config.get('enabled'):
        print("\n⚠️ AI未配置")
        print("选择操作:")
        print("1. 使用基础分析模式（不需要AI）")
        print("2. 配置AI增强分析")
        
        choice = input("请选择 (1-2): ").strip()
        
        if choice == '2':
            if not config_manager.start_guided_setup():
                print("❌ AI配置失败")
                return
        elif choice != '1':
            print("👋 已取消")
            return
    else:
        print(f"✅ AI配置已就绪: {config.get('model', '未知模型')}")
    
    # 确认开始处理
    print(f"\n🎯 准备开始稳定视频分析剪辑")
    print("📋 处理特点:")
    print("  1. 批量处理所有SRT文件，无需逐个选择")
    print("  2. API结果缓存，分析过的文件不会重复调用API")
    print("  3. 剪辑结果缓存，已剪辑的片段不会重复剪辑")
    print("  4. 多次执行保证完全一致的结果")
    print("  5. 生成第一人称旁白和精彩字幕提示")
    print("  6. 完善的错误处理和恢复机制")
    
    choice = input("\n是否开始处理？(Y/n): ").strip().lower()
    
    if choice in ['', 'y', 'yes', '是']:
        # 启动稳定系统
        system = StableVideoAnalysisSystem()
        system.process_all_episodes()
    else:
        print("👋 已取消")

if __name__ == "__main__":
    main()

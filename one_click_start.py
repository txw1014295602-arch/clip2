
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一键启动脚本 - 最简单的使用方式
"""

import os
import subprocess
import sys

def check_files():
    """检查必要文件"""
    print("🔍 检查文件...")
    
    # 检查字幕文件
    subtitle_files = [f for f in os.listdir('.') if f.endswith('.txt') and f.startswith('S01E')]
    
    if not subtitle_files:
        print("❌ 未找到字幕文件")
        print("请确保字幕文件命名格式为: S01E01_4K_60fps.txt")
        return False
    
    print(f"✅ 找到 {len(subtitle_files)} 个字幕文件")
    return True

def one_click_analysis():
    """一键分析"""
    print("🚀 开始一键分析...")
    
    if not check_files():
        return
    
    try:
        # 运行字幕分析
        result = subprocess.run([sys.executable, 'subtitle_analyzer.py'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print("✅ 分析完成！")
            print("📄 查看详细结果: professional_editing_plan.txt")
        else:
            print("❌ 分析失败:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 运行错误: {e}")

def one_click_full():
    """一键完整流程"""
    print("🎬 开始一键完整剪辑...")
    
    if not check_files():
        return
    
    # 检查视频文件
    if not os.path.exists('videos'):
        print("⚠️ videos文件夹不存在，只能进行字幕分析")
        one_click_analysis()
        return
    
    video_files = [f for f in os.listdir('videos') 
                   if f.endswith(('.mp4', '.mkv', '.avi'))]
    
    if not video_files:
        print("⚠️ videos文件夹中无视频文件，只能进行字幕分析")
        one_click_analysis()
        return
    
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    try:
        # 运行完整流程
        result = subprocess.run([sys.executable, 'video_clipper.py'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print("🎉 完整剪辑完成！")
            print("📁 视频文件: professional_clips/")
            print("📄 详细方案: professional_editing_plan.txt")
        else:
            print("❌ 剪辑失败:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 运行错误: {e}")

def quick_config_ai():
    """快速配置AI"""
    try:
        subprocess.run([sys.executable, 'api_config_helper.py'])
    except Exception as e:
        print(f"❌ 配置AI失败: {e}")

if __name__ == "__main__":
    print("📺 电视剧剪辑系统 - 一键启动")
    print("=" * 40)
    print("1. 🚀 一键分析字幕")
    print("2. 🎬 一键完整剪辑") 
    print("3. 🤖 快速配置AI")
    print("4. 📖 查看详细教程")
    print("0. ❌ 退出")
    
    choice = input("选择功能 (0-4): ").strip()
    
    if choice == "1":
        one_click_analysis()
    elif choice == "2":
        one_click_full()
    elif choice == "3":
        quick_config_ai()
    elif choice == "4":
        print("📖 详细教程请查看: QUICK_START.md")
        print("🌐 在线查看: https://replit.com/@yourusername/your-repl-name")
    elif choice == "0":
        print("👋 再见!")
    else:
        print("❌ 无效选择")

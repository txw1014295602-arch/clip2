
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清理启动脚本 - 简化的使用方式
"""

import os
import sys

def setup_directories():
    """设置目录结构"""
    print("📁 设置目录结构...")
    
    directories = {
        'srt': '字幕文件目录 (.srt文件)',
        'videos': '视频文件目录 (.mp4, .mkv等)',
        'output_clips': '剪辑输出目录'
    }
    
    for dir_name, desc in directories.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/ - {desc}")
        else:
            print(f"✓ 目录已存在: {dir_name}/ - {desc}")

def check_files():
    """检查文件"""
    print("\n📊 检查文件状态...")
    
    # 检查字幕文件
    srt_files = []
    if os.path.exists('srt'):
        srt_files = [f for f in os.listdir('srt') if f.endswith('.srt')]
    
    # 检查视频文件
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
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
    """主函数"""
    print("🚀 智能视频剪辑系统 - 清理版")
    print("=" * 50)
    
    # 设置目录
    setup_directories()
    
    # 检查文件
    if not check_files():
        print("\n❌ 缺少必要文件，请按提示放入文件后重新运行")
        input("按回车键退出...")
        return
    
    print("\n✅ 环境检查通过，开始剪辑...")
    
    try:
        from main_clipper import main as run_clipper
        run_clipper()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()

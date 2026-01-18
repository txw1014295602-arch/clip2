
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧连贯剪辑系统 - 专门处理按集顺序的字幕文件
确保每集一个短视频，且剧情连贯
"""

import os
import sys
from intelligent_tv_clipper import main as intelligent_main
from tv_series_clipper import process_all_episodes

def setup_directories():
    """设置必要目录"""
    directories = ['videos', 'series_clips', 'analysis_cache']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}/")

def check_subtitle_files():
    """检查字幕文件"""
    subtitle_files = []
    
    # 查找所有可能的字幕文件格式
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')):
            # 排除说明文件
            if not any(exclude in file for exclude in ['说明', 'README', 'USAGE', '指南']):
                subtitle_files.append(file)
    
    subtitle_files.sort()
    return subtitle_files

def main():
    """主程序 - 电视剧连贯剪辑"""
    print("🎬 电视剧连贯剪辑系统启动")
    print("=" * 60)
    print("📋 系统特点：")
    print("• 每集生成一个2-3分钟短视频")
    print("• 自动修正字幕错误")
    print("• 智能选择精彩片段")
    print("• 保证剧情连贯性")
    print("• 自动生成专业标题")
    print("=" * 60)
    
    # 1. 设置目录
    print("\n📁 第一步：设置工作目录")
    setup_directories()
    
    # 2. 检查字幕文件
    print("\n📄 第二步：检查字幕文件")
    subtitle_files = check_subtitle_files()
    
    if not subtitle_files:
        print("❌ 未找到字幕文件！")
        print("\n📝 使用说明：")
        print("1. 将字幕文件（.txt 或 .srt）放在项目根目录")
        print("2. 文件名示例：E01.txt, S01E01.txt, 第1集.txt")
        print("3. 确保字幕文件按集数顺序命名")
        return
    
    print(f"✅ 找到 {len(subtitle_files)} 个字幕文件：")
    for i, file in enumerate(subtitle_files[:10], 1):  # 显示前10个
        print(f"   {i:2d}. {file}")
    if len(subtitle_files) > 10:
        print(f"   ... 等共 {len(subtitle_files)} 个文件")
    
    # 3. 检查视频文件
    print("\n🎬 第三步：检查视频文件")
    if not os.path.exists('videos'):
        print("❌ 请创建 videos/ 目录并放入视频文件")
        print("📁 视频文件命名要与字幕文件对应")
        return
    
    video_files = [f for f in os.listdir('videos') 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if not video_files:
        print("❌ videos/ 目录中没有视频文件")
        print("📁 请将视频文件放入 videos/ 目录")
        return
    
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    # 4. 开始剪辑
    print(f"\n🎯 第四步：开始智能剪辑")
    print("正在分析字幕并创建短视频...")
    
    try:
        # 使用智能剪辑系统
        intelligent_main()
        
        print(f"\n📊 剪辑完成！")
        print(f"📁 输出目录：intelligent_clips/")
        print(f"📄 详细报告：intelligent_tv_analysis_report.txt")
        print(f"\n🎉 每个短视频都包含：")
        print(f"• 专业标题和字幕")
        print(f"• 详细说明文件")
        print(f"• 剧情连贯性分析")
        
    except Exception as e:
        print(f"❌ 剪辑过程出错：{e}")
        print(f"\n🔧 故障排除建议：")
        print(f"1. 检查字幕文件格式是否正确")
        print(f"2. 确保视频文件与字幕文件对应")
        print(f"3. 检查是否安装了 FFmpeg")

if __name__ == "__main__":
    main()

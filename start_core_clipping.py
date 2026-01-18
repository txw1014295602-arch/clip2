
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心剧情剪辑系统 - 快速启动脚本
专门处理单集核心剧情，每集一个2-3分钟短视频，确保跨集连贯性
"""

import os
import sys
from episode_core_clipper import process_all_episodes

def setup_directories():
    """设置必要目录"""
    directories = ['videos', 'core_clips', 'episode_reports']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}/")

def check_files():
    """检查文件准备情况"""
    print("\n📁 检查文件准备情况...")
    
    # 检查字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and not file.startswith('.'):
            if any(pattern in file.lower() for pattern in ['e', 's0', '第', '集', 'ep']):
                subtitle_files.append(file)
    
    if not subtitle_files:
        print("❌ 未找到字幕文件")
        print("\n📝 使用说明：")
        print("1. 将字幕文件放在项目根目录")
        print("2. 文件名示例：S01E01.txt, 第1集.srt, EP01.txt")
        print("3. 支持格式：.txt, .srt")
        return False
    
    print(f"✅ 找到 {len(subtitle_files)} 个字幕文件")
    
    # 检查视频文件
    if not os.path.exists('videos'):
        print("⚠ videos目录不存在，请创建并放入视频文件")
        return False
    
    video_files = [f for f in os.listdir('videos') 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if not video_files:
        print("⚠ videos目录中没有视频文件")
        print("请将视频文件放入videos/目录")
        return False
    
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    return True

def main():
    """主程序"""
    print("🎬 电视剧核心剧情剪辑系统")
    print("=" * 80)
    print("🎯 系统特点：")
    print("• 单集核心聚焦：每集围绕1个核心剧情点，时长2-3分钟")
    print("• 主线剧情优先：突出四二八案、628旧案、听证会等关键线索") 
    print("• 强戏剧张力：证词反转、法律争议、情感爆发点")
    print("• 跨集连贯性：明确衔接点，保持故事线逻辑一致")
    print("• 自动错别字修正：修正"防衛"→"防卫"等常见错误")
    print("=" * 80)
    
    # 1. 设置目录
    print("\n📁 第一步：设置工作目录")
    setup_directories()
    
    # 2. 检查文件
    print("\n📄 第二步：检查文件准备")
    if not check_files():
        return
    
    # 3. 开始处理
    print(f"\n🎯 第三步：开始核心剧情剪辑")
    print("正在分析字幕并创建每集核心短视频...")
    
    try:
        process_all_episodes()
        
        print(f"\n🎉 处理完成！")
        print(f"📁 短视频输出：core_clips/")
        print(f"📄 集数报告：episode_reports/")
        print(f"📄 连贯性分析：series_coherence_report.txt")
        print(f"\n📋 每个短视频包含：")
        print(f"• 精确时间标注的关键台词")
        print(f"• 详细的内容亮点分析")
        print(f"• 与下一集的明确衔接说明")
        print(f"• 完整的剧情价值评估")
        
    except Exception as e:
        print(f"❌ 处理过程出错：{e}")
        print(f"\n🔧 故障排除建议：")
        print(f"1. 检查字幕文件格式是否正确")
        print(f"2. 确保视频文件与字幕文件对应")
        print(f"3. 检查是否安装了 FFmpeg")

if __name__ == "__main__":
    main()

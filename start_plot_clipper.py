
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能剧情点剪辑系统启动脚本
一键启动完整的剧情点分析和剪辑流程
"""

import os
import sys

def setup_directories():
    """设置必要目录"""
    directories = ['srt', 'videos', 'clips', 'cache', 'reports']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}/")

def check_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    # 检查SRT文件
    srt_files = []
    if os.path.exists('srt'):
        srt_files = [f for f in os.listdir('srt') if f.endswith(('.srt', '.txt'))]
    
    if not srt_files:
        print("❌ 未找到字幕文件")
        print("📋 使用说明:")
        print("1. 将字幕文件(.srt或.txt)放入 srt/ 目录")
        print("2. 将对应视频文件放入 videos/ 目录") 
        print("3. 文件名要包含集数信息，如: S01E01.srt")
        return False
    
    # 检查视频文件
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if not video_files:
        print("❌ 未找到视频文件")
        print("📋 请将视频文件放入 videos/ 目录")
        return False
    
    print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    return True

def main():
    """主启动函数"""
    print("🎬 智能剧情点剪辑系统 v3.0")
    print("=" * 60)
    print("🎯 核心功能特色:")
    print("• 智能识别5种剧情点类型")
    print("• 按剧情点分段剪辑(关键冲突、人物转折、线索揭露)")
    print("• 非连续时间段智能合并，保证剧情连贯")
    print("• 自动生成旁观者叙述字幕")
    print("• 完整故事线说明")
    print("• 智能错别字修正 (防衛→防卫, 正當→正当等)")
    print()
    print("🔗 跨集连贯性保证:")
    print("• 每集结尾明确标注与下一集的衔接点")
    print("• 分析与前集的逻辑连接")
    print("• 主线剧情追踪和连贯性分析")
    print()
    print("📋 标准化输出格式:")
    print("• 完整剧情分析报告")
    print("• 内容亮点自动提取")
    print("• 跨集连贯性详细说明")
    print("• 错别字修正标注")
    print("=" * 60)
    
    # 设置目录
    setup_directories()
    
    # 检查要求
    if not check_requirements():
        return
    
    # 导入并运行主系统
    try:
        from intelligent_plot_clipper import main as run_clipper
        run_clipper()
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保 intelligent_plot_clipper.py 存在")
    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
旁白预览工具 - 预览旁白效果
"""

import os
import json
from enhanced_narration_generator import EnhancedNarrationGenerator

def preview_narration_for_file(subtitle_file: str):
    """预览单个字幕文件的旁白效果"""
    print(f"\n📺 预览旁白效果: {subtitle_file}")
    print("=" * 60)
    
    # 模拟片段数据（实际使用时从AI分析结果获取）
    sample_segment = {
        'title': 'E01：四二八案申诉启动',
        'plot_significance': '李慕枫正式启动申诉程序，四二八案件迎来重要转机',
        'content_summary': '律师团队分析案件材料，发现关键证据疑点',
        'professional_narration': '在这个关键时刻，李慕枫终于决定为儿子申请重审。经过深入调查，律师团队发现了当年案件的重要疑点，这些新证据可能彻底改变案件的走向。',
        'duration_seconds': 150
    }
    
    # 创建旁白生成器
    ai_config = {'enabled': True}  # 可以根据实际配置调整
    generator = EnhancedNarrationGenerator(ai_config)
    
    # 生成旁白
    narration = generator.generate_segment_narration(sample_segment)
    
    if narration:
        print(f"🎭 检测到剧情类型: {narration['genre']}")
        print(f"🎙️ 主要解说 (3-8秒): {narration['main_explanation']}")
        print(f"💡 精彩提示 (最后3秒): {narration['highlight_tip']}")
        print(f"📝 完整旁白: {narration['full_narration']}")
        
        print(f"\n🎬 字幕效果预览:")
        print("=" * 40)
        print("0-3秒:   [主标题] E01：四二八案申诉启动")
        print("1-4秒:   [标识] 🔥 精彩片段") 
        print(f"3-8秒:   [解说] {narration['main_explanation']}")
        print(f"最后3秒: [提示] {narration['highlight_tip']}")
        
        # 预览FFmpeg滤镜效果
        filters = generator.create_subtitle_filters(narration, 150)
        print(f"\n🔧 生成字幕滤镜数量: {len(filters)}")
        
    else:
        print("❌ 旁白生成失败")

def preview_all_narrations():
    """预览所有字幕文件的旁白效果"""
    print("🎙️ 批量预览旁白效果")
    print("=" * 60)
    
    srt_folder = "srt"
    if not os.path.exists(srt_folder):
        print(f"❌ 字幕目录不存在: {srt_folder}/")
        return
    
    subtitle_files = [f for f in os.listdir(srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
    
    if not subtitle_files:
        print(f"❌ {srt_folder}/ 目录中未找到字幕文件")
        return
    
    subtitle_files.sort()
    
    for i, filename in enumerate(subtitle_files[:3], 1):  # 预览前3个文件
        print(f"\n📺 预览 {i}/{len(subtitle_files)}: {filename}")
        preview_narration_for_file(filename)
        
        if i < 3:
            input("\n按Enter继续下一个预览...")

if __name__ == "__main__":
    print("🎙️ 旁白效果预览工具")
    print("1. 预览单个文件")
    print("2. 批量预览")
    
    choice = input("\n请选择 (1-2): ").strip()
    
    if choice == '1':
        filename = input("请输入字幕文件名: ").strip()
        preview_narration_for_file(filename)
    elif choice == '2':
        preview_all_narrations()
    else:
        print("无效选择")

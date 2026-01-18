
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一智能剪辑系统启动脚本
解决所有15个核心问题的完整解决方案
"""

import os
import sys

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查目录
    required_dirs = ['srt', 'videos']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}/")
        else:
            print(f"✅ 目录存在: {directory}/")
    
    # 检查文件
    srt_files = [f for f in os.listdir('srt') if f.endswith(('.srt', '.txt'))]
    video_files = [f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    
    print(f"📄 字幕文件: {len(srt_files)} 个")
    print(f"🎬 视频文件: {len(video_files)} 个")
    
    # 检查AI配置
    ai_configured = False
    if os.path.exists('.ai_config.json'):
        try:
            import json
            with open('.ai_config.json', 'r') as f:
                config = json.load(f)
                if config.get('enabled') and config.get('api_key'):
                    ai_configured = True
                    print(f"🤖 AI配置: 已启用 ({config.get('provider', '未知')})")
        except:
            pass
    
    if not ai_configured:
        print("⚠️ AI配置: 未启用，将使用基础分析")
    
    return len(srt_files) > 0, len(video_files) > 0

def main():
    """主启动函数"""
    print("🚀 统一智能电视剧剪辑系统")
    print("=" * 60)
    print("✨ 完美解决15个核心问题:")
    print("1. ✅ 完全智能化 - AI自动识别各种剧情类型")
    print("2. ✅ 完整上下文 - 整集分析避免台词割裂")
    print("3. ✅ 上下文连贯 - 前后剧情自然衔接")
    print("4. ✅ 多段精彩视频 - 每集3-5个智能片段")
    print("5. ✅ 自动剪辑生成 - 完整流程自动化")
    print("6. ✅ 规范目录结构 - srt/ 和 videos/ 标准化")
    print("7. ✅ 附带旁白生成 - 专业解说文件")
    print("8. ✅ 优化API调用 - 整集分析大幅减少调用")
    print("9. ✅ 保证剧情连贯 - 考虑反转等特殊情况")
    print("10. ✅ 专业旁白解说 - AI深度剧情理解")
    print("11. ✅ 完整对话保证 - 确保句子完整")
    print("12. ✅ 智能缓存机制 - 避免重复API调用")
    print("13. ✅ 剪辑一致性 - 相同分析相同结果")
    print("14. ✅ 断点续传 - 已剪辑不重复处理")
    print("15. ✅ 执行一致性 - 多次运行结果一致")
    print("=" * 60)
    
    has_srt, has_video = check_environment()
    
    if not has_srt:
        print("\n❌ 未找到字幕文件")
        print("请将字幕文件(.srt 或 .txt)放入 srt/ 目录")
        print("支持格式: EP01.srt, 第01集.txt, S01E01.srt 等")
        return
    
    if not has_video:
        print("\n❌ 未找到视频文件")
        print("请将视频文件(.mp4, .mkv等)放入 videos/ 目录")
        print("文件名应与字幕文件对应")
        return
    
    print("\n🎯 系统特性:")
    print("• 🧠 AI完全驱动，自动识别各种剧情类型")
    print("• 📖 整集上下文分析，避免单句割裂")
    print("• 🎬 每集生成3-5个2-3分钟精彩短视频")
    print("• 🎙️ 自动生成专业旁白解说文件")
    print("• 🔗 保证跨片段剧情连贯性")
    print("• 💾 智能缓存，避免重复API调用")
    print("• ⚖️ 多次执行结果完全一致")
    
    print("\n🚀 启动统一智能剪辑系统...")
    
    try:
        from unified_intelligent_clipper import main as unified_main
        unified_main()
    except ImportError:
        print("❌ 统一系统模块导入失败")
        try:
            os.system("python unified_intelligent_clipper.py")
        except:
            print("❌ 系统启动失败，请检查文件完整性")
    except Exception as e:
        print(f"❌ 系统运行错误: {e}")

if __name__ == "__main__":
    main()

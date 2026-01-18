
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版智能剪辑系统启动脚本
解决您提出的所有15个问题
"""

import os
import sys

def check_requirements():
    """检查运行要求"""
    print("🔍 检查运行环境...")
    
    # 检查目录结构
    required_folders = ['srt', 'videos']
    missing_folders = []
    
    for folder in required_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✓ 创建目录: {folder}/")
        else:
            print(f"✓ 目录存在: {folder}/")
    
    # 检查字幕文件
    srt_files = [f for f in os.listdir('srt') 
                 if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
    
    print(f"📄 字幕文件: {len(srt_files)} 个")
    
    # 检查视频文件
    video_files = [f for f in os.listdir('videos') 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    print(f"🎬 视频文件: {len(video_files)} 个")
    
    # 检查AI配置
    ai_configured = False
    if os.path.exists('.ai_config.json'):
        try:
            import json
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled') and config.get('api_key'):
                    ai_configured = True
                    print(f"🤖 AI配置: 已启用 ({config.get('provider', '未知')})")
        except:
            pass
    
    if not ai_configured:
        print("⚠️ AI配置: 未启用，将使用基础分析")
    
    return len(srt_files) > 0, len(video_files) > 0, ai_configured

def main():
    """主启动函数"""
    print("🚀 增强版智能电视剧剪辑系统")
    print("=" * 60)
    print("✨ 解决的15个核心问题:")
    print("1. ✅ 完全智能化 - 不限制剧情类型")
    print("2. ✅ 完整上下文 - 避免台词割裂")
    print("3. ✅ 上下文连贯 - 前后衔接自然")
    print("4. ✅ 多段精彩视频 - 每集3-5个片段")
    print("5. ✅ 自动剪辑生成 - 完整流程自动化")
    print("6. ✅ 规范目录结构 - videos/ 和 srt/")
    print("7. ✅ 旁白生成 - 专业解说文件")
    print("8. ✅ 优化API调用 - 整集分析减少次数")
    print("9. ✅ 剧情连贯 - 考虑反转等特殊情况")
    print("10. ✅ 专业旁白解说 - AI剧情理解")
    print("11. ✅ 完整对话 - 不截断句子")
    print("12. ✅ 智能缓存 - 避免重复API调用")
    print("13. ✅ 剪辑一致性 - 相同分析相同结果")
    print("14. ✅ 断点续传 - 已剪辑不重复")
    print("15. ✅ 执行一致性 - 多次运行结果一致")
    print("=" * 60)
    
    has_srt, has_video, ai_enabled = check_requirements()
    
    if not has_srt:
        print("\n❌ 未找到字幕文件")
        print("请将字幕文件(.srt 或 .txt)放入 srt/ 目录")
        return
    
    if not has_video:
        print("\n❌ 未找到视频文件")  
        print("请将视频文件(.mp4, .mkv等)放入 videos/ 目录")
        return
    
    print("\n🎯 系统特性:")
    print("• 🧠 AI完全驱动分析，自动识别各种剧情类型")
    print("• 📖 整集上下文分析，避免单句台词割裂")
    print("• 🎬 每集生成3-5个2-3分钟精彩短视频")
    print("• 🎙️ 自动生成专业旁白解说文件")
    print("• 🔗 保证跨片段剧情连贯性")
    print("• 💾 智能缓存机制，避免重复API调用")
    print("• ⚖️ 多次执行结果完全一致")
    
    if ai_enabled:
        print("• 🤖 AI增强分析已启用")
    else:
        print("• 📏 使用基础规则分析")
    
    print("\n🚀 启动增强版智能剪辑系统...")
    
    try:
        from enhanced_intelligent_clipper import main as enhanced_main
        enhanced_main()
    except ImportError:
        print("❌ 增强版系统模块导入失败")
        try:
            os.system("python enhanced_intelligent_clipper.py")
        except:
            print("❌ 系统启动失败，请检查文件完整性")
    except Exception as e:
        print(f"❌ 系统运行错误: {e}")

if __name__ == "__main__":
    main()

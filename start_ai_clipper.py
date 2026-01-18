
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI智能剪辑系统启动脚本
"""

import os
import sys

def check_requirements():
    """检查系统要求"""
    print("🔍 检查系统环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    # 检查必要的包
    try:
        import requests
        import json
        print("✅ 系统环境检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少必要的包: {e}")
        print("请运行: pip install requests")
        return False

def setup_directories():
    """设置目录结构"""
    print("📁 设置目录结构...")
    
    directories = ['videos', 'ai_clips']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}/")
        else:
            print(f"✓ 目录已存在: {directory}/")

def check_files():
    """检查文件情况"""
    print("📄 检查字幕文件...")
    
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and not file.startswith('.') and not file.endswith('说明.txt'):
            subtitle_files.append(file)
    
    if not subtitle_files:
        print("⚠️ 未找到字幕文件")
        print("请将字幕文件放在项目根目录，文件名示例：")
        print("  - E01.txt")
        print("  - S01E01.srt") 
        print("  - 第1集.txt")
        return False
    
    print(f"✅ 找到 {len(subtitle_files)} 个字幕文件")
    
    # 检查videos目录
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    if not video_files:
        print("⚠️ videos目录中没有视频文件")
        print("请将视频文件放入videos/目录")
        return False
    
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    return True

def check_ai_config():
    """检查AI配置"""
    print("🤖 检查AI配置...")
    
    config_file = '.ai_config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled') and config.get('api_key'):
                    print(f"✅ AI配置已启用: {config.get('provider', 'unknown')}")
                    return True
        except:
            pass
    
    print("⚠️ AI配置未设置，将使用基础规则分析")
    print("如需启用AI分析，请运行: python configure_ai.py")
    return True

def main():
    """主启动函数"""
    print("🚀 AI智能电视剧剪辑系统")
    print("=" * 50)
    print("🎯 功能特点:")
    print("• AI智能分析，自适应各种剧情类型")
    print("• 每集2-3分钟精彩片段")
    print("• 自动错别字修正")
    print("• 跨集剧情连贯性")
    print("• 智能视频匹配")
    print("=" * 50)
    
    # 系统检查
    if not check_requirements():
        return
    
    setup_directories()
    check_ai_config()
    
    if not check_files():
        print("\n❌ 文件检查未通过，请准备好字幕和视频文件后重试")
        return
    
    print("\n🎬 开始AI智能剪辑...")
    print("=" * 50)
    
    # 导入并运行主程序
    try:
        from intelligent_ai_clipper import main as ai_main
        ai_main()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        print("请检查文件是否正确放置，或尝试重新运行")

if __name__ == "__main__":
    import json
    main()

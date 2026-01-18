
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一键智能启动 - 自动检测配置，智能推荐，快速开始
"""

import os
import json
from api_config_helper import config_helper
from smart_api_selector import smart_selector

def main():
    """一键智能启动"""
    print("🚀 智能电视剧剪辑系统 - 一键启动")
    print("=" * 60)
    print("🎬 专业的电视剧短视频剪辑工具")
    print("💡 支持AI智能分析 + 规则分析双模式")
    print()
    
    # 检查是否已有配置
    config = config_helper.load_config()
    
    if config.get('enabled'):
        print("✅ 检测到已有AI配置:")
        print(f"   服务商: {config.get('provider', '未知')}")
        print(f"   模型: {config.get('model', '未知')}")
        print()
        
        use_existing = input("是否使用现有配置？(Y/n): ").lower().strip()
        if use_existing not in ['n', 'no', '否']:
            print("🎉 使用现有配置启动系统...")
            start_clipping_system()
            return
    
    print("🔧 开始配置AI接口...")
    print()
    print("💡 提示: AI分析可以显著提升剧情识别准确性")
    print("   • 智能识别关键剧情转折点")
    print("   • 自动评估片段戏剧张力")
    print("   • 优化短视频剧情连贯性")
    print()
    
    enable_ai = input("是否启用AI增强分析？(Y/n): ").lower().strip()
    
    if enable_ai in ['n', 'no', '否']:
        print("📋 将使用基础规则分析模式")
        config = {'enabled': False, 'provider': 'rule_based'}
        config_helper._save_config(config)
    else:
        # 智能配置AI
        print("\n🧠 启动智能配置向导...")
        if smart_selector.smart_configure():
            print("✅ AI配置完成！")
        else:
            print("⚠️ AI配置失败，将使用基础模式")
            config = {'enabled': False, 'provider': 'rule_based'}
            config_helper._save_config(config)
    
    print("\n🎉 配置完成！正在启动剪辑系统...")
    start_clipping_system()

def start_clipping_system():
    """启动剪辑系统"""
    print("\n" + "=" * 60)
    print("🎬 智能电视剧剪辑系统已启动")
    print("=" * 60)
    
    # 导入主要剪辑模块
    try:
        from tv_series_clipper import main as clipper_main
        clipper_main()
    except ImportError:
        try:
            from start_tv_clipping import main as clipper_main
            clipper_main()
        except ImportError:
            print("❌ 未找到剪辑系统主程序")
            print("💡 请检查是否存在 tv_series_clipper.py 或 start_tv_clipping.py")

if __name__ == "__main__":
    main()

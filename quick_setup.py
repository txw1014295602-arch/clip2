
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速配置脚本 - 一键设置AI接口和环境
"""

import json
import os

def quick_setup():
    """快速设置"""
    print("🚀 智能剪辑系统 - 快速配置")
    print("=" * 50)
    
    # 推荐配置
    recommended_configs = {
        "1": {
            "name": "Claude 3.5 Sonnet (推荐)",
            "model": "claude-3-5-sonnet-20240620",
            "base_url": "https://www.chataiapi.com/v1"
        },
        "2": {
            "name": "DeepSeek R1 (思考链)",
            "model": "deepseek-r1", 
            "base_url": "https://www.chataiapi.com/v1"
        },
        "3": {
            "name": "GPT-4o",
            "model": "gpt-4o",
            "base_url": "https://www.chataiapi.com/v1"
        },
        "4": {
            "name": "Gemini 2.5 Pro",
            "model": "gemini-2.5-pro",
            "base_url": "https://www.chataiapi.com/v1"
        }
    }
    
    print("推荐的AI模型配置:")
    for key, config in recommended_configs.items():
        print(f"{key}. {config['name']}")
    
    choice = input("\n选择配置 (1-4): ").strip()
    
    if choice not in recommended_configs:
        print("❌ 无效选择")
        return False
    
    selected = recommended_configs[choice]
    api_key = input(f"\n输入 {selected['name']} 的API密钥: ").strip()
    
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    # 保存配置
    config = {
        "enabled": True,
        "base_url": selected["base_url"],
        "api_key": api_key,
        "model": selected["model"]
    }
    
    with open('.ai_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 配置完成！")
    print(f"模型: {selected['name']}")
    print(f"配置已保存到: .ai_config.json")
    
    # 创建必要的目录
    os.makedirs('videos', exist_ok=True)
    os.makedirs('clips', exist_ok=True)
    
    print("\n📁 已创建目录:")
    print("• videos/ - 放入源视频文件")
    print("• clips/ - 剪辑输出目录")
    
    print("\n📝 使用说明:")
    print("1. 将字幕文件(.txt/.srt)放在项目根目录")
    print("2. 将对应的视频文件放在videos/目录")  
    print("3. 运行 python main.py 开始分析")
    
    return True

if __name__ == "__main__":
    quick_setup()

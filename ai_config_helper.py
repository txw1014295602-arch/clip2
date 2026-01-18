
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI配置助手 - 支持官方API和代理API
"""

import json
import os

def configure_ai():
    """配置AI接口"""
    print("🤖 AI配置向导")
    print("=" * 40)
    
    print("选择API类型:")
    print("1. 官方API (如 Google Gemini)")
    print("2. 代理API (如 OpenRouter, ChatAPI等)")
    
    choice = input("请选择 (1-2): ").strip()
    
    if choice == '1':
        config = configure_official_api()
    elif choice == '2':
        config = configure_proxy_api()
    else:
        print("❌ 无效选择")
        return False
    
    if config:
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ AI配置保存成功")
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    return False

def configure_official_api():
    """配置官方API"""
    print("\n📡 官方API配置")
    
    provider = input("API提供商 (gemini/openai): ").strip().lower()
    api_key = input("API密钥: ").strip()
    
    if not api_key:
        print("❌ API密钥不能为空")
        return None
    
    config = {
        'enabled': True,
        'api_type': 'official',
        'provider': provider,
        'api_key': api_key
    }
    
    if provider == 'gemini':
        config['model'] = input("模型名称 (默认: gemini-2.5-flash): ").strip() or 'gemini-2.5-flash'
    elif provider == 'openai':
        config['model'] = input("模型名称 (默认: gpt-4): ").strip() or 'gpt-4'
    
    return config

def configure_proxy_api():
    """配置代理API"""
    print("\n🌐 代理API配置")
    
    base_url = input("API地址: ").strip()
    api_key = input("API密钥: ").strip()
    model = input("模型名称: ").strip()
    
    if not all([base_url, api_key, model]):
        print("❌ 所有字段都必须填写")
        return None
    
    return {
        'enabled': True,
        'api_type': 'proxy',
        'provider': 'proxy',
        'base_url': base_url,
        'api_key': api_key,
        'model': model
    }

def load_config():
    """加载配置"""
    try:
        if os.path.exists('.ai_config.json'):
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ 配置加载失败: {e}")
    
    return {'enabled': False}

if __name__ == "__main__":
    configure_ai()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速API配置脚本 - 支持多种中转服务商和官方API
"""

from api_config_helper import config_helper

def quick_setup_chataiapi():
    """快速配置ChatAI API"""
    print("🚀 快速配置 ChatAI API")
    print("=" * 40)
    
    api_key = input("请输入ChatAI API密钥: ").strip()
    if not api_key:
        return False
    
    # 推荐模型选择
    models = {
        "1": "claude-3-5-sonnet-20240620",
        "2": "gpt-4o", 
        "3": "deepseek-r1",
        "4": "gemini-2.5-pro"
    }
    
    print("\n选择模型:")
    for key, model in models.items():
        print(f"{key}. {model}")
    
    model_choice = input("请选择 (1-4): ").strip()
    model = models.get(model_choice, "deepseek-r1")
    
    config = {
        'enabled': True,
        'provider': 'ChatAI',
        'api_key': api_key,
        'model': model,
        'base_url': 'https://www.chataiapi.com/v1',
        'api_type': 'proxy'
    }
    
    if config_helper._test_proxy_api(config):
        config_helper._save_config(config)
        print("✅ ChatAI API配置成功！")
        return True
    else:
        print("❌ 配置失败")
        return False

def quick_setup_openai_official():
    """快速配置OpenAI官方API"""
    print("🚀 快速配置 OpenAI 官方API")
    print("=" * 40)
    
    api_key = input("请输入OpenAI API密钥: ").strip()
    if not api_key:
        return False
    
    models = {
        "1": "gpt-4o",
        "2": "gpt-4o-mini",
        "3": "gpt-3.5-turbo"
    }
    
    print("\n选择模型:")
    for key, model in models.items():
        print(f"{key}. {model}")
    
    model_choice = input("请选择 (1-3): ").strip()
    model = models.get(model_choice, "gpt-4o-mini")
    
    config = {
        'enabled': True,
        'provider': 'openai',
        'api_key': api_key,
        'model': model,
        'api_type': 'official'
    }
    
    if config_helper._test_official_api(config):
        config_helper._save_config(config)
        print("✅ OpenAI官方API配置成功！")
        return True
    else:
        print("❌ 配置失败")
        return False

def quick_setup_custom_proxy():
    """快速配置自定义中转API"""
    print("🚀 快速配置自定义中转API")
    print("=" * 40)
    print("💡 请按照以下格式配置:")
    print("示例: https://www.chataiapi.com/v1")
    print()
    
    base_url = input("API地址: ").strip()
    api_key = input("API密钥: ").strip()
    model = input("模型名称: ").strip()
    
    if not all([base_url, api_key, model]):
        print("❌ 所有字段都必须填写")
        return False
    
    config = {
        'enabled': True,
        'provider': 'custom',
        'api_key': api_key,
        'model': model,
        'base_url': base_url,
        'api_type': 'proxy'
    }
    
    if config_helper._test_proxy_api(config):
        config_helper._save_config(config)
        print("✅ 自定义API配置成功！")
        return True
    else:
        print("❌ 配置失败")
        return False

def main():
    """主配置菜单"""
    print("🤖 快速API配置助手")
    print("=" * 50)
    print("支持官方API和中转API，一键配置")
    print()
    
    while True:
        print("选择配置方式:")
        print("1. ChatAI中转API (推荐)")
        print("2. OpenAI官方API")
        print("3. 自定义中转API")
        print("4. 完整交互式配置")
        print("0. 退出")
        
        choice = input("\n请选择 (0-4): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            if quick_setup_chataiapi():
                print("\n🎉 配置完成！现在可以运行系统")
                break
        elif choice == "2":
            if quick_setup_openai_official():
                print("\n🎉 配置完成！现在可以运行系统")
                break
        elif choice == "3":
            if quick_setup_custom_proxy():
                print("\n🎉 配置完成！现在可以运行系统")
                break
        elif choice == "4":
            config = config_helper.interactive_setup()
            if config.get('enabled'):
                print("\n🎉 配置完成！现在可以运行系统")
                break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()

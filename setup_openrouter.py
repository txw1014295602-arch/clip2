
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenRouter API快速配置脚本
支持免费和付费模型
"""

import json
from api_config_helper import config_helper

def setup_openrouter_free():
    """配置OpenRouter免费模型"""
    print("🚀 OpenRouter免费模型快速配置")
    print("=" * 50)
    print("💡 推荐免费模型：")
    print("• deepseek/deepseek-chat-v3-0324:free - DeepSeek免费版本")
    print("• google/gemini-flash-1.5:free - Gemini免费版本")
    print("• meta-llama/llama-3.2-3b-instruct:free - Llama免费版本")
    print()
    
    # 获取API密钥
    api_key = input("请输入OpenRouter API密钥 (从 https://openrouter.ai/keys 获取): ").strip()
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    # 选择模型
    free_models = [
        'deepseek/deepseek-chat-v3-0324:free',
        'google/gemini-flash-1.5:free',
        'meta-llama/llama-3.2-3b-instruct:free',
        'microsoft/phi-3-medium-128k-instruct:free'
    ]
    
    print("可用免费模型：")
    for i, model in enumerate(free_models, 1):
        mark = " ⭐ 推荐" if i == 1 else ""
        print(f"{i}. {model}{mark}")
    
    while True:
        try:
            choice = input(f"选择模型 (1-{len(free_models)}，回车使用推荐): ").strip()
            if not choice:
                selected_model = free_models[0]
                break
            
            choice = int(choice)
            if 1 <= choice <= len(free_models):
                selected_model = free_models[choice - 1]
                break
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入数字")
    
    # 构建配置
    config = {
        'enabled': True,
        'provider': 'openrouter',
        'api_key': api_key,
        'model': selected_model,
        'url': 'https://openrouter.ai/api/v1'
    }
    
    # 测试连接
    print(f"\n🔍 测试API连接...")
    print(f"模型: {selected_model}")
    print(f"地址: https://openrouter.ai/api/v1")
    
    if config_helper._test_api_connection(config):
        print("✅ OpenRouter API连接成功！")
        print(f"🎯 {selected_model} 特别适合电视剧剧情分析")
        config_helper._save_config(config)
        
        print("\n🎬 使用说明：")
        print("1. 运行: python main.py")
        print("2. 选择智能分析或完整剪辑")
        print("3. 享受AI增强的剧情分析功能")
        print("4. 免费模型有使用限制，请合理使用")
        
        return True
    else:
        print("❌ OpenRouter API连接失败，请检查:")
        print("• API密钥是否正确")
        print("• 网络连接是否正常")
        print("• 是否已在OpenRouter注册账户")
        return False

def setup_openrouter_premium():
    """配置OpenRouter付费模型"""
    print("🚀 OpenRouter付费模型配置")
    print("=" * 50)
    print("💎 推荐付费模型：")
    print("• deepseek/deepseek-r1 - 最新推理模型")
    print("• google/gemini-2.0-flash-thinking-exp - 思维链模型")
    print("• openai/gpt-4o - GPT-4 Omni")
    print("• anthropic/claude-3-5-sonnet - Claude 3.5")
    print()
    
    # 获取API密钥
    api_key = input("请输入OpenRouter API密钥: ").strip()
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    # 选择模型
    premium_models = [
        'deepseek/deepseek-r1',
        'google/gemini-2.0-flash-thinking-exp',
        'openai/gpt-4o',
        'anthropic/claude-3-5-sonnet',
        'meta-llama/llama-3.2-90b-vision-instruct'
    ]
    
    print("可用付费模型：")
    for i, model in enumerate(premium_models, 1):
        mark = " ⭐ 推荐" if i == 1 else ""
        print(f"{i}. {model}{mark}")
    
    while True:
        try:
            choice = input(f"选择模型 (1-{len(premium_models)}，回车使用推荐): ").strip()
            if not choice:
                selected_model = premium_models[0]
                break
            
            choice = int(choice)
            if 1 <= choice <= len(premium_models):
                selected_model = premium_models[choice - 1]
                break
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入数字")
    
    # 构建配置
    config = {
        'enabled': True,
        'provider': 'openrouter',
        'api_key': api_key,
        'model': selected_model,
        'url': 'https://openrouter.ai/api/v1'
    }
    
    # 测试连接
    print(f"\n🔍 测试API连接...")
    if config_helper._test_api_connection(config):
        print("✅ OpenRouter付费API连接成功！")
        config_helper._save_config(config)
        return True
    else:
        print("❌ 连接失败")
        return False

def main():
    """主函数"""
    print("🤖 OpenRouter API配置助手")
    print("=" * 50)
    print("OpenRouter提供多种模型选择，包括免费和付费选项")
    print("免费模型适合测试和轻量使用")
    print("付费模型提供更强大的分析能力")
    print()
    
    while True:
        print("选择配置类型：")
        print("1. 免费模型配置 (推荐新手)")
        print("2. 付费模型配置 (高级功能)")
        print("0. 退出")
        
        choice = input("请选择 (0-2): ").strip()
        
        if choice == "0":
            print("👋 退出配置")
            break
        elif choice == "1":
            if setup_openrouter_free():
                print("\n✅ 免费模型配置完成！")
                break
        elif choice == "2":
            if setup_openrouter_premium():
                print("\n✅ 付费模型配置完成！")
                break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()

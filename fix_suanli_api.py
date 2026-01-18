
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
算力云API问题修复脚本
"""

import requests
import json
from api_config_helper import config_helper

def test_suanli_models():
    """测试算力云可用模型"""
    print("🔍 测试算力云可用模型...")
    
    api_key = input("请输入您的算力云API密钥: ").strip()
    if not api_key:
        return
    
    base_urls = [
        "https://api.suanli.cn/v1",
        "https://api.suanli.ai/v1",  # 备用地址
    ]
    
    models_to_test = [
        "deepseek-ai/DeepSeek-R1",
        "deepseek-ai/DeepSeek-V3", 
        "QwQ-32B",
        "Qwen/Qwen2.5-72B-Instruct",
        "meta-llama/Llama-3.2-90B-Vision-Instruct"
    ]
    
    for base_url in base_urls:
        print(f"\n📡 测试地址: {base_url}")
        
        for model in models_to_test:
            print(f"   🤖 测试模型: {model}")
            
            try:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': model,
                    'messages': [{'role': 'user', 'content': 'hi'}],
                    'max_tokens': 5
                }
                
                response = requests.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"      ✅ 成功: {content}")
                    
                    # 保存可用配置
                    config = {
                        'enabled': True,
                        'provider': 'suanli',
                        'api_key': api_key,
                        'model': model,
                        'base_url': base_url,
                        'api_type': 'openai_compatible',
                        'extra_headers': {}
                    }
                    
                    config_helper._save_config(config)
                    print(f"      ✅ 已保存可用配置")
                    return True
                    
                elif response.status_code == 401:
                    print(f"      ❌ 密钥无效")
                    break  # 密钥问题，不用继续测试其他模型
                elif response.status_code == 404:
                    print(f"      ❌ 模型不存在")
                elif response.status_code == 403:
                    print(f"      ❌ 无权限访问")
                else:
                    print(f"      ❌ 错误: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ 异常: {e}")
    
    return False

def fix_suanli_config():
    """修复算力云配置"""
    print("🔧 算力云API配置修复工具")
    print("=" * 40)
    
    print("常见问题及解决方案:")
    print("1. 密钥格式: 确保以 sk- 开头")
    print("2. 账户余额: 确认账户有足够余额")
    print("3. 模型权限: 有些模型需要特殊权限")
    print("4. 网络问题: 尝试更换网络或使用VPN")
    print()
    
    if test_suanli_models():
        print("\n🎉 算力云API配置成功！")
        return True
    else:
        print("\n❌ 算力云API配置失败")
        print("\n💡 建议:")
        print("1. 检查API密钥是否正确")
        print("2. 登录算力云官网确认账户状态")
        print("3. 尝试其他服务商 (如 ChatAI API)")
        return False

def show_alternative_apis():
    """显示备用API选项"""
    print("\n🔄 推荐的备用API服务商:")
    print("=" * 40)
    
    alternatives = [
        {
            'name': 'ChatAI API (推荐)',
            'url': 'https://www.chataiapi.com',
            'models': ['deepseek-r1', 'claude-3.5-sonnet', 'gpt-4'],
            'note': '支持多种模型，连接稳定'
        },
        {
            'name': 'OpenRouter',
            'url': 'https://openrouter.ai',
            'models': ['deepseek/deepseek-r1', 'google/gemini-2.0-flash'],
            'note': '有免费模型可用'
        },
        {
            'name': 'DeepSeek 官方',
            'url': 'https://platform.deepseek.com',
            'models': ['deepseek-r1', 'deepseek-v3'],
            'note': '官方API，稳定性好'
        }
    ]
    
    for i, api in enumerate(alternatives, 1):
        print(f"{i}. {api['name']}")
        print(f"   官网: {api['url']}")
        print(f"   推荐模型: {', '.join(api['models'])}")
        print(f"   特点: {api['note']}")
        print()
    
    choice = input("是否切换到其他API? (y/N): ").lower()
    if choice == 'y':
        from quick_api_config import main as config_main
        config_main()

if __name__ == "__main__":
    if not fix_suanli_config():
        show_alternative_apis()

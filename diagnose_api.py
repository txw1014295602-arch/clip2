
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API连接诊断工具 - 帮助排查API连接问题
"""

import requests
import json
import time
from api_config_helper import config_helper

def diagnose_api_connection():
    """诊断API连接问题"""
    print("🔍 API连接诊断工具")
    print("=" * 50)
    
    # 加载当前配置
    config = config_helper.load_config()
    
    if not config.get('enabled'):
        print("❌ 未找到API配置，请先运行配置脚本")
        return
    
    print(f"📋 当前配置:")
    print(f"   服务商: {config.get('provider', 'unknown')}")
    print(f"   API地址: {config.get('base_url', 'unknown')}")
    print(f"   模型: {config.get('model', 'unknown')}")
    print(f"   密钥: {config.get('api_key', '')[:10]}...")
    print()
    
    # 1. 基础网络连通性测试
    print("1️⃣ 测试基础网络连通性...")
    try:
        base_url = config['base_url']
        domain = base_url.split('//')[1].split('/')[0] if '//' in base_url else base_url.split('/')[0]
        
        response = requests.get(f"https://{domain}", timeout=10)
        print(f"✅ 网络连通正常 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 网络连通异常: {e}")
        print("💡 建议: 检查网络连接或使用VPN")
        return
    
    # 2. API端点测试
    print("\n2️⃣ 测试API端点...")
    try:
        api_url = config['base_url'].rstrip('/') + '/chat/completions'
        
        # 不带认证的请求，看是否返回正确的错误格式
        response = requests.post(api_url, json={}, timeout=10)
        print(f"✅ API端点可访问 (状态码: {response.status_code})")
        
        if response.status_code == 401:
            print("✅ API认证机制正常 (需要密钥)")
        elif response.status_code == 422:
            print("✅ API参数验证正常 (需要正确参数)")
            
    except Exception as e:
        print(f"❌ API端点异常: {e}")
        return
    
    # 3. 认证测试
    print("\n3️⃣ 测试API认证...")
    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }
    headers.update(config.get('extra_headers', {}))
    
    # 最小化请求测试认证
    minimal_data = {
        'model': config['model'],
        'messages': [{'role': 'user', 'content': 'hi'}],
        'max_tokens': 1
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=minimal_data, timeout=15)
        
        if response.status_code == 200:
            print("✅ API认证成功")
            try:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print(f"✅ 模型响应正常: '{content}'")
            except:
                print("⚠️ 响应格式异常，但认证成功")
        elif response.status_code == 401:
            print("❌ API密钥无效")
            print("💡 建议: 检查API密钥是否正确或是否已过期")
        elif response.status_code == 403:
            print("❌ 访问被拒绝")
            print("💡 建议: 检查账户余额或模型访问权限")
        elif response.status_code == 422:
            print("❌ 请求参数错误")
            print("💡 建议: 检查模型名称是否正确")
        else:
            print(f"❌ 未知错误 (状态码: {response.status_code})")
            try:
                error_info = response.json()
                print(f"   错误详情: {error_info}")
            except:
                print(f"   响应内容: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ 认证测试异常: {e}")
    
    # 4. 常见问题建议
    print("\n📋 常见问题解决建议:")
    print("1. API密钥问题:")
    print("   • 确认密钥格式正确 (通常以 sk- 开头)")
    print("   • 检查密钥是否已过期")
    print("   • 确认账户余额充足")
    print()
    print("2. 网络问题:")
    print("   • 检查网络连接是否正常")
    print("   • 尝试使用VPN或更换网络")
    print("   • 确认防火墙设置")
    print()
    print("3. 模型问题:")
    print("   • 确认模型名称拼写正确")
    print("   • 检查是否有权限访问该模型")
    print("   • 尝试使用其他可用模型")

def quick_fix_suggestions():
    """快速修复建议"""
    print("\n🔧 快速修复选项:")
    print("1. 重新配置API")
    print("2. 切换到其他服务商")
    print("3. 使用备用API地址")
    print("4. 联系服务商客服")
    print("0. 退出")
    
    choice = input("\n请选择 (0-4): ").strip()
    
    if choice == "1":
        from quick_api_config import main as config_main
        config_main()
    elif choice == "2":
        print("💡 推荐的备用服务商:")
        print("• ChatAI API: https://www.chataiapi.com")
        print("• OpenRouter: https://openrouter.ai")
        print("• DeepSeek 官方: https://platform.deepseek.com")
    elif choice == "3":
        print("💡 算力云备用地址:")
        print("• 主地址: https://api.suanli.cn/v1")
        print("• 备用地址: https://api.suanli.ai/v1 (如果有)")
    elif choice == "4":
        print("💡 联系方式:")
        print("• 算力云官网: https://suanli.cn")
        print("• 查看官方文档获取最新信息")

if __name__ == "__main__":
    diagnose_api_connection()
    quick_fix_suggestions()

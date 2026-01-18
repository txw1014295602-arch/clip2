
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
连接诊断工具 - 专门解决10054错误
"""

import socket
import time
import requests
from urllib.parse import urlparse
from api_config_helper import config_helper

def diagnose_10054_error():
    """诊断10054错误的原因"""
    print("🔍 Windows Socket Error 10054 诊断工具")
    print("=" * 50)
    print("错误说明: 远程主机强制关闭了现有连接")
    print()
    
    # 1. 检查网络基础连通性
    print("1️⃣ 基础网络连通性测试")
    test_basic_connectivity()
    
    # 2. 检查DNS解析
    print("\n2️⃣ DNS解析测试")
    test_dns_resolution()
    
    # 3. 检查防火墙和代理
    print("\n3️⃣ 防火墙和代理检查")
    check_firewall_proxy()
    
    # 4. 测试API端点
    print("\n4️⃣ API端点连接测试")
    test_api_endpoints()
    
    # 5. 提供解决方案
    print("\n5️⃣ 解决方案建议")
    provide_solutions()

def test_basic_connectivity():
    """测试基础网络连通性"""
    test_hosts = [
        ("百度", "www.baidu.com", 80),
        ("腾讯", "www.qq.com", 80),
        ("Google", "www.google.com", 80)
    ]
    
    for name, host, port in test_hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {name} ({host}): 连接正常")
            else:
                print(f"❌ {name} ({host}): 连接失败 (错误码: {result})")
        except Exception as e:
            print(f"❌ {name} ({host}): 异常 - {e}")

def test_dns_resolution():
    """测试DNS解析"""
    test_domains = [
        "api.openai.com",
        "api.deepseek.com", 
        "www.chataiapi.com",
        "api.suanli.cn"
    ]
    
    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain} -> {ip}")
        except Exception as e:
            print(f"❌ {domain}: DNS解析失败 - {e}")

def check_firewall_proxy():
    """检查防火墙和代理设置"""
    import os
    
    print("检查代理设置:")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    
    has_proxy = False
    for var in proxy_vars:
        if os.environ.get(var):
            print(f"🔍 发现代理设置: {var} = {os.environ[var]}")
            has_proxy = True
    
    if not has_proxy:
        print("✅ 未检测到系统代理设置")
    
    print("\n防火墙建议:")
    print("• 检查Windows防火墙是否阻止Python网络访问")
    print("• 检查杀毒软件的网络保护设置")
    print("• 如果在企业网络，检查公司防火墙设置")

def test_api_endpoints():
    """测试API端点连接"""
    config = config_helper.load_config()
    
    if not config.get('enabled'):
        print("❌ 未找到API配置")
        return
    
    base_url = config.get('base_url')
    if not base_url:
        print("❌ 未找到API地址配置")
        return
    
    print(f"测试API端点: {base_url}")
    
    try:
        # 解析URL
        parsed = urlparse(base_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        # 测试TCP连接
        print(f"测试TCP连接到 {host}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP连接成功")
            
            # 测试HTTP请求
            print("测试HTTP请求...")
            try:
                response = requests.get(base_url, timeout=10)
                print(f"✅ HTTP请求成功 (状态码: {response.status_code})")
            except Exception as e:
                print(f"❌ HTTP请求失败: {e}")
                
        else:
            print(f"❌ TCP连接失败 (错误码: {result})")
            
    except Exception as e:
        print(f"❌ 端点测试异常: {e}")

def provide_solutions():
    """提供解决方案"""
    print("🔧 Error 10054 解决方案:")
    print()
    
    print("立即尝试的解决方案:")
    print("1. 重启网络连接:")
    print("   • 禁用并重新启用网络适配器")
    print("   • 或运行: ipconfig /release && ipconfig /renew")
    print()
    
    print("2. 刷新DNS缓存:")
    print("   • 运行: ipconfig /flushdns")
    print()
    
    print("3. 重置网络设置:")
    print("   • 运行: netsh winsock reset")
    print("   • 运行: netsh int ip reset")
    print("   • 重启计算机")
    print()
    
    print("4. 检查网络环境:")
    print("   • 尝试更换网络 (如手机热点)")
    print("   • 检查是否在企业网络环境")
    print("   • 暂时关闭VPN或代理")
    print()
    
    print("5. 软件层面解决:")
    print("   • 更新Python和相关库")
    print("   • 尝试不同的API服务商")
    print("   • 使用国内中转API服务")
    print()
    
    print("推荐的API服务商 (避免10054错误):")
    print("• ChatAI API: https://www.chataiapi.com (国内访问稳定)")
    print("• 算力云: https://suanli.cn (国内服务商)")
    print("• OpenRouter: https://openrouter.ai (海外但相对稳定)")

def quick_fix_network():
    """快速修复网络问题"""
    print("\n🚀 快速修复向导")
    print("=" * 30)
    
    print("1. 重置API配置 (使用更稳定的服务商)")
    print("2. 测试不同的网络环境")
    print("3. 应用网络修复命令")
    print("0. 返回")
    
    choice = input("\n选择修复方案 (0-3): ").strip()
    
    if choice == "1":
        print("\n🔄 重新配置API...")
        try:
            from quick_api_config import main as config_main
            config_main()
        except ImportError:
            print("❌ 无法导入配置模块")
    
    elif choice == "2":
        print("\n📶 网络环境测试建议:")
        print("• 尝试连接手机热点")
        print("• 更换WiFi网络")
        print("• 使用有线网络连接")
        print("• 暂时关闭VPN/代理")
    
    elif choice == "3":
        print("\n⚠️ 网络修复命令 (需要管理员权限):")
        print("请在管理员命令提示符中运行:")
        print("1. ipconfig /flushdns")
        print("2. netsh winsock reset")
        print("3. netsh int ip reset")
        print("4. 重启计算机")

if __name__ == "__main__":
    diagnose_10054_error()
    quick_fix_network()

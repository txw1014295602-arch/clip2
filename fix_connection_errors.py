
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
连接错误修复工具 - 一键解决常见网络问题
"""

import os
import subprocess
import sys
from api_config_helper import config_helper

def main():
    """主修复流程"""
    print("🔧 连接错误修复工具")
    print("=" * 40)
    print("专门解决 Error 10054 等网络连接问题")
    print()
    
    # 1. 诊断当前问题
    print("1️⃣ 诊断当前配置...")
    diagnose_current_setup()
    
    # 2. 提供修复选项
    print("\n2️⃣ 选择修复方案:")
    show_fix_options()

def diagnose_current_setup():
    """诊断当前设置"""
    config = config_helper.load_config()
    
    if not config.get('enabled'):
        print("❌ 未配置AI分析，建议先配置")
        return False
    
    print(f"✅ 当前API: {config.get('provider', 'unknown')}")
    print(f"✅ API地址: {config.get('base_url', 'unknown')}")
    print(f"✅ 模型: {config.get('model', 'unknown')}")
    
    # 测试连接
    print("🔍 测试连接...")
    if config_helper._test_api_connection(config):
        print("✅ API连接正常")
        return True
    else:
        print("❌ API连接失败")
        return False

def show_fix_options():
    """显示修复选项"""
    while True:
        print("\n选择修复方案:")
        print("1. 🔄 重新配置API (推荐稳定服务商)")
        print("2. 🌐 测试网络环境")
        print("3. 🛠️ 应用系统网络修复")
        print("4. 📊 运行完整诊断")
        print("5. 💡 查看详细解决建议")
        print("0. 退出")
        
        choice = input("\n请选择 (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            reconfigure_api()
        elif choice == "2":
            test_network_environments()
        elif choice == "3":
            apply_system_fixes()
        elif choice == "4":
            run_full_diagnostics()
        elif choice == "5":
            show_detailed_solutions()
        else:
            print("❌ 无效选择")

def reconfigure_api():
    """重新配置API"""
    print("\n🔄 重新配置API")
    print("推荐使用国内可访问的稳定服务商:")
    print()
    
    stable_providers = [
        ("ChatAI API", "国内可访问，支持多种模型"),
        ("算力云", "国内服务商，网络稳定"),
        ("自定义API", "配置其他稳定的中转服务")
    ]
    
    for i, (name, desc) in enumerate(stable_providers, 1):
        print(f"{i}. {name} - {desc}")
    
    choice = input(f"\n选择服务商 (1-{len(stable_providers)}): ").strip()
    
    try:
        if choice == "1":
            setup_chataiapi()
        elif choice == "2":
            setup_suanli()
        elif choice == "3":
            from quick_api_config import main as config_main
            config_main()
        else:
            print("❌ 无效选择")
    except Exception as e:
        print(f"❌ 配置失败: {e}")

def setup_chataiapi():
    """快速设置ChatAI API"""
    print("\n🔧 配置 ChatAI API")
    print("优势: 国内可访问，支持多种模型，网络稳定")
    print()
    
    api_key = input("请输入ChatAI API密钥: ").strip()
    if not api_key:
        print("❌ 密钥不能为空")
        return
    
    config = {
        'enabled': True,
        'provider': 'chataiapi',
        'api_key': api_key,
        'model': 'deepseek-r1',
        'base_url': 'https://www.chataiapi.com/v1',
        'api_type': 'openai_compatible',
        'extra_headers': {}
    }
    
    print("🔍 测试连接...")
    if config_helper._test_api_connection(config):
        config_helper._save_config(config)
        print("✅ ChatAI API配置成功！")
    else:
        print("❌ 连接测试失败")

def setup_suanli():
    """快速设置算力云API"""
    print("\n🔧 配置算力云API")
    print("优势: 国内服务商，网络连接稳定")
    print()
    
    api_key = input("请输入算力云API密钥: ").strip()
    if not api_key:
        print("❌ 密钥不能为空")
        return
    
    config = {
        'enabled': True,
        'provider': 'suanli',
        'api_key': api_key,
        'model': 'deepseek-ai/DeepSeek-R1',
        'base_url': 'https://api.suanli.cn/v1',
        'api_type': 'openai_compatible',
        'extra_headers': {}
    }
    
    print("🔍 测试连接...")
    if config_helper._test_api_connection(config):
        config_helper._save_config(config)
        print("✅ 算力云API配置成功！")
    else:
        print("❌ 连接测试失败")

def test_network_environments():
    """测试网络环境"""
    print("\n🌐 网络环境测试指南")
    print("=" * 30)
    
    test_steps = [
        "1. 当前网络环境测试",
        "2. 更换网络连接 (如手机热点)",
        "3. 禁用VPN/代理后测试",
        "4. 使用有线网络连接测试",
        "5. 更换DNS服务器测试"
    ]
    
    for step in test_steps:
        print(step)
    
    print("\n💡 如果更换网络后正常，说明是网络环境问题")
    print("建议联系网络管理员或ISP解决")

def apply_system_fixes():
    """应用系统修复"""
    print("\n🛠️ 系统网络修复")
    print("=" * 20)
    
    if sys.platform.startswith('win'):
        apply_windows_fixes()
    else:
        apply_unix_fixes()

def apply_windows_fixes():
    """应用Windows修复"""
    print("Windows网络修复命令:")
    print("需要以管理员身份运行命令提示符")
    print()
    
    commands = [
        ("刷新DNS缓存", "ipconfig /flushdns"),
        ("重置Winsock", "netsh winsock reset"),
        ("重置TCP/IP", "netsh int ip reset"),
        ("释放IP", "ipconfig /release"),
        ("重新获取IP", "ipconfig /renew")
    ]
    
    for desc, cmd in commands:
        print(f"• {desc}: {cmd}")
    
    print("\n⚠️ 执行完所有命令后需要重启计算机")
    
    auto_fix = input("\n是否尝试自动执行修复? (需要管理员权限) [y/N]: ").lower() == 'y'
    
    if auto_fix:
        try:
            for desc, cmd in commands[:1]:  # 只执行DNS刷新，比较安全
                print(f"执行: {desc}")
                subprocess.run(cmd, shell=True, check=True)
            print("✅ DNS缓存已刷新")
        except Exception as e:
            print(f"❌ 自动修复失败: {e}")
            print("请手动以管理员身份执行上述命令")

def apply_unix_fixes():
    """应用Unix/Linux修复"""
    print("Unix/Linux网络修复:")
    print("• 重启网络服务: sudo systemctl restart NetworkManager")
    print("• 刷新DNS: sudo systemctl flush-dns")
    print("• 重置网络接口: sudo ifconfig <interface> down && sudo ifconfig <interface> up")

def run_full_diagnostics():
    """运行完整诊断"""
    print("\n📊 运行完整网络诊断...")
    try:
        from connection_diagnostics import diagnose_10054_error
        diagnose_10054_error()
    except ImportError:
        print("❌ 诊断模块未找到")

def show_detailed_solutions():
    """显示详细解决方案"""
    print("\n💡 Error 10054 详细解决方案")
    print("=" * 40)
    
    solutions = [
        {
            "问题": "网络环境问题",
            "症状": "在某些网络下出现10054错误",
            "解决": [
                "更换网络环境 (手机热点、其他WiFi)",
                "联系网络管理员检查防火墙设置",
                "使用VPN或更换DNS服务器"
            ]
        },
        {
            "问题": "API服务商连接不稳定",
            "症状": "偶尔出现10054错误",
            "解决": [
                "更换到国内API服务商 (ChatAI、算力云)",
                "使用官方API + 稳定VPN",
                "配置重试机制和超时设置"
            ]
        },
        {
            "问题": "系统网络配置问题",
            "症状": "所有网络请求都不稳定",
            "解决": [
                "重置网络设置 (Winsock, TCP/IP)",
                "更新网络驱动程序",
                "检查防火墙和杀毒软件设置"
            ]
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. {solution['问题']}")
        print(f"   症状: {solution['症状']}")
        print("   解决方案:")
        for fix in solution['解决']:
            print(f"   • {fix}")

if __name__ == "__main__":
    main()

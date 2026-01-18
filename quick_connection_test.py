
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速连接测试工具 - 专门用于测试AI API连接
"""

from api_config_helper import config_helper

def quick_test_connection():
    """快速测试当前配置的连接"""
    print("🚀 快速连接测试工具")
    print("=" * 50)
    
    # 加载当前配置
    config = config_helper.load_config()
    
    if not config.get('enabled'):
        print("❌ 未找到AI配置")
        print("💡 请先运行主程序配置AI接口")
        return
    
    print("📋 当前配置信息:")
    print(f"   🏷️  服务商: {config.get('model_provider', '未知')}")
    print(f"   🤖 模型: {config.get('model', '未知')}")
    print(f"   🔗 类型: {config.get('api_type', '未知')}")
    if config.get('base_url'):
        print(f"   🌐 地址: {config['base_url']}")
    print(f"   🔑 密钥: {config.get('api_key', '')[:10]}...")
    print()
    
    # 执行连接测试
    success = config_helper._test_api_connection(config)
    
    if success:
        print("\n" + "="*50)
        print("🎉 连接测试成功！AI接口工作正常")
        print("=" * 50)
        
        # 进行功能测试
        print("\n🧪 进行功能测试...")
        test_prompt = "请简单介绍一下电视剧剧情分析的重要性"
        
        try:
            response = config_helper.call_ai_api(test_prompt, config)
            if response:
                print("✅ AI功能测试成功")
                print(f"📝 AI回复预览: {response[:100]}...")
            else:
                print("⚠️  AI功能测试失败，但连接正常")
        except Exception as e:
            print(f"⚠️  AI功能测试异常: {e}")
            
    else:
        print("\n" + "="*50)
        print("❌ 连接测试失败")
        print("=" * 50)
        print("🔧 建议解决方案:")
        print("1. 检查网络连接")
        print("2. 验证API密钥")
        print("3. 确认服务商状态")
        print("4. 运行网络诊断工具")
        
        print(f"\n📞 技术支持:")
        provider = config.get('model_provider', '')
        if provider == 'openai':
            print("• OpenAI状态页: https://status.openai.com/")
        elif provider == 'deepseek':
            print("• DeepSeek文档: https://platform.deepseek.com/")
        elif provider == 'gemini':
            print("• Google AI文档: https://ai.google.dev/")

def interactive_diagnosis():
    """交互式诊断"""
    print("\n🔍 交互式连接诊断")
    print("=" * 30)
    print("1. 基础连接测试")
    print("2. 网络诊断")
    print("3. API配置检查")
    print("4. 重新配置API")
    print("0. 退出")
    
    choice = input("\n请选择诊断项目 (0-4): ").strip()
    
    if choice == "1":
        quick_test_connection()
    elif choice == "2":
        print("💡 启动网络诊断工具...")
        try:
            from connection_diagnostics import diagnose_10054_error
            diagnose_10054_error()
        except ImportError:
            print("❌ 网络诊断工具不可用")
    elif choice == "3":
        check_config_details()
    elif choice == "4":
        print("💡 启动API配置...")
        new_config = config_helper.interactive_setup()
        if new_config.get('enabled'):
            print("✅ 重新配置完成")
        else:
            print("❌ 配置取消或失败")

def check_config_details():
    """检查配置详情"""
    config = config_helper.load_config()
    
    print("\n📋 详细配置检查")
    print("=" * 30)
    
    required_fields = ['enabled', 'api_type', 'model_provider', 'api_key', 'model']
    
    for field in required_fields:
        if field in config:
            if field == 'api_key':
                print(f"✅ {field}: {config[field][:10]}...")
            else:
                print(f"✅ {field}: {config[field]}")
        else:
            print(f"❌ 缺少字段: {field}")
    
    # 检查可选字段
    optional_fields = ['base_url', 'extra_headers', 'proxy_provider']
    for field in optional_fields:
        if field in config:
            print(f"🔧 {field}: {config[field]}")

if __name__ == "__main__":
    quick_test_connection()
    
    # 提供交互选项
    if input("\n是否需要更多诊断? (y/n): ").strip().lower() == 'y':
        interactive_diagnosis()

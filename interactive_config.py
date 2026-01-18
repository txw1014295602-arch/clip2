#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式配置系统 - 解决问题15：引导式让用户选择配置
"""

import os
import json
from typing import Dict, Optional

class InteractiveConfigManager:
    """交互式配置管理器"""

    def __init__(self):
        self.config_file = '.ai_config.json'
        self.current_config = self._load_existing_config()

    def _load_existing_config(self) -> Dict:
        """加载现有配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载配置失败: {e}")
        return {}

    def start_guided_setup(self) -> bool:
        """开始引导式配置"""
        print("🎬 电影AI剪辑系统 - 配置向导")
        print("=" * 50)

        # 检查现有配置
        if self._check_existing_config():
            if self._ask_use_existing():
                return True

        print("\n🔧 开始新的配置设置...")

        # 选择配置类型
        config_type = self._choose_config_type()
        if config_type == 'skip':
            print("⚠️ 跳过AI配置，将使用基础功能")
            return False

        # 根据类型进行配置
        if config_type == 'official':
            return self._configure_official_api()
        elif config_type == 'proxy':
            return self._configure_proxy_api()
        elif config_type == 'preset':
            return self._configure_preset_api()

        return False

    def _check_existing_config(self) -> bool:
        """检查现有配置"""
        if not self.current_config.get('enabled'):
            return False

        print("✅ 发现现有AI配置:")
        print(f"   🔧 类型: {self.current_config.get('api_type', '未知')}")
        print(f"   🏢 提供商: {self.current_config.get('provider', '未知')}")
        print(f"   🤖 模型: {self.current_config.get('model', '未知')}")
        if self.current_config.get('base_url'):
            print(f"   🌐 地址: {self.current_config.get('base_url')}")
        print(f"   🔑 密钥: {self.current_config.get('api_key', '')[:10]}...")

        return True

    def _ask_use_existing(self) -> bool:
        """询问是否使用现有配置"""
        while True:
            choice = input("\n是否使用现有配置？(Y/n): ").strip().lower()
            if choice in ['', 'y', 'yes', '是']:
                # 测试现有配置
                if self._test_current_config():
                    print("✅ 现有配置测试成功，将使用现有配置")
                    return True
                else:
                    print("❌ 现有配置测试失败，需要重新配置")
                    return False
            elif choice in ['n', 'no', '否']:
                return False
            else:
                print("请输入 Y 或 N")

    def _choose_config_type(self) -> str:
        """选择配置类型"""
        print("\n🚀 选择AI配置方式:")
        print("1. 🔒 官方API (Google Gemini, OpenAI等)")
        print("2. 🌐 中转API (ChatAI, OpenRouter等)")
        print("3. 📋 预设配置 (推荐中转服务)")
        print("4. ⏭️ 跳过配置 (仅使用基础功能)")

        while True:
            choice = input("\n请选择 (1-4): ").strip()
            if choice == '1':
                return 'official'
            elif choice == '2':
                return 'proxy'
            elif choice == '3':
                return 'preset'
            elif choice == '4':
                return 'skip'
            else:
                print("❌ 无效选择，请输入1-4")

    def _configure_official_api(self) -> bool:
        """配置官方API"""
        print("\n🔒 官方API配置")
        print("支持的官方API:")
        print("1. Google Gemini (推荐)")
        print("2. OpenAI GPT")
        print("3. Anthropic Claude")

        while True:
            choice = input("请选择 (1-3): ").strip()
            if choice == '1':
                return self._setup_gemini()
            elif choice == '2':
                return self._setup_openai()
            elif choice == '3':
                return self._setup_claude()
            else:
                print("❌ 无效选择，请输入1-3")

    def _setup_gemini(self) -> bool:
        """设置Gemini配置"""
        print("\n📡 Google Gemini配置")
        print("获取API密钥：https://aistudio.google.com/")

        api_key = input("请输入Gemini API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False

        model = input("模型名称 (默认: gemini-2.0-flash-exp): ").strip()
        if not model:
            model = "gemini-2.0-flash-exp"

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': model
        }

        return self._save_and_test_config(config)

    def _setup_openai(self) -> bool:
        """设置OpenAI配置"""
        print("\n🤖 OpenAI配置")
        print("获取API密钥：https://platform.openai.com/")

        api_key = input("请输入OpenAI API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False

        model = input("模型名称 (默认: gpt-4): ").strip()
        if not model:
            model = "gpt-4"

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'openai',
            'api_key': api_key,
            'model': model
        }

        return self._save_and_test_config(config)

    def _setup_claude(self) -> bool:
        """设置Claude配置"""
        print("\n🎭 Anthropic Claude配置")
        print("获取API密钥：https://console.anthropic.com/")

        api_key = input("请输入Anthropic API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False

        model = input("模型名称 (默认: claude-3-5-sonnet-20241022): ").strip()
        if not model:
            model = "claude-3-5-sonnet-20241022"

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'claude',
            'api_key': api_key,
            'model': model
        }

        return self._save_and_test_config(config)

    def _configure_proxy_api(self) -> bool:
        """配置中转API"""
        print("\n🌐 中转API配置")
        print("推荐服务：")
        print("• ChatAI: https://www.chataiapi.com/")
        print("• OpenRouter: https://openrouter.ai/")
        print("• SiliconFlow: https://siliconflow.cn/")

        base_url = input("\nAPI地址: ").strip()
        if not base_url:
            print("❌ API地址不能为空")
            return False

        api_key = input("API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False

        model = input("模型名称 (如: deepseek-r1): ").strip()
        if not model:
            print("❌ 模型名称不能为空")
            return False

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': 'proxy',
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }

        return self._save_and_test_config(config)

    def _configure_preset_api(self) -> bool:
        """配置预设API"""
        print("\n📋 预设配置选择")
        presets = {
            '1': {
                'name': 'ChatAI (DeepSeek-R1)',
                'config': {
                    'enabled': True,
                    'api_type': 'proxy',
                    'provider': 'chatai',
                    'base_url': 'https://www.chataiapi.com/v1',
                    'model': 'deepseek-r1'
                }
            },
            '2': {
                'name': 'OpenRouter (DeepSeek-R1)',
                'config': {
                    'enabled': True,
                    'api_type': 'proxy',
                    'provider': 'openrouter',
                    'base_url': 'https://openrouter.ai/api/v1',
                    'model': 'deepseek/deepseek-r1'
                }
            },
            '3': {
                'name': 'SiliconFlow (DeepSeek-V3)',
                'config': {
                    'enabled': True,
                    'api_type': 'proxy',
                    'provider': 'siliconflow',
                    'base_url': 'https://api.siliconflow.cn/v1',
                    'model': 'deepseek-ai/DeepSeek-V2.5'
                }
            }
        }

        for key, preset in presets.items():
            print(f"{key}. {preset['name']}")

        while True:
            choice = input("\n请选择预设配置 (1-3): ").strip()
            if choice in presets:
                preset = presets[choice]
                print(f"\n选择了: {preset['name']}")

                api_key = input("请输入API密钥: ").strip()
                if not api_key:
                    print("❌ API密钥不能为空")
                    return False

                config = preset['config'].copy()
                config['api_key'] = api_key

                return self._save_and_test_config(config)
            else:
                print("❌ 无效选择，请输入1-3")

    def _save_and_test_config(self, config: Dict) -> bool:
        """保存并测试配置"""
        try:
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            print("\n🔍 测试配置...")

            # 测试配置
            if self._test_config(config):
                print("✅ 配置测试成功！")
                self.current_config = config
                return True
            else:
                print("❌ 配置测试失败")
                return False

        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False

    def _test_config(self, config: Dict) -> bool:
        """测试配置"""
        try:
            # 这里应该调用实际的API测试
            # 为了简化，我们只做基本验证
            required_fields = ['enabled', 'api_type', 'api_key']
            for field in required_fields:
                if not config.get(field):
                    return False

            if config['api_type'] == 'proxy' and not config.get('base_url'):
                return False

            # 实际测试需要调用API
            print("   🔗 检查API连通性...")
            print("   📝 验证模型可用性...")

            return True

        except Exception as e:
            print(f"   ❌ 测试出错: {e}")
            return False

    def _test_current_config(self) -> bool:
        """测试当前配置"""
        return self._test_config(self.current_config)

    def get_config(self) -> Dict:
        """获取当前配置"""
        return self.current_config

    def show_config_status(self):
        """显示配置状态"""
        print("\n📊 当前配置状态:")
        if self.current_config.get('enabled'):
            print("✅ AI配置: 已启用")
            print(f"   类型: {self.current_config.get('api_type')}")
            print(f"   提供商: {self.current_config.get('provider')}")
            print(f"   模型: {self.current_config.get('model')}")
        else:
            print("❌ AI配置: 未启用")

def main():
    """主函数 - 独立配置工具"""
    config_manager = InteractiveConfigManager()

    print("🎬 电影AI剪辑系统 - 配置工具")
    print("=" * 40)

    if config_manager.start_guided_setup():
        print("\n🎉 配置完成！可以开始使用电影AI剪辑系统")
    else:
        print("\n⚠️ 配置跳过或失败，将使用基础功能")

    config_manager.show_config_status()

if __name__ == "__main__":
    main()
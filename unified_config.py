
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一配置管理系统
整合所有AI配置功能
"""

import os
import json
from typing import Dict, Any, Optional

class UnifiedConfig:
    """统一配置管理器"""
    
    def __init__(self):
        self.config_file = '.ai_config.json'
        self.config = self._load_config()
        
        # 支持的AI提供商配置
        self.providers = {
            'openai_official': {
                'name': 'OpenAI 官方',
                'base_url': 'https://api.openai.com/v1',
                'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
                'default_model': 'gpt-4o-mini',
                'requires_custom_client': False
            },
            'gemini_official': {
                'name': 'Google Gemini 官方',
                'models': ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro'],
                'default_model': 'gemini-2.5-flash',
                'requires_custom_client': True
            },
            'deepseek_official': {
                'name': 'DeepSeek 官方',
                'base_url': 'https://api.deepseek.com/v1',
                'models': ['deepseek-r1', 'deepseek-v3'],
                'default_model': 'deepseek-r1',
                'requires_custom_client': False
            },
            'proxy_chataiapi': {
                'name': '中转商 - ChatAI API',
                'base_url': 'https://www.chataiapi.com/v1',
                'models': ['gpt-4o', 'claude-3.5-sonnet', 'deepseek-r1', 'gemini-2.5-pro'],
                'default_model': 'deepseek-r1',
                'requires_custom_client': False
            },
            'proxy_openrouter': {
                'name': '中转商 - OpenRouter',
                'base_url': 'https://openrouter.ai/api/v1',
                'models': ['anthropic/claude-3.5-sonnet', 'google/gemini-2.0-flash-exp'],
                'default_model': 'anthropic/claude-3.5-sonnet',
                'requires_custom_client': False,
                'extra_headers': {
                    'HTTP-Referer': 'https://replit.com',
                    'X-Title': 'TV-Clipper-AI'
                }
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 配置加载失败: {e}")
        
        return {'enabled': False}
    
    def save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已保存")
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    def is_enabled(self) -> bool:
        """检查AI是否启用"""
        return self.config.get('enabled', False)
    
    def get_provider_info(self, provider_key: str) -> Optional[Dict]:
        """获取提供商信息"""
        return self.providers.get(provider_key)
    
    def interactive_setup(self) -> Dict[str, Any]:
        """交互式配置"""
        print("🤖 AI配置向导")
        print("=" * 50)
        
        # 显示提供商选择
        provider_list = list(self.providers.keys())
        for i, key in enumerate(provider_list, 1):
            info = self.providers[key]
            print(f"{i}. {info['name']}")
        
        print("0. 禁用AI分析")
        
        while True:
            try:
                choice = input(f"\n请选择 (0-{len(provider_list)}): ").strip()
                
                if choice == '0':
                    config = {'enabled': False}
                    self.save_config(config)
                    return config
                
                choice = int(choice)
                if 1 <= choice <= len(provider_list):
                    provider_key = provider_list[choice - 1]
                    return self._setup_provider(provider_key)
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")
    
    def _setup_provider(self, provider_key: str) -> Dict[str, Any]:
        """配置特定提供商"""
        provider_info = self.providers[provider_key]
        
        print(f"\n配置 {provider_info['name']}")
        print("-" * 30)
        
        # 获取API密钥
        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return {'enabled': False}
        
        # 选择模型
        models = provider_info['models']
        print(f"\n可用模型:")
        for i, model in enumerate(models, 1):
            mark = " (推荐)" if model == provider_info['default_model'] else ""
            print(f"{i}. {model}{mark}")
        
        while True:
            model_choice = input(f"选择模型 (1-{len(models)}, 回车默认): ").strip()
            if not model_choice:
                selected_model = provider_info['default_model']
                break
            
            try:
                choice = int(model_choice)
                if 1 <= choice <= len(models):
                    selected_model = models[choice - 1]
                    break
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")
        
        # 构建配置
        config = {
            'enabled': True,
            'provider': provider_key,
            'api_key': api_key,
            'model': selected_model
        }
        
        # 添加特定字段
        if 'base_url' in provider_info:
            config['base_url'] = provider_info['base_url']
        
        if 'extra_headers' in provider_info:
            config['extra_headers'] = provider_info['extra_headers']
        
        # 测试连接
        if self._test_connection(config):
            self.save_config(config)
            self.config = config
            return config
        else:
            print("❌ 连接测试失败")
            return {'enabled': False}
    
    def _test_connection(self, config: Dict[str, Any]) -> bool:
        """测试API连接"""
        print("🔍 测试API连接...")
        
        try:
            provider = config['provider']
            
            if provider == 'gemini_official':
                return self._test_gemini(config)
            else:
                return self._test_openai_compatible(config)
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False
    
    def _test_gemini(self, config: Dict[str, Any]) -> bool:
        """测试Gemini API"""
        try:
            from google import genai
            
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'],
                contents="hello"
            )
            
            print("✅ Gemini连接成功")
            return True
        except ImportError:
            print("❌ 需要安装: pip install google-genai")
            return False
        except Exception as e:
            print(f"❌ Gemini测试失败: {e}")
            return False
    
    def _test_openai_compatible(self, config: Dict[str, Any]) -> bool:
        """测试OpenAI兼容API"""
        try:
            from openai import OpenAI
            
            client_kwargs = {'api_key': config['api_key']}
            if 'base_url' in config:
                client_kwargs['base_url'] = config['base_url']
            
            client = OpenAI(**client_kwargs)
            
            completion = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': 'hello'}],
                max_tokens=10,
                extra_headers=config.get('extra_headers', {})
            )
            
            print("✅ API连接成功")
            return True
        except Exception as e:
            print(f"❌ API测试失败: {e}")
            return False

# 全局配置实例
unified_config = UnifiedConfig()

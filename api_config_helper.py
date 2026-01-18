#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的API配置助手 - 区分官方API和中转API
官方API: 直接使用官方SDK，无需base_url
中转API: 使用OpenAI兼容格式，需要base_url
"""

import json
import os
import requests
from typing import Dict, Optional

class ConfigHelper:
    """简化的配置助手类"""

    def interactive_setup(self) -> Dict:
        """交互式AI配置"""
        print("\n🤖 AI接口配置")
        print("=" * 40)
        print("选择API类型:")
        print("1. 🔒 官方API (Google Gemini)")
        print("2. 🌐 中转API (ChatAI, OpenRouter等)")
        print("3. ⏭️ 跳过配置")

        choice = input("请选择 (1-3): ").strip()

        if choice == '1':
            return self._setup_official_api()
        elif choice == '2':
            return self._setup_proxy_api()
        else:
            return {'enabled': False}

    def _setup_official_api(self) -> Dict:
        """配置官方API - 仅支持Gemini"""
        print("\n🔒 官方API配置 - Google Gemini")

        api_key = input("Gemini API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return {'enabled': False}

        models = ["gemini-2.5-flash", "gemini-2.5-pro"]
        print(f"\n可用模型:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")

        model_choice = input(f"选择模型 (1-{len(models)}): ").strip()
        try:
            model = models[int(model_choice) - 1]
        except:
            model = models[0]

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': model
        }

        # 测试连接
        print("🔍 测试连接...")
        if self._test_gemini_official(config):
            print("✅ 连接成功")
            self._save_config(config)
            return config
        else:
            print("❌ 连接失败")
            return {'enabled': False}

    def _setup_proxy_api(self) -> Dict:
        """配置中转API"""
        print("\n🌐 中转API配置")

        # 预设选项
        presets = {
            "1": {
                "name": "ChatAI API",
                "base_url": "https://www.chataiapi.com/v1",
                "models": ["deepseek-r1", "claude-3-5-sonnet-20240620", "gpt-4o"]
            },
            "2": {
                "name": "自定义中转",
                "base_url": "",
                "models": []
            }
        }

        print("选择中转服务:")
        for key, preset in presets.items():
            print(f"{key}. {preset['name']}")

        choice = input("请选择 (1-2): ").strip()

        if choice not in presets:
            return {'enabled': False}

        selected = presets[choice]

        if choice == "2":
            base_url = input("API地址 (如: https://api.example.com/v1): ").strip()
            if not base_url:
                return {'enabled': False}
            model = input("模型名称: ").strip()
            if not model:
                return {'enabled': False}
        else:
            base_url = selected["base_url"]
            print(f"\n推荐模型:")
            for i, m in enumerate(selected["models"], 1):
                print(f"{i}. {m}")

            model_choice = input(f"选择模型 (1-{len(selected['models'])}): ").strip()
            try:
                model = selected["models"][int(model_choice) - 1]
            except:
                model = selected["models"][0]

        api_key = input("API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return {'enabled': False}

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': selected['name'],
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }

        # 测试连接
        print("🔍 测试连接...")
        if self._test_openai_compatible(config):
            print("✅ 连接成功")
            self._save_config(config)
            return config
        else:
            print("❌ 连接失败")
            return {'enabled': False}

    def _test_gemini_official(self, config: Dict) -> bool:
        """测试Gemini官方API"""
        try:
            from google import genai

            # 官方方式创建客户端
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'], 
                contents="测试"
            )
            return bool(response.text)
        except ImportError:
            print("需要安装: pip install google-generativeai")
            return False
        except Exception as e:
            print(f"测试失败: {e}")
            return False

    def _test_openai_compatible(self, config: Dict) -> bool:
        """测试OpenAI兼容API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试'}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except ImportError:
            print("需要安装: pip install openai")
            return False
        except Exception as e:
            print(f"测试失败: {e}")
            return False

    def _save_config(self, config: Dict) -> bool:
        """保存配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def call_ai_api(self, prompt: str, config: Dict, system_prompt: str = "") -> Optional[str]:
        """统一AI API调用"""
        if not config.get('enabled'):
            return None

        try:
            if config.get('api_type') == 'official':
                return self._call_gemini_official(prompt, config, system_prompt)
            else:
                return self._call_openai_compatible(prompt, config, system_prompt)
        except Exception as e:
            print(f"API调用失败: {e}")
            return None

    def _call_gemini_official(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai

            # 官方方式创建客户端
            client = genai.Client(api_key=config['api_key'])

            # 组合提示词
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            # 生成内容
            response = client.models.generate_content(
                model=config['model'], 
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return None

    def _call_openai_compatible(self, prompt: str, config: Dict, system_prompt: str) -> Optional[str]:
        """调用OpenAI兼容API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=config['model'],
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API调用失败: {e}")
            return None

# 全局实例
config_helper = ConfigHelper()
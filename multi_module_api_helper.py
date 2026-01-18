#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多模块API助手
支持不同模块使用不同的AI API配置
"""

import os
from typing import Dict, Optional, Any
from config_manager import ConfigManager


class MultiModuleAPIHelper:
    """多模块API助手 - 统一管理不同模块的API调用"""

    def __init__(self, config_manager: ConfigManager):
        """初始化API助手"""
        self.config_manager = config_manager

    def call_module_api(
        self,
        module_name: str,
        prompt: str,
        system_prompt: str = "",
        **kwargs
    ) -> Optional[str]:
        """
        根据模块名称调用对应的API

        Args:
            module_name: 模块名称（speech_to_text, content_analysis, subtitle_generation）
            prompt: 用户提示词
            system_prompt: 系统提示词
            **kwargs: 其他参数

        Returns:
            API响应文本，失败返回None
        """
        # 获取模块配置
        config = self.config_manager.get_module_config(module_name)

        if not config:
            print(f"❌ 模块 {module_name} 不存在")
            return None

        if not config.get('enabled'):
            print(f"❌ 模块 {module_name} 未启用")
            return None

        # 验证配置
        is_valid, message = self.config_manager.validate_module_config(module_name)
        if not is_valid:
            print(f"❌ {message}")
            return None

        # 根据提供商调用对应的API
        provider = config['provider'].lower()

        try:
            if provider == 'openai':
                return self._call_openai_api(config, prompt, system_prompt, **kwargs)
            elif provider == 'gemini':
                return self._call_gemini_api(config, prompt, system_prompt, **kwargs)
            elif provider == 'deepseek':
                return self._call_deepseek_api(config, prompt, system_prompt, **kwargs)
            else:
                print(f"❌ 不支持的提供商: {provider}")
                return None
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return None

    def _call_openai_api(
        self,
        config: Dict,
        prompt: str,
        system_prompt: str = "",
        **kwargs
    ) -> Optional[str]:
        """调用OpenAI兼容的API"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=config['api_key'],
                base_url=config.get('base_url', 'https://api.openai.com/v1')
            )

            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            response = client.chat.completions.create(
                model=config['model'],
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 8000),
                temperature=kwargs.get('temperature', 0.7)
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"⚠️ OpenAI API调用失败: {e}")
            return None

    def _call_gemini_api(
        self,
        config: Dict,
        prompt: str,
        system_prompt: str = "",
        **kwargs
    ) -> Optional[str]:
        """调用Google Gemini API"""
        try:
            from google import genai

            client = genai.Client(api_key=config['api_key'])

            # 合并system_prompt和prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = client.models.generate_content(
                model=config['model'],
                contents=full_prompt
            )

            return response.text

        except Exception as e:
            print(f"⚠️ Gemini API调用失败: {e}")
            return None

    def _call_deepseek_api(
        self,
        config: Dict,
        prompt: str,
        system_prompt: str = "",
        **kwargs
    ) -> Optional[str]:
        """调用DeepSeek API（OpenAI兼容）"""
        # DeepSeek使用OpenAI兼容接口
        return self._call_openai_api(config, prompt, system_prompt, **kwargs)

    def test_module_connection(self, module_name: str) -> bool:
        """
        测试模块API连接

        Args:
            module_name: 模块名称

        Returns:
            连接是否成功
        """
        print(f"\n🔍 测试模块: {module_name}")

        config = self.config_manager.get_module_config(module_name)

        if not config:
            print(f"❌ 模块 {module_name} 不存在")
            return False

        if not config.get('enabled'):
            print(f"⚠️ 模块 {module_name} 未启用")
            return False

        print(f"📋 提供商: {config.get('provider')}")
        print(f"📋 模型: {config.get('model')}")
        print(f"🔍 正在测试连接...")

        # 使用简单的测试提示词
        test_prompt = "请回复：连接成功"
        response = self.call_module_api(module_name, test_prompt)

        if response:
            print(f"✅ 连接测试成功")
            return True
        else:
            print(f"❌ 连接测试失败")
            return False


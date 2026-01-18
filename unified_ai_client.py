
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一AI客户端
支持多种AI提供商和中转服务
"""

import json
from typing import Optional, Dict, Any
from unified_config import unified_config

class UnifiedAIClient:
    """统一AI客户端"""
    
    def __init__(self):
        self.client = None
        self.provider_type = None
        
    def _initialize_client(self):
        """初始化AI客户端"""
        if not unified_config.is_enabled():
            return False
            
        config = unified_config.config
        
        # 确定provider类型
        api_type = config.get('api_type', 'proxy')
        model_provider = config.get('model_provider', 'openai')
        
        try:
            if api_type == 'gemini_official' or model_provider == 'gemini':
                self._init_gemini_client(config)
                self.provider_type = 'gemini'
            else:
                self._init_openai_compatible_client(config)
                self.provider_type = 'openai_compatible'
            
            return True
            
        except Exception as e:
            print(f"❌ AI客户端初始化失败: {e}")
            return False
    
    def _init_gemini_client(self, config: Dict[str, Any]):
        """初始化Gemini客户端"""
        try:
            from google import genai
            self.client = genai.Client(api_key=config['api_key'])
            self.provider_type = 'gemini'
        except ImportError:
            raise Exception("需要安装: pip install google-genai")
    
    def _init_openai_compatible_client(self, config: Dict[str, Any]):
        """初始化OpenAI兼容客户端"""
        try:
            from openai import OpenAI
            
            client_kwargs = {'api_key': config['api_key']}
            
            if 'base_url' in config:
                client_kwargs['base_url'] = config['base_url']
            
            self.client = OpenAI(**client_kwargs)
            self.provider_type = 'openai_compatible'
        except ImportError:
            raise Exception("需要安装: pip install openai")
    
    def call_ai(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """调用AI分析"""
        if not unified_config.is_enabled():
            print("❌ AI未启用")
            return None
        
        # 初始化客户端
        if not self.client:
            if not self._initialize_client():
                print("❌ AI客户端初始化失败")
                return None
        
        config = unified_config.config
        
        try:
            if self.provider_type == 'gemini':
                return self._call_gemini(prompt, system_prompt, config)
            elif self.provider_type == 'openai_compatible':
                return self._call_openai_compatible(prompt, system_prompt, config)
            else:
                print(f"❌ 未知的provider类型: {self.provider_type}")
                return None
                
        except Exception as e:
            print(f"❌ AI调用失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _call_gemini(self, prompt: str, system_prompt: str, config: Dict[str, Any]) -> str:
        """调用Gemini API"""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = self.client.models.generate_content(
            model=config['model'],
            contents=full_prompt
        )
        
        return response.text
    
    def _call_openai_compatible(self, prompt: str, system_prompt: str, config: Dict[str, Any]) -> str:
        """调用OpenAI兼容API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # 准备请求参数
        request_params = {
            'model': config['model'],
            'messages': messages,
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
        # 添加额外headers
        if 'extra_headers' in config and config['extra_headers']:
            request_params['extra_headers'] = config['extra_headers']
        
        completion = self.client.chat.completions.create(**request_params)
        
        return completion.choices[0].message.content
    
    def test_connection(self) -> bool:
        """测试AI连接"""
        try:
            response = self.call_ai("Hello", "You are a helpful assistant.")
            return response is not None and len(response) > 0
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False

# 全局AI客户端实例
ai_client = UnifiedAIClient()

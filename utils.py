
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用工具函数
"""

import os
import re
import json
from typing import Dict, Any, List, Optional

def extract_episode_number(filename: str) -> str:
    """从SRT文件名提取集数，使用字符串排序"""
    # 直接使用文件名（去掉扩展名）作为集数标识
    # 这样可以保持原始的字符串排序顺序
    base_name = os.path.splitext(filename)[0]
    return base_name

def get_srt_files_sorted() -> List[str]:
    """获取排序后的SRT文件列表"""
    srt_files = [f for f in os.listdir('.') if f.endswith('.srt') or f.endswith('.txt')]
    # 按字符串排序，这样可以保持电视剧的正确顺序
    return sorted(srt_files)

def load_ai_config() -> Dict[str, Any]:
    """加载AI配置"""
    config_file = '.ai_config.json'
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
    except Exception as e:
        print(f"⚠ 加载AI配置失败: {e}")
    
    return {'enabled': False}

def save_ai_config(config: Dict[str, Any]) -> bool:
    """保存AI配置"""
    config_file = '.ai_config.json'
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ AI配置已保存到 {config_file}")
        return True
    except Exception as e:
        print(f"⚠ 保存AI配置失败: {e}")
        return False

def validate_ai_config(config: Dict[str, Any]) -> bool:
    """验证AI配置的有效性"""
    if not config.get('enabled', False):
        return False
    
    required_fields = ['api_type', 'model_provider', 'api_key', 'model']
    
    for field in required_fields:
        if not config.get(field):
            print(f"❌ 配置缺少必需字段: {field}")
            return False
    
    # 检查api_type特定的配置
    api_type = config.get('api_type')
    
    if api_type == 'proxy':
        if not config.get('proxy_provider'):
            print("❌ 中转API需要指定proxy_provider")
            return False
        if not config.get('base_url'):
            print("❌ 中转API需要指定base_url")
            return False
    
    elif api_type == 'official':
        model_provider = config.get('model_provider')
        if model_provider != 'gemini' and not config.get('base_url'):
            print("❌ 官方API（除Gemini外）需要指定base_url")
            return False
    
    return True

def format_time_to_seconds(time_str: str) -> float:
    """将时间字符串转换为秒数"""
    try:
        # 格式: "00:01:30,500" -> 90.5秒
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        
        total_seconds = h * 3600 + m * 60 + s + ms / 1000.0
        return total_seconds
    except:
        return 0.0

def seconds_to_time_format(seconds: float) -> str:
    """将秒数转换为时间格式字符串"""
    try:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"
    except:
        return "00:00:00,000"

def clean_text(text: str) -> str:
    """清理文本内容"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 移除特殊字符（保留中文、英文、数字、常用标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？：；""''（）【】《》、\-\.]+', '', text)
    
    return text

def ensure_directory(path: str) -> bool:
    """确保目录存在"""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except Exception as e:
        print(f"⚠ 创建目录失败 {path}: {e}")
        return False

def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0

def print_config_help():
    """打印配置帮助信息"""
    print("\n📋 AI配置说明")
    print("=" * 40)
    print("1. 配置文件位置: .ai_config.json")
    print("2. 配置模板文件: config_template.json")
    print("3. 支持的模型类型:")
    print("   - openai: GPT系列模型")
    print("   - gemini: Google Gemini系列")
    print("   - deepseek: DeepSeek系列")
    print("   - claude: Anthropic Claude系列")
    print("4. 接口类型:")
    print("   - official: 官方API")
    print("   - proxy: 中转API")
    print("5. 中转服务商:")
    print("   - chataiapi: ChatAI API (推荐)")
    print("   - openrouter: OpenRouter")
    print("   - suanli: 算力云")
    print("   - custom: 自定义")

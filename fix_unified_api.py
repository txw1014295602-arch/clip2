
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一API配置修复脚本 - 确保所有组件使用相同的配置格式
"""

import os
import json
import re

def fix_ai_config_consistency():
    """修复AI配置一致性问题"""
    print("🔧 修复AI配置一致性问题")
    print("=" * 50)
    
    # 检查配置文件
    config_file = '.ai_config.json'
    if not os.path.exists(config_file):
        print("❌ 未找到AI配置文件")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return False
    
    print(f"📋 当前配置:")
    print(f"  启用状态: {config.get('enabled', False)}")
    print(f"  服务商: {config.get('provider', '未知')}")
    print(f"  模型: {config.get('model', '未知')}")
    print(f"  API地址: {config.get('base_url') or config.get('url', '未知')}")
    
    # 统一配置字段
    fixes_applied = []
    
    # 修复 url -> base_url
    if 'url' in config and 'base_url' not in config:
        config['base_url'] = config['url']
        del config['url']
        fixes_applied.append("url -> base_url")
    
    # 确保 api_type 字段存在
    if 'api_type' not in config:
        if config.get('provider') == 'gemini_official':
            config['api_type'] = 'gemini_official'
        else:
            config['api_type'] = 'openai_compatible'
        fixes_applied.append("添加 api_type")
    
    # 确保 extra_headers 字段存在
    if 'extra_headers' not in config:
        config['extra_headers'] = {}
        fixes_applied.append("添加 extra_headers")
    
    # 保存修复后的配置
    if fixes_applied:
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已修复: {', '.join(fixes_applied)}")
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False
    else:
        print("✅ 配置格式正确，无需修复")
    
    return True

def find_ai_usage_in_files():
    """查找所有使用AI分析的文件"""
    ai_usage_files = []
    
    for file in os.listdir('.'):
        if file.endswith('.py'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含AI分析相关代码
                ai_patterns = [
                    r'ai_analyze',
                    r'call_ai_api',
                    r'config_helper\.call',
                    r'openai\..*completions',
                    r'base_url.*chat/completions'
                ]
                
                for pattern in ai_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        ai_usage_files.append(file)
                        break
                        
            except:
                continue
    
    return ai_usage_files

def validate_api_consistency():
    """验证API使用一致性"""
    print("\n🔍 检查API使用一致性")
    print("-" * 30)
    
    ai_files = find_ai_usage_in_files()
    print(f"发现 {len(ai_files)} 个使用AI的文件:")
    
    for file in ai_files:
        print(f"  📄 {file}")
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查配置使用模式
            issues = []
            
            # 检查是否使用了过时的字段
            if re.search(r'config\.get\([\'"]url[\'"]', content):
                issues.append("使用了过时的 'url' 字段")
            
            # 检查是否直接使用了requests而不是config_helper
            if 'import requests' in content and 'config_helper.call_ai_api' not in content:
                if 'chat/completions' in content:
                    issues.append("直接使用requests而非config_helper")
            
            if issues:
                print(f"    ⚠️ 问题: {', '.join(issues)}")
            else:
                print(f"    ✅ 配置使用正确")
                
        except Exception as e:
            print(f"    ❌ 检查失败: {e}")

if __name__ == "__main__":
    print("🔧 统一API配置修复工具")
    print("=" * 50)
    
    # 修复配置文件
    if fix_ai_config_consistency():
        # 验证代码一致性
        validate_api_consistency()
        
        print("\n✅ 修复完成！")
        print("💡 建议:")
        print("  1. 所有AI分析现在统一使用 config_helper.call_ai_api()")
        print("  2. 配置字段已统一为 base_url, api_type, extra_headers")
        print("  3. 支持官方API和中转API的自动识别")
    else:
        print("❌ 修复失败，请检查配置")

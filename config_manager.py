#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块 - 支持多模块独立配置
统一管理AI配置、项目配置等
"""

import os
import json
from typing import Dict, Optional, List


class ConfigManager:
    """配置管理器 - 支持多模块独立配置"""

    def __init__(self, config_file: str = '.config.json'):
        """初始化配置管理器"""
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 如果是旧格式配置，自动迁移
                    if 'ai' in config and 'modules' not in config:
                        return self._migrate_old_config(config)
                    return config
            except Exception as e:
                print(f"⚠️ 配置加载失败: {e}")

        # 默认配置 - 新的多模块格式
        return {
            'modules': {
                'speech_to_text': {
                    'enabled': False,
                    'provider': 'openai',
                    'api_key': '',
                    'base_url': 'https://api.openai.com/v1',
                    'model': 'whisper-1',
                    'language': 'zh'
                },
                'content_analysis': {
                    'enabled': False,
                    'provider': 'gemini',
                    'api_key': '',
                    'base_url': '',
                    'model': 'gemini-2.0-flash-exp'
                },
                'subtitle_generation': {
                    'enabled': False,
                    'provider': 'deepseek',
                    'api_key': '',
                    'base_url': 'https://api.deepseek.com',
                    'model': 'deepseek-chat'
                }
            },
            'paths': {
                'input_videos': 'videos',
                'audio_cache': 'audio_cache',
                'srt_folder': 'srt',
                'output_clips': 'clips',
                'analysis_cache': 'cache'
            },
            'processing': {
                'audio_format': 'mp3',
                'audio_quality': '192k',
                'max_clips_per_video': 8,
                'min_clip_duration': 30,
                'max_clip_duration': 300
            }
        }

    def _migrate_old_config(self, old_config: Dict) -> Dict:
        """迁移旧配置格式到新格式"""
        print("🔄 检测到旧配置格式，正在自动迁移...")

        new_config = self._load_config()  # 获取默认新格式

        # 迁移旧的AI配置到content_analysis模块
        if old_config.get('ai', {}).get('enabled'):
            old_ai = old_config['ai']
            new_config['modules']['content_analysis'] = {
                'enabled': True,
                'provider': old_ai.get('provider', 'gemini'),
                'api_key': old_ai.get('api_key', ''),
                'base_url': old_ai.get('base_url', ''),
                'model': old_ai.get('model', 'gemini-2.0-flash-exp')
            }

        # 迁移路径配置
        if 'paths' in old_config:
            old_paths = old_config['paths']
            new_config['paths'].update({
                'input_videos': old_paths.get('videos_folder', 'videos'),
                'srt_folder': old_paths.get('srt_folder', 'srt'),
                'output_clips': old_paths.get('output_folder', 'clips'),
                'analysis_cache': old_paths.get('cache_folder', 'cache')
            })

        # 保存迁移后的配置
        self.config = new_config
        self.save_config()
        print("✅ 配置迁移完成")

        return new_config

    def save_config(self) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    # ========== 新的多模块配置方法 ==========

    def get_module_config(self, module_name: str) -> Optional[Dict]:
        """获取指定模块的配置"""
        return self.config.get('modules', {}).get(module_name)

    def set_module_config(self, module_name: str, module_config: Dict) -> bool:
        """设置指定模块的配置"""
        if 'modules' not in self.config:
            self.config['modules'] = {}
        self.config['modules'][module_name] = module_config
        return self.save_config()

    def get_all_modules(self) -> Dict:
        """获取所有模块配置"""
        return self.config.get('modules', {})

    def is_module_enabled(self, module_name: str) -> bool:
        """检查模块是否启用"""
        module = self.get_module_config(module_name)
        return module.get('enabled', False) if module else False

    def enable_module(self, module_name: str) -> bool:
        """启用指定模块"""
        module = self.get_module_config(module_name)
        if module:
            module['enabled'] = True
            return self.save_config()
        return False

    def disable_module(self, module_name: str) -> bool:
        """禁用指定模块"""
        module = self.get_module_config(module_name)
        if module:
            module['enabled'] = False
            return self.save_config()
        return False

    def get_enabled_modules(self) -> List[str]:
        """获取所有已启用的模块名称"""
        modules = self.get_all_modules()
        return [name for name, config in modules.items() if config.get('enabled', False)]

    # ========== 兼容旧接口的方法 ==========

    def get_ai_config(self) -> Dict:
        """获取AI配置（兼容旧接口，返回content_analysis模块配置）"""
        return self.get_module_config('content_analysis') or {}

    def set_ai_config(self, ai_config: Dict) -> bool:
        """设置AI配置（兼容旧接口，设置content_analysis模块）"""
        return self.set_module_config('content_analysis', ai_config)

    # ========== 路径和处理配置方法 ==========

    def get_paths(self) -> Dict:
        """获取路径配置"""
        return self.config.get('paths', {})

    def set_paths(self, paths: Dict) -> bool:
        """设置路径配置"""
        self.config['paths'] = paths
        return self.save_config()

    def get_processing_config(self) -> Dict:
        """获取处理配置"""
        return self.config.get('processing', {})

    def set_processing_config(self, processing: Dict) -> bool:
        """设置处理配置"""
        self.config['processing'] = processing
        return self.save_config()

    # ========== 工具方法 ==========

    def create_directories(self) -> bool:
        """创建所有必要的目录"""
        try:
            paths = self.get_paths()
            for path_key, path_value in paths.items():
                if path_value and not os.path.exists(path_value):
                    os.makedirs(path_value, exist_ok=True)
                    print(f"📁 创建目录: {path_value}")
            return True
        except Exception as e:
            print(f"❌ 创建目录失败: {e}")
            return False

    def validate_module_config(self, module_name: str) -> tuple[bool, str]:
        """验证模块配置是否完整"""
        module = self.get_module_config(module_name)

        if not module:
            return False, f"模块 {module_name} 不存在"

        if not module.get('enabled'):
            return False, f"模块 {module_name} 未启用"

        required_fields = ['provider', 'api_key', 'model']
        for field in required_fields:
            if not module.get(field):
                return False, f"模块 {module_name} 缺少必要字段: {field}"

        return True, "配置有效"

    def export_config(self, export_path: str) -> bool:
        """导出配置到文件"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"✅ 配置已导出到: {export_path}")
            return True
        except Exception as e:
            print(f"❌ 配置导出失败: {e}")
            return False

    def import_config(self, import_path: str) -> bool:
        """从文件导入配置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # 验证配置格式
            if 'modules' in imported_config:
                self.config = imported_config
                self.save_config()
                print(f"✅ 配置已从 {import_path} 导入")
                return True
            else:
                print("❌ 配置文件格式不正确")
                return False
        except Exception as e:
            print(f"❌ 配置导入失败: {e}")
            return False

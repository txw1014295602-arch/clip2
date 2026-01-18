
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
纯后端智能视频剪辑系统
功能：
1. 引导用户配置AI接口
2. 一键智能剪辑视频
3. 批量处理所有文件
4. 智能缓存和一致性保证
"""

import os
import json
import sys
from typing import Dict, List, Optional

class BackendVideoClipperSystem:
    """后端视频剪辑系统"""
    
    def __init__(self):
        self.config_file = '.ai_config.json'
        self.srt_folder = "movie_srt"
        self.videos_folder = "movie_videos"
        self.clips_folder = "movie_clips"
        self.analysis_folder = "movie_analysis"
        
        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, self.analysis_folder]:
            os.makedirs(folder, exist_ok=True)
        
        print("🎬 智能视频剪辑系统 - 后端服务")
        print("=" * 60)
        print("✨ 核心功能:")
        print("• 🤖 AI接口智能配置")
        print("• 🎬 一键视频剪辑")
        print("• 📊 批量处理")
        print("• 💾 智能缓存")
        print("=" * 60)

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        return config
        except Exception as e:
            print(f"⚠️ 配置加载失败: {e}")
        return {'enabled': False}

    def guided_ai_setup(self) -> bool:
        """引导式AI配置"""
        print("\n🤖 AI接口配置向导")
        print("=" * 40)
        
        # 检查现有配置
        current_config = self.load_ai_config()
        if current_config.get('enabled'):
            print("✅ 发现现有AI配置:")
            print(f"   提供商: {current_config.get('provider', '未知')}")
            print(f"   模型: {current_config.get('model', '未知')}")
            
            use_existing = input("\n是否使用现有配置？(Y/n): ").strip().lower()
            if use_existing not in ['n', 'no', '否']:
                print("✅ 使用现有配置")
                return True
        
        print("\n🚀 选择AI服务类型:")
        print("1. 🌐 中转API (推荐 - 稳定便宜)")
        print("2. 🔒 官方API (OpenAI/Gemini等)")
        print("3. 📋 快速预设配置")
        print("0. ❌ 跳过配置")
        
        while True:
            choice = input("\n请选择 (0-3): ").strip()
            
            if choice == '0':
                print("⚠️ 跳过AI配置，将无法进行智能分析")
                return False
            elif choice == '1':
                return self._setup_proxy_api()
            elif choice == '2':
                return self._setup_official_api()
            elif choice == '3':
                return self._setup_preset_config()
            else:
                print("❌ 无效选择，请输入0-3")

    def _setup_proxy_api(self) -> bool:
        """设置中转API"""
        print("\n🌐 中转API配置")
        print("推荐服务商:")
        print("• ChatAI: https://www.chataiapi.com/")
        print("• OpenRouter: https://openrouter.ai/")
        print("• SiliconFlow: https://siliconflow.cn/")
        
        base_url = input("\nAPI地址 (如: https://www.chataiapi.com/v1): ").strip()
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
        
        return self._save_config(config)

    def _setup_official_api(self) -> bool:
        """设置官方API"""
        print("\n🔒 官方API配置")
        print("1. Google Gemini")
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
        """设置Gemini"""
        print("\n📡 Google Gemini配置")
        api_key = input("请输入Gemini API密钥: ").strip()
        if not api_key:
            return False
        
        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': 'gemini-2.0-flash-exp'
        }
        return self._save_config(config)

    def _setup_openai(self) -> bool:
        """设置OpenAI"""
        print("\n🤖 OpenAI配置")
        api_key = input("请输入OpenAI API密钥: ").strip()
        if not api_key:
            return False
        
        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'openai',
            'api_key': api_key,
            'model': 'gpt-4'
        }
        return self._save_config(config)

    def _setup_claude(self) -> bool:
        """设置Claude"""
        print("\n🎭 Claude配置")
        api_key = input("请输入Anthropic API密钥: ").strip()
        if not api_key:
            return False
        
        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'claude',
            'api_key': api_key,
            'model': 'claude-3-5-sonnet-20241022'
        }
        return self._save_config(config)

    def _setup_preset_config(self) -> bool:
        """快速预设配置"""
        print("\n📋 快速预设配置")
        presets = {
            '1': {
                'name': 'ChatAI (DeepSeek-R1)',
                'base_url': 'https://www.chataiapi.com/v1',
                'model': 'deepseek-r1'
            },
            '2': {
                'name': 'OpenRouter (Claude)',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'anthropic/claude-3.5-sonnet'
            },
            '3': {
                'name': 'SiliconFlow (DeepSeek)',
                'base_url': 'https://api.siliconflow.cn/v1',
                'model': 'deepseek-ai/DeepSeek-V2.5'
            }
        }
        
        for key, preset in presets.items():
            print(f"{key}. {preset['name']}")
        
        while True:
            choice = input("\n请选择预设 (1-3): ").strip()
            if choice in presets:
                preset = presets[choice]
                print(f"\n选择了: {preset['name']}")
                
                api_key = input("请输入API密钥: ").strip()
                if not api_key:
                    return False
                
                config = {
                    'enabled': True,
                    'api_type': 'proxy',
                    'provider': 'preset',
                    'base_url': preset['base_url'],
                    'api_key': api_key,
                    'model': preset['model']
                }
                return self._save_config(config)
            else:
                print("❌ 无效选择，请输入1-3")

    def _save_config(self, config: Dict) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"✅ AI配置保存成功: {config.get('provider')}")
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    def check_file_status(self) -> Dict:
        """检查文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) 
                    if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        video_files = []
        if os.path.exists(self.videos_folder):
            video_files = [f for f in os.listdir(self.videos_folder) 
                          if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'))]
        
        return {
            'srt_files': srt_files,
            'video_files': video_files,
            'srt_count': len(srt_files),
            'video_count': len(video_files)
        }

    def one_click_intelligent_clipping(self) -> bool:
        """一键智能剪辑"""
        print("\n🚀 一键智能剪辑启动")
        print("=" * 50)
        
        # 检查AI配置
        ai_config = self.load_ai_config()
        if not ai_config.get('enabled'):
            print("❌ 需要AI配置才能进行智能分析")
            print("💡 请先配置AI接口")
            return False
        
        print(f"✅ AI已配置: {ai_config.get('provider')}")
        
        # 检查文件状态
        file_status = self.check_file_status()
        
        if file_status['srt_count'] == 0:
            print(f"❌ 未在 {self.srt_folder}/ 目录找到字幕文件")
            print("💡 请将字幕文件(.srt/.txt)放入该目录")
            return False
        
        print(f"📝 找到 {file_status['srt_count']} 个字幕文件")
        print(f"🎬 找到 {file_status['video_count']} 个视频文件")
        
        if file_status['video_count'] == 0:
            print("⚠️ 未找到视频文件，将仅进行分析")
        
        # 开始处理
        print(f"\n🎬 开始智能剪辑处理...")
        
        try:
            # 导入剪辑系统
            from clean_main import MovieAIClipperSystem
            
            clipper = MovieAIClipperSystem()
            clipper.ai_config = ai_config  # 使用已配置的AI
            
            # 执行批量处理
            clipper.process_all_movies()
            
            print(f"\n🎉 智能剪辑完成！")
            print(f"📁 输出目录: {self.clips_folder}/")
            print(f"📊 分析报告: {self.analysis_folder}/")
            
            return True
            
        except Exception as e:
            print(f"❌ 剪辑过程出错: {e}")
            return False

    def show_main_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("🎬 智能视频剪辑系统 - 后端控制台")
            print("=" * 60)
            
            # 显示状态
            ai_config = self.load_ai_config()
            ai_status = "✅ 已配置" if ai_config.get('enabled') else "❌ 未配置"
            print(f"🤖 AI状态: {ai_status}")
            
            file_status = self.check_file_status()
            print(f"📝 字幕文件: {file_status['srt_count']} 个")
            print(f"🎬 视频文件: {file_status['video_count']} 个")
            
            print(f"\n🎯 操作选项:")
            print("1. 🤖 配置AI接口")
            print("2. 🚀 一键智能剪辑")
            print("3. 📊 查看文件状态")
            print("4. 🔧 系统环境检查")
            print("0. ❌ 退出系统")
            
            try:
                choice = input("\n请选择操作 (0-4): ").strip()
                
                if choice == '0':
                    print("\n👋 感谢使用智能视频剪辑系统！")
                    break
                elif choice == '1':
                    self.guided_ai_setup()
                elif choice == '2':
                    self.one_click_intelligent_clipping()
                elif choice == '3':
                    self._show_detailed_file_status()
                elif choice == '4':
                    self._check_system_environment()
                else:
                    print("❌ 无效选择，请输入0-4")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")

    def _show_detailed_file_status(self):
        """显示详细文件状态"""
        print(f"\n📊 详细文件状态")
        print("=" * 40)
        
        file_status = self.check_file_status()
        
        print(f"📝 字幕文件 ({file_status['srt_count']} 个):")
        if file_status['srt_files']:
            for i, f in enumerate(file_status['srt_files'][:10], 1):
                print(f"   {i}. {f}")
            if len(file_status['srt_files']) > 10:
                print(f"   ... 还有 {len(file_status['srt_files'])-10} 个")
        else:
            print(f"   ❌ {self.srt_folder}/ 目录为空")
        
        print(f"\n🎬 视频文件 ({file_status['video_count']} 个):")
        if file_status['video_files']:
            for i, f in enumerate(file_status['video_files'][:10], 1):
                print(f"   {i}. {f}")
            if len(file_status['video_files']) > 10:
                print(f"   ... 还有 {len(file_status['video_files'])-10} 个")
        else:
            print(f"   ❌ {self.videos_folder}/ 目录为空")

    def _check_system_environment(self):
        """检查系统环境"""
        print(f"\n🔧 系统环境检查")
        print("=" * 40)
        
        # 检查目录
        directories = [
            (self.srt_folder, "字幕目录"),
            (self.videos_folder, "视频目录"),
            (self.clips_folder, "输出目录"),
            (self.analysis_folder, "分析目录")
        ]
        
        for directory, name in directories:
            status = "✅ 存在" if os.path.exists(directory) else "❌ 不存在"
            print(f"📁 {name}: {directory}/ {status}")
        
        # 检查AI配置
        ai_config = self.load_ai_config()
        ai_status = "✅ 已配置" if ai_config.get('enabled') else "❌ 未配置"
        print(f"🤖 AI配置: {ai_status}")
        
        if ai_config.get('enabled'):
            print(f"   提供商: {ai_config.get('provider')}")
            print(f"   模型: {ai_config.get('model')}")
        
        # 检查FFmpeg
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            ffmpeg_status = "✅ 已安装" if result.returncode == 0 else "❌ 未安装"
        except:
            ffmpeg_status = "❌ 未安装或不可用"
        
        print(f"🎬 FFmpeg: {ffmpeg_status}")
        
        # 检查Python依赖
        required_modules = ['requests', 'json', 're', 'os', 'subprocess']
        print(f"\n📦 Python依赖:")
        for module in required_modules:
            try:
                __import__(module)
                print(f"   ✅ {module}")
            except ImportError:
                print(f"   ❌ {module}")

def main():
    """主函数"""
    try:
        system = BackendVideoClipperSystem()
        system.show_main_menu()
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

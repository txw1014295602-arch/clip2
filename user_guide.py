
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户引导和配置系统
帮助用户快速配置和使用智能电视剧剪辑系统
"""

import os
import json
from typing import Dict, Optional

class UserGuideSystem:
    """用户引导系统"""
    
    def __init__(self):
        self.config_file = "user_config.json"
        self.config = self.load_user_config()
    
    def load_user_config(self) -> Dict:
        """加载用户配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "ai_enabled": False,
            "api_provider": "none",
            "api_key": "",
            "model": "",
            "base_url": "",
            "剧情分析模式": "智能分析",
            "每集片段数量": 3,
            "片段时长": "2-3分钟",
            "错别字修正": True,
            "跨集连贯性": True,
            "第三人称旁白": True
        }
    
    def save_config(self, config: Dict):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ 配置已保存")
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    def welcome_guide(self):
        """欢迎引导"""
        print("🎬 智能电视剧剪辑系统")
        print("=" * 60)
        print("🎯 系统功能：")
        print("• 智能分析电视剧字幕，自动识别剧情类型")
        print("• 按剧情点分剪短视频（关键冲突、人物转折、线索揭露）")
        print("• 支持非连续时间段的智能合并剪辑")
        print("• 自动生成第三人称旁白字幕")
        print("• 跨集连贯性分析和衔接说明")
        print("• 智能错别字修正（防衛→防卫，正當→正当等）")
        print("• 固定输出格式，便于剪辑参考")
        print("=" * 60)
    
    def check_directory_structure(self):
        """检查目录结构"""
        print("\n📁 检查目录结构...")
        
        required_dirs = {
            'srt': '字幕文件目录（.srt/.txt文件）',
            'videos': '视频文件目录（.mp4/.mkv等）',
            'clips': '输出剪辑目录（自动创建）',
            'reports': '分析报告目录（自动创建）',
            'cache': '缓存目录（自动创建）'
        }
        
        all_ready = True
        for dir_name, description in required_dirs.items():
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f"✓ 创建目录: {dir_name}/ - {description}")
            else:
                print(f"✓ 目录存在: {dir_name}/ - {description}")
        
        # 检查字幕文件
        srt_files = [f for f in os.listdir('srt') if f.endswith(('.srt', '.txt'))] if os.path.exists('srt') else []
        if srt_files:
            print(f"✅ 找到 {len(srt_files)} 个字幕文件")
            for f in srt_files[:3]:  # 显示前3个
                print(f"   📝 {f}")
            if len(srt_files) > 3:
                print(f"   ... 和其他 {len(srt_files)-3} 个文件")
        else:
            print("⚠️ srt/ 目录中未找到字幕文件")
            print("   请将字幕文件（.srt 或 .txt）放入 srt/ 目录")
            all_ready = False
        
        # 检查视频文件
        video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        video_files = []
        if os.path.exists('videos'):
            video_files = [f for f in os.listdir('videos') 
                          if any(f.lower().endswith(ext) for ext in video_exts)]
        
        if video_files:
            print(f"✅ 找到 {len(video_files)} 个视频文件")
            for f in video_files[:3]:  # 显示前3个
                print(f"   🎬 {f}")
            if len(video_files) > 3:
                print(f"   ... 和其他 {len(video_files)-3} 个文件")
        else:
            print("⚠️ videos/ 目录中未找到视频文件")
            print("   请将视频文件放入 videos/ 目录")
            all_ready = False
        
        return all_ready
    
    def ai_config_guide(self):
        """AI配置引导"""
        print("\n🤖 AI配置（可选）")
        print("-" * 40)
        print("AI功能可以提升分析精度，但不是必需的")
        print("系统内置智能规则分析，无AI也能正常工作")
        
        use_ai = input("\n是否配置AI功能？(y/N): ").lower().strip()
        
        if use_ai in ['y', 'yes']:
            providers = {
                '1': ('OpenAI', 'https://api.openai.com/v1/chat/completions'),
                '2': ('OpenRouter', 'https://openrouter.ai/api/v1/chat/completions'),
                '3': ('通义千问', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'),
                '4': ('豆包', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'),
                '5': ('自定义', '')
            }
            
            print("\n选择AI服务提供商：")
            for key, (name, _) in providers.items():
                print(f"{key}. {name}")
            
            choice = input("请选择 (1-5): ").strip()
            
            if choice in providers:
                provider_name, default_url = providers[choice]
                
                api_key = input(f"\n请输入 {provider_name} API密钥: ").strip()
                if not api_key:
                    print("❌ 未输入API密钥，跳过AI配置")
                    return
                
                if choice == '5':  # 自定义
                    base_url = input("请输入API地址: ").strip()
                    model = input("请输入模型名称: ").strip()
                else:
                    base_url = default_url
                    if choice == '1':  # OpenAI
                        model = 'gpt-3.5-turbo'
                    elif choice == '2':  # OpenRouter
                        model = 'anthropic/claude-3-haiku'
                    elif choice == '3':  # 通义千问
                        model = 'qwen-turbo'
                    elif choice == '4':  # 豆包
                        model = 'ep-20241230181419-ql9vs'
                    else:
                        model = input("请输入模型名称: ").strip()
                
                # 保存AI配置
                ai_config = {
                    "enabled": True,
                    "provider": provider_name.lower(),
                    "api_key": api_key,
                    "model": model,
                    "url": base_url
                }
                
                with open('.ai_config.json', 'w', encoding='utf-8') as f:
                    json.dump(ai_config, f, ensure_ascii=False, indent=2)
                
                print(f"✅ AI配置完成: {provider_name} - {model}")
                self.config["ai_enabled"] = True
                self.config["api_provider"] = provider_name
            else:
                print("❌ 无效选择，跳过AI配置")
        else:
            print("✅ 使用内置智能规则分析")
    
    def show_usage_examples(self):
        """显示使用示例"""
        print("\n📋 使用示例")
        print("-" * 40)
        print("文件命名建议：")
        print("  字幕文件: E01.srt, E02.srt, EP01.txt, 第01集.srt")
        print("  视频文件: E01.mp4, E02.mkv, EP01.avi")
        print("  (系统会自动匹配对应的字幕和视频文件)")
        
        print("\n输出示例：")
        print("  clips/E01_关键冲突_1.mp4 - 剧情冲突片段")
        print("  clips/E01_关键冲突_1_片段说明.txt - 详细说明")
        print("  reports/完整剪辑报告.txt - 整体分析报告")
        
        print("\n特色功能：")
        print("• 错别字自动修正: 防衛→防卫, 正當→正当")
        print("• 智能剧情类型识别: 法律剧、爱情剧、悬疑剧等")
        print("• 跨集连贯性: 每集结尾生成与下集的衔接说明")
        print("• 第三人称旁白: 为每个片段生成专业解说")
    
    def start_processing_guide(self):
        """开始处理引导"""
        print("\n🚀 开始处理")
        print("-" * 40)
        print("处理流程：")
        print("1. 📖 解析字幕文件，修正错别字")
        print("2. 🎭 智能识别剧情类型和关键剧情点")
        print("3. 🎯 提取精彩片段（关键冲突、人物转折、线索揭露）")
        print("4. 🎬 自动剪辑视频片段")
        print("5. 📝 生成第三人称旁白和详细说明")
        print("6. 🔗 分析跨集连贯性和衔接点")
        print("7. 📄 生成完整分析报告")
        
        ready = input("\n准备开始处理? (Y/n): ").lower().strip()
        return ready not in ['n', 'no']
    
    def run_complete_guide(self):
        """运行完整引导流程"""
        self.welcome_guide()
        
        # 检查目录结构
        structure_ready = self.check_directory_structure()
        
        if not structure_ready:
            print("\n❌ 请先准备好必要的文件")
            print("\n📋 准备步骤:")
            print("1. 将字幕文件放入 srt/ 目录")
            print("2. 将对应的视频文件放入 videos/ 目录")
            print("3. 确保文件名能够匹配（如 E01.srt 对应 E01.mp4）")
            return False
        
        # AI配置引导
        self.ai_config_guide()
        
        # 显示使用示例
        self.show_usage_examples()
        
        # 开始处理引导
        if self.start_processing_guide():
            self.save_config(self.config)
            return True
        else:
            print("✋ 处理已取消")
            return False

def main():
    """主函数"""
    guide = UserGuideSystem()
    
    if guide.run_complete_guide():
        print("\n🎬 启动智能剪辑系统...")
        # 导入并运行主系统
        try:
            from clean_main import main as clipper_main
            clipper_main()
        except ImportError:
            print("❌ 系统文件缺失，请检查 clean_main.py")
        except Exception as e:
            print(f"❌ 系统运行出错: {e}")

if __name__ == "__main__":
    main()

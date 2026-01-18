
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI驱动电影剪辑系统启动器
满足用户7个核心需求的完整解决方案
"""

import os
import json

def check_ai_config():
    """检查AI配置"""
    try:
        with open('.ai_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            if config.get('enabled') and config.get('api_key'):
                return True, config
    except:
        pass
    return False, {}

def setup_ai_config():
    """设置AI配置"""
    print("🤖 100% AI驱动系统需要配置AI接口")
    print("=" * 50)
    
    print("支持的AI服务商：")
    print("1. OpenAI (ChatGPT)")
    print("2. Anthropic (Claude)")
    print("3. DeepSeek")
    print("4. 通义千问")
    print("5. 中转API")
    
    while True:
        try:
            choice = input("\n请选择AI服务商 (1-5): ").strip()
            
            configs = {
                '1': ('OpenAI', 'https://api.openai.com/v1', 'gpt-4'),
                '2': ('Anthropic', 'https://api.anthropic.com/v1', 'claude-3-haiku-20240307'),
                '3': ('DeepSeek', 'https://api.deepseek.com/v1', 'deepseek-chat'),
                '4': ('通义千问', 'https://dashscope.aliyuncs.com/api/v1', 'qwen-turbo'),
                '5': (None, None, None)
            }
            
            if choice in configs:
                provider, base_url, model = configs[choice]
                
                if choice == '5':
                    provider = '中转API'
                    base_url = input("请输入中转API地址: ").strip()
                    model = input("请输入模型名称: ").strip()
                
                break
            else:
                print("❌ 无效选择，请输入1-5")
        except KeyboardInterrupt:
            print("\n👋 取消配置")
            return False
    
    api_key = input(f"\n请输入{provider} API密钥: ").strip()
    
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    config = {
        'enabled': True,
        'provider': provider,
        'base_url': base_url,
        'api_key': api_key,
        'model': model
    }
    
    try:
        with open('.ai_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ AI配置已保存: {provider}")
        return True
        
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False

def setup_directories():
    """设置目录结构"""
    directories = {
        'movie_srt': '电影字幕文件 (.srt, .txt)',
        'movie_videos': '电影视频文件 (.mp4, .mkv, .avi等)',
        'ai_movie_clips': '输出: 主人公故事视频',
        'ai_movie_analysis': '输出: AI分析报告',
        'ai_cache': '系统: AI分析缓存'
    }
    
    print("\n📁 创建目录结构...")
    for dir_name, desc in directories.items():
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ {dir_name}/ - {desc}")

def check_files():
    """检查必要文件"""
    srt_files = []
    if os.path.exists('movie_srt'):
        srt_files = [f for f in os.listdir('movie_srt') 
                     if f.lower().endswith(('.srt', '.txt')) and not f.startswith('.')]
    
    video_files = []
    if os.path.exists('movie_videos'):
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        video_files = [f for f in os.listdir('movie_videos') 
                      if any(f.lower().endswith(ext) for ext in video_extensions)]
    
    return srt_files, video_files

def show_system_features():
    """显示系统特色"""
    print("🎬 100% AI驱动电影剪辑系统")
    print("=" * 80)
    print("🎯 完全满足您的7个核心需求:")
    print()
    print("1️⃣ 字幕解析和错误修正")
    print("   • 智能多编码解析 (UTF-8, GBK, UTF-16等)")
    print("   • 自动修正繁体字和错别字")
    print("   • 格式兼容性处理")
    print()
    print("2️⃣ AI识别主人公")
    print("   • 100% AI深度分析所有角色")
    print("   • 智能判断真正的故事主角")
    print("   • 提供AI选择理由和置信度")
    print()
    print("3️⃣ 主人公完整故事线")
    print("   • 以主人公视角构建完整叙述")
    print("   • 长故事智能分割多个短视频")
    print("   • 确保故事完整性和连贯性")
    print()
    print("4️⃣ 非连续剧情点剪辑")
    print("   • 时间不连续但逻辑连贯")
    print("   • 智能合并多个时间段")
    print("   • 附带详细的第一人称字幕")
    print()
    print("5️⃣ 100% AI分析")
    print("   • 完全AI驱动，无人工规则")
    print("   • 分析失败直接返回")
    print("   • AI置信度评估")
    print()
    print("6️⃣ 固定输出格式")
    print("   • 标准化文件命名")
    print("   • 统一的报告格式")
    print("   • 完整的分析文档")
    print()
    print("7️⃣ 无声视频+实时叙述")
    print("   • 移除原声音频")
    print("   • 第一人称详细叙述")
    print("   • 视频与叙述精确同步")

def main():
    """主启动函数"""
    show_system_features()
    
    # 检查AI配置
    has_ai, ai_config = check_ai_config()
    if not has_ai:
        print("\n❌ 系统需要AI配置才能运行")
        print("⚠️ 100% AI分析要求，未配置AI将直接返回")
        
        setup_choice = input("\n是否现在配置AI？(y/n): ").strip().lower()
        if setup_choice not in ['y', 'yes', '是']:
            print("❌ 未配置AI，系统退出")
            return
        
        if not setup_ai_config():
            print("❌ AI配置失败，系统退出")
            return
        
        print("✅ AI配置成功")
    else:
        print(f"\n✅ AI已配置: {ai_config.get('provider', 'unknown')}")
    
    # 设置目录
    setup_directories()
    
    # 检查文件
    srt_files, video_files = check_files()
    
    print(f"\n📊 文件检查结果:")
    print(f"📝 字幕文件: {len(srt_files)} 个")
    print(f"🎬 视频文件: {len(video_files)} 个")
    
    if not srt_files:
        print("\n❌ 未找到字幕文件")
        print("💡 请将电影字幕文件放入 movie_srt/ 目录")
        print("支持格式: .srt, .txt")
        print("示例: 复仇者联盟.srt, 阿凡达.txt")
        
        input("\n准备好字幕文件后，按回车键继续...")
        srt_files, _ = check_files()
        
        if not srt_files:
            print("❌ 仍未找到字幕文件，请检查 movie_srt/ 目录")
            return
    
    if not video_files:
        print("\n⚠️ 未找到视频文件")
        print("💡 请将电影视频文件放入 movie_videos/ 目录")
        print("支持格式: .mp4, .mkv, .avi, .mov, .wmv, .flv")
        
        continue_choice = input("\n是否继续？(仅分析不生成视频) (y/n): ").strip().lower()
        if continue_choice not in ['y', 'yes', '是']:
            return
    
    print(f"\n🚀 启动100% AI驱动电影剪辑系统")
    print("=" * 60)
    print("🎯 处理特色:")
    print("• AI识别主人公和完整故事线")
    print("• 非连续时间但逻辑连贯的剪辑")
    print("• 第一人称详细叙述")
    print("• 无声视频专为叙述设计")
    print("• 固定标准输出格式")
    
    # 启动主系统
    try:
        from ai_driven_movie_clipper import AIDrivenMovieClipper
        
        print("\n" + "="*80)
        print("🎬 启动AI驱动电影剪辑系统")
        print("="*80)
        
        clipper = AIDrivenMovieClipper()
        
        # 验证AI配置
        if not clipper.ai_config.get('enabled'):
            print("❌ AI配置验证失败，系统退出")
            return
        
        # 开始处理
        clipper.process_all_movies()
        
        print(f"\n🎉 100% AI驱动剪辑完成！")
        print("📁 输出文件（固定格式）:")
        print(f"  • 主人公故事视频: ai_movie_clips/*.mp4")
        print(f"  • 第一人称叙述字幕: ai_movie_clips/*_第一人称叙述.srt")
        print(f"  • AI分析报告: ai_movie_clips/*_AI分析报告.txt")
        print(f"  • 完整故事报告: ai_movie_analysis/*_完整故事AI分析报告.txt")
        print(f"  • 系统总结: ai_movie_analysis/100%AI驱动电影剪辑系统总结报告.txt")
        
        print(f"\n🎯 系统特色完成（7个需求）:")
        print("1. ✅ 字幕解析和错误修正")
        print("2. ✅ AI识别主人公")
        print("3. ✅ 主人公完整故事线")
        print("4. ✅ 非连续但连贯的剧情点剪辑")
        print("5. ✅ 100% AI分析")
        print("6. ✅ 固定输出格式")
        print("7. ✅ 无声视频+第一人称实时叙述")
        
    except ImportError:
        print("❌ 系统文件缺失，请检查 ai_driven_movie_clipper.py")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

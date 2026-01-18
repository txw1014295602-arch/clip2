
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电影AI分析剪辑系统启动器
满足用户6个核心需求的完整解决方案
"""

import os
import sys
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
    print("🤖 AI配置设置（满足需求5：必须100% AI分析）")
    print("=" * 60)
    
    print("支持的AI服务商：")
    print("1. OpenAI (ChatGPT)")
    print("2. Anthropic (Claude)")
    print("3. DeepSeek")
    print("4. 通义千问")
    print("5. 中转API")
    
    while True:
        try:
            choice = input("\n请选择AI服务商 (1-5): ").strip()
            
            if choice == '1':
                provider = 'openai'
                base_url = 'https://api.openai.com/v1'
                model = 'gpt-4'
                break
            elif choice == '2':
                provider = 'anthropic'
                base_url = 'https://api.anthropic.com/v1'
                model = 'claude-3-haiku-20240307'
                break
            elif choice == '3':
                provider = 'deepseek'
                base_url = 'https://api.deepseek.com/v1'
                model = 'deepseek-chat'
                break
            elif choice == '4':
                provider = 'qwen'
                base_url = 'https://dashscope.aliyuncs.com/api/v1'
                model = 'qwen-turbo'
                break
            elif choice == '5':
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
        'movie_srt': '电影字幕文件（需求1）',
        'movie_videos': '电影视频文件（可选）',
        'movie_clips': '剪辑输出视频（需求4）',
        'movie_analysis': '分析报告（需求6）',
        'ai_cache': 'AI分析缓存'
    }
    
    print("\n📁 创建目录结构...")
    for dir_name, desc in directories.items():
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ {dir_name}/ - {desc}")

def check_subtitle_files():
    """检查字幕文件"""
    srt_folder = 'movie_srt'
    srt_files = [f for f in os.listdir(srt_folder) 
                 if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
    
    if not srt_files:
        print(f"\n📝 请将电影字幕文件放入 {srt_folder}/ 目录")
        print("支持格式: .srt, .txt")
        print("示例文件名:")
        print("  • 复仇者联盟.srt")
        print("  • 阿凡达.txt")
        print("  • 泰坦尼克号.srt")
        return []
    
    return srt_files

def show_system_features():
    """显示系统特色"""
    print("🎬 完全AI驱动的电影分析剪辑系统")
    print("=" * 80)
    print("✨ 满足您的6个核心需求:")
    print()
    print("📖 需求1: 电影字幕分析")
    print("   • 智能解析多种字幕格式")
    print("   • 支持SRT和TXT格式")
    print("   • 多编码格式兼容")
    print()
    print("🔧 需求2: 错误修正")
    print("   • 自动修正字幕错别字")
    print("   • 繁体字转简体字")
    print("   • 格式标准化")
    print()
    print("🎭 需求3: AI识别主人公和故事线")
    print("   • 100% AI自动识别主要角色")
    print("   • AI分析主人公完整故事弧线")
    print("   • 长故事自动分割为多个短视频")
    print()
    print("✂️ 需求4: 按剧情点剪辑")
    print("   • 时间可以不连续但逻辑连贯")
    print("   • 每个片段附带第一人称叙述字幕")
    print("   • 叙述内容详细清晰")
    print("   • 完整覆盖剧情要点")
    print()
    print("🤖 需求5: 100% AI分析")
    print("   • 无AI配置直接返回")
    print("   • 所有分析部分均为AI生成")
    print("   • 不依赖固定规则或关键词")
    print()
    print("📋 需求6: 固定输出格式")
    print("   • 标准化分析报告")
    print("   • 统一的文件命名")
    print("   • 完整的使用说明")

def main():
    """主启动函数"""
    show_system_features()
    
    # 设置目录
    setup_directories()
    
    # 需求5：必须检查AI配置
    has_ai, ai_config = check_ai_config()
    if not has_ai:
        print("\n❌ 需求5要求：必须100% AI分析")
        print("⚠️ 未检测到AI配置，不使用AI就直接返回")
        
        setup_choice = input("\n是否现在配置AI？(y/n): ").strip().lower()
        if setup_choice not in ['y', 'yes', '是']:
            print("❌ 未配置AI，根据需求5直接返回")
            return
        
        if not setup_ai_config():
            print("❌ AI配置失败，根据需求5直接返回")
            return
        
        print("✅ AI配置成功，现在可以进行100% AI分析")
    else:
        print(f"\n✅ AI已配置: {ai_config.get('provider', 'unknown')}")
    
    # 检查字幕文件
    srt_files = check_subtitle_files()
    if not srt_files:
        input("\n准备好字幕文件后，按回车键继续...")
        srt_files = check_subtitle_files()
        
        if not srt_files:
            print("❌ 仍未找到字幕文件，请检查 movie_srt/ 目录")
            return
    
    print(f"\n✅ 找到 {len(srt_files)} 个电影字幕文件:")
    for i, file in enumerate(srt_files, 1):
        print(f"  {i}. {file}")
    
    # 检查视频文件（可选）
    video_folder = 'movie_videos'
    video_files = []
    if os.path.exists(video_folder):
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        video_files = [f for f in os.listdir(video_folder) 
                      if any(f.lower().endswith(ext) for ext in video_extensions)]
    
    if video_files:
        print(f"\n🎬 找到 {len(video_files)} 个视频文件（将生成剪辑视频）")
    else:
        print(f"\n📝 未找到视频文件（仅生成AI分析报告）")
        print(f"如需剪辑视频，请将视频文件放入 {video_folder}/ 目录")
    
    print(f"\n🚀 开始100% AI分析...")
    print("🎯 系统特点:")
    print("• AI识别主人公和完整故事线")
    print("• 按剧情点智能剪辑（时间可不连续但逻辑连贯）")
    print("• 生成第一人称叙述字幕")
    print("• 自动修正字幕错误")
    print("• 固定输出格式")
    
    # 启动电影AI分析系统
    try:
        from movie_ai_analysis_system import MovieAIAnalysisSystem
        
        print("\n" + "="*80)
        print("🎬 启动完全AI驱动的电影分析剪辑系统")
        print("="*80)
        
        system = MovieAIAnalysisSystem()
        
        # 验证AI配置
        if not system.ai_config.get('enabled'):
            print("❌ AI未正确配置，根据需求5直接返回")
            return
        
        # 开始处理
        system.process_all_movies()
        
        print(f"\n🎉 100% AI分析完成！")
        print("📁 输出文件（需求6固定格式）:")
        print(f"  • AI剪辑方案: movie_analysis/*_AI剪辑方案.txt")
        print(f"  • 剪辑视频: movie_clips/*.mp4")
        print(f"  • 第一人称叙述字幕: movie_clips/*_第一人称叙述.srt")
        
        print(f"\n🎯 输出格式特色（需求6）:")
        print("1. 📊 电影基本信息（类型、主角、主题）")
        print("2. 🎭 主人公识别和完整故事弧线")
        print("3. ✂️ 精彩片段详细剪辑方案")
        print("4. 🎙️ 第一人称详细叙述内容")
        print("5. ⏰ 精确时间标注（支持非连续时间段）")
        print("6. 🔗 剧情连贯性分析")
        print("7. 🤖 100% AI分析确认")
        
    except ImportError:
        print("❌ 系统文件缺失，请检查 movie_ai_analysis_system.py")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

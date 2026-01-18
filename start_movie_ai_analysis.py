
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电影字幕AI分析剪辑启动器 - 100% AI分析版本
专门解决您的6个核心需求：
1. 电影字幕分析
2. 智能错误修正
3. AI识别主人公和完整故事线
4. 按剧情点剪辑（非连续时间但逻辑连贯）
5. 100% AI分析（不用AI就直接返回）
6. 固定输出格式
"""

import os
import sys
import json

def check_ai_config():
    """检查AI配置 - 必须配置AI才能运行"""
    try:
        with open('.ai_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            if config.get('enabled') and config.get('api_key'):
                print(f"✅ AI已配置: {config.get('provider', 'unknown')}")
                return True, config
    except:
        pass
    return False, {}

def setup_ai_config():
    """设置AI配置 - 必须配置AI"""
    print("🤖 电影分析需要AI支持 - 配置AI服务")
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
                '1': ('openai', 'https://api.openai.com/v1', 'gpt-3.5-turbo'),
                '2': ('anthropic', 'https://api.anthropic.com/v1', 'claude-3-haiku-20240307'),
                '3': ('deepseek', 'https://api.deepseek.com/v1', 'deepseek-chat'),
                '4': ('qwen', 'https://dashscope.aliyuncs.com/api/v1', 'qwen-turbo'),
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
        'movie_srt': '电影字幕文件',
        'movie_videos': '电影视频文件（可选）',
        'movie_clips': '剪辑输出视频',
        'movie_analysis': '分析报告',
        'ai_cache': 'AI分析缓存'
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
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
    
    if not srt_files:
        print(f"\n📝 请将电影字幕文件放入 movie_srt/ 目录")
        print("支持格式: .srt, .txt")
        print("示例文件名:")
        print("  • 复仇者联盟.srt")
        print("  • 阿凡达.txt")
        print("  • 泰坦尼克号.srt")
        return []
    
    return srt_files

def show_system_features():
    """显示系统特色"""
    print("🎬 电影字幕AI分析剪辑系统")
    print("=" * 80)
    print("✨ 100% AI分析特色（满足您的6个需求）:")
    print()
    print("📖 1. 电影字幕智能分析")
    print("   • 自动解析多种字幕格式")
    print("   • 智能修正错别字和格式问题")
    print("   • 支持多种编码格式")
    print()
    print("🤖 2. 100% AI分析保证")
    print("   • 无AI配置直接返回，不进行任何分析")
    print("   • AI识别电影类型、主要角色、核心主题")
    print("   • AI生成完整故事线说明")
    print()
    print("🎭 3. 主人公识别和故事线")
    print("   • AI自动识别主要角色")
    print("   • 生成主人公视角的完整故事线")
    print("   • 长故事自动分割为多个短视频")
    print()
    print("🎬 4. 智能剧情点剪辑")
    print("   • 支持非连续时间段智能合并")
    print("   • 按5种剧情点分类：关键冲突、人物转折、线索揭露、情感高潮、动作场面")
    print("   • 剪辑后逻辑连贯，适合短视频传播")
    print()
    print("🎙️ 5. 第一人称叙述字幕")
    print("   • 详细的'我'视角叙述内容")
    print("   • 叙述与视频内容精确同步")
    print("   • 完整覆盖剧情发展和人物动机")
    print()
    print("📋 6. 固定输出格式")
    print("   • 标准化剪辑方案报告")
    print("   • 完整的AI分析数据")
    print("   • 第一人称叙述字幕文件")
    print("   • 错别字修正记录")

def main():
    """主启动函数"""
    show_system_features()
    
    # 必须先配置AI
    has_ai, ai_config = check_ai_config()
    if not has_ai:
        print("\n❌ 需求5：必须100% AI分析，未检测到AI配置")
        print("⚠️ 不使用AI就直接返回，无法进行分析")
        
        setup_choice = input("\n是否现在配置AI？(y/n): ").strip().lower()
        if setup_choice not in ['y', 'yes', '是']:
            print("❌ 未配置AI，程序退出（满足需求5：不用AI就直接返回）")
            return
        
        if not setup_ai_config():
            print("❌ AI配置失败，程序退出")
            return
        
        print("✅ AI配置成功，可以进行100% AI分析")
    
    # 设置目录
    setup_directories()
    
    # 检查字幕文件
    srt_files = check_files()
    if not srt_files:
        input("\n准备好字幕文件后，按回车键继续...")
        srt_files = check_files()
        
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
        print(f"如需生成剪辑视频，请将视频文件放入 {video_folder}/ 目录")
    
    print(f"\n🚀 开始100% AI分析...")
    print("🎯 分析特色:")
    print("• AI识别主人公和完整故事线")
    print("• 按剧情点智能剪辑（非连续时间但逻辑连贯）")
    print("• 生成第一人称叙述字幕")
    print("• 自动修正字幕错误")
    print("• 固定输出格式")
    
    # 启动电影AI剪辑系统
    try:
        from movie_ai_clipper import MovieAIClipper
        
        print("\n" + "="*80)
        print("🎬 启动电影AI分析剪辑系统")
        print("="*80)
        
        clipper = MovieAIClipper()
        
        # 验证AI配置
        if not clipper.ai_config.get('enabled'):
            print("❌ AI未正确配置，无法进行100% AI分析")
            print("⚠️ 根据需求5，程序直接返回")
            return
        
        # 开始处理
        clipper.process_all_movies()
        
        print(f"\n🎉 100% AI分析完成！")
        print("📁 输出文件（固定格式）:")
        print(f"  • AI剪辑方案: movie_analysis/*_AI剪辑方案.txt")
        print(f"  • AI分析数据: movie_analysis/*_AI分析数据.json")
        print(f"  • 总结报告: movie_analysis/电影AI分析总结报告.txt")
        
        if video_files:
            print(f"  • 剪辑视频: movie_clips/*.mp4")
            print(f"  • 第一人称叙述字幕: movie_clips/*_第一人称叙述.srt")
            print(f"  • 叙述详情: movie_clips/*_叙述详情.txt")
        
        print(f"\n🎯 输出格式特色（满足需求6）:")
        print("1. 📊 电影基本信息（类型、主角、主题）")
        print("2. 📖 主人公视角完整故事线")
        print("3. 🎬 精彩片段详细方案（5-8个）")
        print("4. 🎙️ 第一人称完整叙述（开场-发展-高潮-结尾）")
        print("5. ⏱️ 精确时间标注（支持非连续时间段）")
        print("6. 🎭 剧情点类型分类")
        print("7. 📝 错别字修正记录")
        print("8. 🔗 剪辑逻辑连贯性说明")
        
    except ImportError:
        print("❌ 系统文件缺失，请检查 movie_ai_clipper.py")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

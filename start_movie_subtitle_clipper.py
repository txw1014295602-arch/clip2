
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电影字幕AI分析剪辑启动器
专门处理：
1. 电影字幕AI分析
2. 自动错误修正
3. 主人公识别和故事线提取
4. 精彩片段剪辑（支持多个短视频）
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
    print("🤖 AI配置设置（电影分析需要AI支持）")
    print("=" * 50)
    
    print("支持的AI服务商：")
    print("1. OpenAI (ChatGPT)")
    print("2. Anthropic (Claude)")
    print("3. DeepSeek")
    print("4. 通义千问")
    print("5. 中转API (支持多种模型)")
    
    while True:
        try:
            choice = input("\n请选择AI服务商 (1-5): ").strip()
            
            if choice == '1':
                provider = 'openai'
                base_url = 'https://api.openai.com/v1'
                model = 'gpt-3.5-turbo'
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
                base_url = input("请输入中转API地址 (如: https://api.chataiapi.com/v1): ").strip()
                model = input("请输入模型名称 (如: gpt-3.5-turbo): ").strip()
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
    
    # 保存配置
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

def show_features():
    """显示功能特色"""
    print("🎬 电影字幕AI分析剪辑系统")
    print("=" * 60)
    print("✨ 核心功能:")
    print("📖 1. 智能字幕解析 - 自动修正错别字和格式问题")
    print("🤖 2. AI全面分析 - 识别电影类型、主要角色、核心主题")
    print("🎭 3. 主人公识别 - 自动识别主要角色和故事线")
    print("🎬 4. 精彩片段剪辑 - 智能选择5-8个最精彩的片段")
    print("🎙️ 5. 第一人称叙述 - 生成详细的观众视角解说")
    print("📊 6. 剧情点分类 - 按冲突、转折、揭露等类型分类")
    print("🔗 7. 故事线完整 - 确保每个片段都有完整的故事弧线")
    print("📹 8. 多视频支持 - 长故事自动分割为多个短视频")
    print()
    print("🎯 输出规格:")
    print("• 每个片段2-3分钟，适合短视频平台")
    print("• 无声视频配第一人称叙述字幕")
    print("• 完整的剧情分析报告")
    print("• 主人公故事线详细说明")

def main():
    """主启动函数"""
    show_features()
    
    # 设置目录
    setup_directories()
    
    # 检查AI配置
    has_ai, ai_config = check_ai_config()
    if not has_ai:
        print("\n⚠️ AI未配置，电影分析需要AI支持")
        if not setup_ai_config():
            print("❌ AI配置失败，无法进行电影分析")
            return
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
        print(f"\n📝 未找到视频文件（仅生成分析报告，不剪辑视频）")
        print(f"如需剪辑视频，请将视频文件放入 {video_folder}/ 目录")
    
    print(f"\n🚀 开始AI分析...")
    print("注意：")
    print("• 系统将分析每部电影的完整剧情")
    print("• 自动识别主人公和故事线")
    print("• 选择最精彩的片段进行剪辑")
    print("• 生成详细的分析报告")
    
    # 启动电影AI剪辑系统
    try:
        from movie_ai_clipper import MovieAIClipper
        clipper = MovieAIClipper()
        clipper.process_all_movies()
        
        print("\n🎉 电影AI分析剪辑完成！")
        print("📁 输出文件:")
        print(f"  • 剪辑方案: movie_analysis/*_AI剪辑方案.txt")
        print(f"  • 分析数据: movie_analysis/*_AI分析数据.json")
        if video_files:
            print(f"  • 剪辑视频: movie_clips/*.mp4")
            print(f"  • 叙述字幕: movie_clips/*_第一人称叙述.srt")
        
        print("\n🎯 下一步:")
        print("1. 查看 movie_analysis/ 目录中的详细分析报告")
        print("2. 每个报告包含主人公识别和完整故事线")
        print("3. 精彩片段按剧情点分类，适合制作短视频")
        
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电影AI分析剪辑系统启动器
一键启动全AI分析流程
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
                return True
    except:
        pass
    return False

def setup_ai_config():
    """设置AI配置"""
    print("🤖 AI配置设置")
    print("=" * 40)
    
    print("支持的AI服务商：")
    print("1. OpenAI (ChatGPT)")
    print("2. Anthropic (Claude)")
    print("3. DeepSeek")
    print("4. 通义千问")
    print("5. 其他OpenAI兼容API")
    
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
                provider = input("请输入服务商名称: ").strip()
                base_url = input("请输入API地址: ").strip()
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

def main():
    """主函数"""
    print("🎬 电影AI分析剪辑系统")
    print("=" * 50)
    
    # 检查AI配置
    if not check_ai_config():
        print("⚠️ AI未配置，需要先设置API密钥")
        if not setup_ai_config():
            print("❌ AI配置失败，无法继续")
            return
    
    # 创建必要目录
    os.makedirs('movie_srt', exist_ok=True)
    os.makedirs('movie_clips', exist_ok=True)
    os.makedirs('movie_analysis', exist_ok=True)
    os.makedirs('ai_cache', exist_ok=True)
    
    # 检查字幕文件
    srt_files = [f for f in os.listdir('movie_srt') 
                 if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
    
    if not srt_files:
        print("\n📁 文件准备说明:")
        print("请将电影字幕文件放入 movie_srt/ 目录")
        print("支持格式: .srt, .txt")
        print("示例文件名: 复仇者联盟.srt, 阿凡达.txt")
        
        input("\n准备好字幕文件后，按回车键继续...")
        
        # 再次检查
        srt_files = [f for f in os.listdir('movie_srt') 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print("❌ 仍未找到字幕文件，请检查 movie_srt/ 目录")
            return
    
    print(f"\n✅ 找到 {len(srt_files)} 个字幕文件:")
    for file in srt_files:
        print(f"  • {file}")
    
    print(f"\n🤖 AI分析即将开始...")
    print("注意：所有分析都使用AI，如果AI不可用将直接返回")
    
    # 启动分析
    try:
        from movie_ai_clipper import MovieAIClipper
        clipper = MovieAIClipper()
        clipper.process_all_movies()
        
        print("\n🎉 电影AI分析完成！")
        print(f"📄 查看剪辑方案: movie_analysis/ 目录")
        
    except Exception as e:
        print(f"❌ 系统错误: {e}")

if __name__ == "__main__":
    main()

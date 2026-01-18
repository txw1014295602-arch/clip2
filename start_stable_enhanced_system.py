
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
稳定增强剪辑系统启动器
解决问题12-17的完整启动方案
"""

import os
import sys

def check_environment():
    """检查运行环境"""
    print("🔧 稳定增强剪辑系统")
    print("=" * 60)
    print("🎯 解决的核心问题：")
    print("• 问题12: API稳定性 - 分析结果缓存机制")
    print("• 问题13: 剪辑一致性 - 避免重复剪辑")
    print("• 问题14: 多次执行一致性保证")
    print("• 问题15: 批量处理所有SRT文件")
    print("• 问题17: 引导式用户配置选择")
    print("=" * 60)
    
    # 检查必要目录
    directories = ['srt', 'videos']
    missing_dirs = []
    
    for directory in directories:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"\n📁 创建必要目录:")
        for directory in missing_dirs:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ {directory}/")
    
    # 检查字幕文件
    srt_files = [f for f in os.listdir('srt') 
                 if f.lower().endswith(('.srt', '.txt')) and not f.startswith('.')] if os.path.exists('srt') else []
    
    if not srt_files:
        print(f"\n❌ srt/ 目录中未找到字幕文件")
        print("📝 请将字幕文件放入 srt/ 目录")
        print("支持格式: .srt, .txt")
        return False
    
    # 检查视频文件
    video_files = [f for f in os.listdir('videos') 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'))] if os.path.exists('videos') else []
    
    print(f"\n✅ 检查结果:")
    print(f"📄 字幕文件: {len(srt_files)} 个")
    print(f"🎬 视频文件: {len(video_files)} 个")
    
    if not video_files:
        print("⚠️ 未找到视频文件，将仅进行分析不生成剪辑")
    
    return True

def show_features():
    """显示系统特性"""
    print("\n🌟 稳定增强系统特性:")
    print()
    print("🔄 **稳定性保证**")
    print("   • API结果自动缓存，避免重复调用")
    print("   • 剪辑状态持久化跟踪")
    print("   • 多次重试机制")
    print()
    print("📋 **一致性保证**")
    print("   • 基于文件内容哈希的缓存键")
    print("   • 多次执行相同字幕文件得到相同结果")
    print("   • 详细的一致性日志记录")
    print()
    print("⚡ **效率优化**")
    print("   • 智能跳过已完成的剪辑")
    print("   • 批量处理所有SRT文件")
    print("   • 支持断点续传")
    print()
    print("🎛️ **用户友好**")
    print("   • 引导式AI配置选择")
    print("   • 详细的处理进度显示")
    print("   • 完整的处理报告生成")

def main():
    """主启动函数"""
    if not check_environment():
        return
    
    show_features()
    
    print(f"\n🚀 启动稳定增强剪辑系统...")
    print("💡 系统将自动:")
    print("1. 引导您配置AI服务")
    print("2. 批量处理所有字幕文件") 
    print("3. 智能缓存避免重复工作")
    print("4. 生成详细处理报告")
    
    try:
        from stable_enhanced_clipper import main as clipper_main
        clipper_main()
        
    except ImportError:
        print("❌ 系统文件缺失，请检查 stable_enhanced_clipper.py")
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断处理")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

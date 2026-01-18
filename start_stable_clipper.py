
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
稳定AI剪辑系统启动脚本
"""

import os
import sys

def check_requirements():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查AI配置
    if not os.path.exists('.ai_config.json'):
        print("❌ 未找到AI配置文件")
        print("请先运行: python configure_ai.py")
        return False
    
    # 检查必要目录
    directories = ['videos']
    for directory in directories:
        if not os.path.exists(directory):
            print(f"❌ 缺少必要目录: {directory}/")
            print(f"请创建 {directory}/ 目录并放入相应文件")
            return False
    
    # 检查字幕文件
    srt_files = [f for f in os.listdir('.') if f.endswith(('.srt', '.txt')) and any(c.isdigit() for c in f)]
    if not srt_files:
        if os.path.exists('srt'):
            srt_files = [f for f in os.listdir('srt') if f.endswith(('.srt', '.txt'))]
    
    if not srt_files:
        print("❌ 未找到字幕文件")
        print("请将字幕文件放在当前目录或srt/目录中")
        return False
    
    # 检查视频文件
    video_files = [f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    if not video_files:
        print("❌ videos/目录中没有视频文件")
        return False
    
    print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    return True

def main():
    """主函数"""
    print("🚀 稳定AI剪辑系统")
    print("=" * 60)
    print("🎯 系统特点:")
    print("• AI分析失败时直接跳过，不使用备用方案")
    print("• 分析结果自动缓存，避免重复API调用")
    print("• 剪辑结果缓存，支持多次执行")
    print("• 智能上下文构建，根据字幕数量动态调整")
    print("• 严格的时间段验证")
    print("=" * 60)
    
    if not check_requirements():
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        return
    
    print("\n🤖 启动稳定AI剪辑系统...")
    
    try:
        from stable_ai_clipper import main as clipper_main
        clipper_main()
    except Exception as e:
        print(f"❌ 系统运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

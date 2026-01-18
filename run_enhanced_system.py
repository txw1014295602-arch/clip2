
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版智能剪辑系统启动脚本
"""

import os
import sys

def check_environment():
    """检查环境"""
    print("🔍 环境检查...")
    
    # 检查目录
    required_dirs = ['srt', 'videos', 'intelligent_clips']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/")
        else:
            print(f"✓ 目录存在: {dir_name}/")
    
    # 检查字幕文件
    srt_files = [f for f in os.listdir('srt') if f.endswith('.srt')]
    if not srt_files:
        print("❌ srt/目录中没有字幕文件")
        print("请将.srt字幕文件放入srt/目录")
        return False
    else:
        print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    
    # 检查视频文件
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if not video_files:
        print("❌ videos/目录中没有视频文件")
        print("请将视频文件放入videos/目录")
        return False
    else:
        print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    # 检查FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
        else:
            print("❌ FFmpeg未正确安装")
            return False
    except FileNotFoundError:
        print("❌ 未找到FFmpeg，请先安装FFmpeg")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 增强版智能剪辑系统")
    print("=" * 60)
    print("解决的问题:")
    print("✓ 智能剧情识别，不限制死")
    print("✓ 完整上下文分析，避免割裂")
    print("✓ 每集多个短视频，AI判断完整内容")
    print("✓ 自动剪辑+旁白生成")
    print("✓ 保持剧情连贯性")
    print("✓ 确保句子完整性")
    print("✓ 大幅减少API调用次数")
    print("=" * 60)
    
    if not check_environment():
        input("\n按回车键退出...")
        return
    
    try:
        from enhanced_clipper import run_enhanced_clipper
        run_enhanced_clipper()
        
        print("\n🎉 所有短视频已创建完成!")
        print("📁 查看 intelligent_clips/ 目录获取结果")
        print("📄 每个短视频都有对应的旁白解说文件")
        
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()

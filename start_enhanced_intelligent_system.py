
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版智能剪辑系统启动脚本
一键解决所有15个问题
"""

import os
import sys

def check_environment():
    """检查环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
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

def setup_directories():
    """设置目录结构"""
    directories = ['srt', 'videos', 'clips', 'analysis_cache']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}/")
        else:
            print(f"✓ 目录已存在: {directory}/")

def check_files():
    """检查文件准备情况"""
    srt_files = [f for f in os.listdir('srt') if f.endswith('.srt')] if os.path.exists('srt') else []
    video_files = [f for f in os.listdir('videos') if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))] if os.path.exists('videos') else []
    
    print(f"📄 字幕文件: {len(srt_files)} 个")
    print(f"🎬 视频文件: {len(video_files)} 个")
    
    if not srt_files:
        print("\n⚠️  使用说明:")
        print("1. 将SRT字幕文件放入 srt/ 目录")
        print("2. 将对应视频文件放入 videos/ 目录")
        print("3. 文件名要对应，例如: EP01.srt 和 EP01.mp4")
        return False
    
    if not video_files:
        print("\n⚠️  请将视频文件放入 videos/ 目录")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 增强版智能电视剧剪辑系统")
    print("=" * 60)
    print("解决的15个核心问题:")
    print("✓ 1. 完全智能化，不限制剧情类型")
    print("✓ 2. 完整上下文分析，避免割裂")
    print("✓ 3. 上下文连贯性保证")
    print("✓ 4. 每集多个智能短视频")
    print("✓ 5. 自动剪辑生成完整视频")
    print("✓ 6. 规范目录结构(videos/, srt/)")
    print("✓ 7. 附带旁白生成")
    print("✓ 8. 整集分析，大幅减少API调用")
    print("✓ 9. 剧情连贯性和反转处理")
    print("✓ 10. 专业剧情理解旁白")
    print("✓ 11. 保证句子完整性")
    print("✓ 12. API结果缓存机制")
    print("✓ 13. 剪辑一致性保证")
    print("✓ 14. 断点续传")
    print("✓ 15. 执行一致性保证")
    print("=" * 60)
    
    # 1. 检查环境
    if not check_environment():
        input("\n按回车退出...")
        return
    
    # 2. 设置目录
    setup_directories()
    
    # 3. 检查文件
    if not check_files():
        input("\n请按说明准备文件后重新运行，按回车退出...")
        return
    
    # 4. 运行主程序
    print(f"\n🎯 启动智能剪辑系统...")
    try:
        from enhanced_intelligent_system import main as run_system
        run_system()
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        input("按回车退出...")
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        input("按回车退出...")

if __name__ == "__main__":
    main()

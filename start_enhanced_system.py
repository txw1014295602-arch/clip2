
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版智能剪辑系统启动脚本
解决所有提出的问题
"""

import os
import sys

def check_directories():
    """检查必要目录"""
    required_dirs = ['srt', 'videos', 'clips', 'analysis_cache']
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ 创建目录: {directory}/")

def main():
    print("🚀 增强版智能电视剧剪辑系统")
    print("=" * 50)
    print("🎯 解决的问题:")
    print("• 完全智能化，不限制剧情类型")
    print("• 完整上下文分析，避免割裂")
    print("• 每集多个连贯短视频")
    print("• AI判断完整剪辑内容")
    print("• 自动生成视频和旁白")
    print("• 保证剧情连贯性")
    print("• 缓存机制避免重复API调用")
    print("• 一致性保证")
    print("=" * 50)
    
    # 检查目录
    check_directories()
    
    # 检查文件
    if not os.path.exists('enhanced_intelligent_clipper.py'):
        print("❌ 找不到核心文件")
        return
    
    try:
        # 运行增强系统
        from enhanced_intelligent_clipper import main as enhanced_main
        enhanced_main()
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")

if __name__ == "__main__":
    main()

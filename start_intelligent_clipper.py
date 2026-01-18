
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能电视剧剪辑系统启动脚本
"""

import os
import sys

def main():
    print("🚀 启动智能电视剧剪辑系统")
    print("=" * 50)
    
    # 检查必要文件
    if not os.path.exists('intelligent_tv_clipper.py'):
        print("❌ 找不到核心文件 intelligent_tv_clipper.py")
        return
    
    try:
        # 导入并运行主程序
        from intelligent_tv_clipper import main as clipper_main
        clipper_main()
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保已安装必要的依赖包")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SRT字幕分析系统启动脚本
"""

if __name__ == "__main__":
    try:
        from srt_analyzer_only import main
        main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保 srt_analyzer_only.py 文件存在")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

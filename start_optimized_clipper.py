
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动优化剪辑系统
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimized_complete_clipper import main

if __name__ == "__main__":
    main()

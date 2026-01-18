
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
平台兼容性修复 - 解决Windows编码问题
"""

import os
import sys
import locale
import subprocess

def fix_encoding():
    """修复Windows编码问题"""
    if sys.platform.startswith('win'):
        # 设置环境变量强制使用UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'
        
        # 尝试设置控制台编码
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass
        
        # 设置默认编码
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            except:
                pass

def safe_subprocess_run(command, **kwargs):
    """安全的子进程运行函数"""
    # 设置默认编码参数
    kwargs.setdefault('encoding', 'utf-8')
    kwargs.setdefault('errors', 'ignore')
    
    # Windows特殊处理
    if sys.platform.startswith('win'):
        kwargs.setdefault('creationflags', subprocess.CREATE_NO_WINDOW)
    
    return subprocess.run(command, **kwargs)

def safe_file_read(filepath, encoding='utf-8'):
    """安全的文件读取函数"""
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # 如果都失败，使用错误忽略模式
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def safe_file_write(filepath, content, encoding='utf-8'):
    """安全的文件写入函数"""
    try:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
    except UnicodeEncodeError:
        # 使用错误忽略模式
        with open(filepath, 'w', encoding=encoding, errors='ignore') as f:
            f.write(content)

# 启动时自动修复
fix_encoding()

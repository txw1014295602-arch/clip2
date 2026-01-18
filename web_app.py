#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web管理界面 - 简单的Flask应用
提供可视化的项目管理界面
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__)

# 配置
CONFIG_FILE = '.config.json'
SRT_FOLDER = 'srt'
VIDEOS_FOLDER = 'videos'
OUTPUT_FOLDER = 'tv_clips'
CACHE_FOLDER = 'tv_cache'

def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'ai': {'enabled': False}}

def save_config(config):
    """保存配置"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    config = load_config()

    # 统计文件
    srt_files = [f for f in os.listdir(SRT_FOLDER) if f.endswith(('.srt', '.txt'))] if os.path.exists(SRT_FOLDER) else []
    video_files = [f for f in os.listdir(VIDEOS_FOLDER) if f.endswith(('.mp4', '.mkv', '.avi'))] if os.path.exists(VIDEOS_FOLDER) else []
    output_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.mp4')] if os.path.exists(OUTPUT_FOLDER) else []

    return jsonify({
        'ai_enabled': config.get('ai', {}).get('enabled', False),
        'ai_provider': config.get('ai', {}).get('provider', '未配置'),
        'srt_count': len(srt_files),
        'video_count': len(video_files),
        'output_count': len(output_files)
    })

@app.route('/api/files')
def get_files():
    """获取文件列表"""
    srt_files = []
    if os.path.exists(SRT_FOLDER):
        for f in os.listdir(SRT_FOLDER):
            if f.endswith(('.srt', '.txt')):
                path = os.path.join(SRT_FOLDER, f)
                srt_files.append({
                    'name': f,
                    'size': os.path.getsize(path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
                })

    return jsonify({'files': srt_files})

@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """管理配置"""
    if request.method == 'GET':
        config = load_config()
        return jsonify(config)
    else:
        config = request.json
        if save_config(config):
            return jsonify({'success': True})
        return jsonify({'success': False}), 500

if __name__ == '__main__':
    # 创建必要目录
    for folder in [SRT_FOLDER, VIDEOS_FOLDER, OUTPUT_FOLDER, CACHE_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    print("🌐 启动Web管理界面...")
    print("📍 访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

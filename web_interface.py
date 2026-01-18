
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from subtitle_analyzer import IntelligentSubtitleAnalyzer
from video_clipper import VideoClipper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析字幕并返回精彩片段"""
    try:
        analyzer = IntelligentSubtitleAnalyzer()
        all_segments = []
        
        # 获取所有字幕文件
        subtitle_files = [f for f in os.listdir('.') if f.endswith('.txt') and f.startswith('S01E')]
        subtitle_files.sort()
        
        for filename in subtitle_files:
            subtitles = analyzer.parse_subtitle_file(filename)
            exciting = analyzer.find_exciting_segments(subtitles)
            all_segments.extend(exciting)
        
        # 生成剪辑点
        cut_points = analyzer.generate_cut_points(all_segments, max_clips=50)
        
        return jsonify({
            'success': True,
            'clips': cut_points,
            'total': len(cut_points)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/clip', methods=['POST'])
def create_clip():
    """创建单个视频片段"""
    try:
        data = request.json
        clipper = VideoClipper()
        
        episode = data['episode']
        start_time = float(data['start_time'])
        end_time = float(data['end_time'])
        clip_name = data.get('name', f"clip_{int(start_time)}")
        
        video_file = clipper.get_episode_video_file(episode)
        if not video_file:
            return jsonify({
                'success': False,
                'error': f'未找到视频文件: {episode}'
            })
        
        output_path = os.path.join(clipper.output_folder, f"{clip_name}.mp4")
        success = clipper.cut_video_segment(video_file, start_time, end_time, output_path)
        
        return jsonify({
            'success': success,
            'output_file': output_path if success else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<filename>')
def download_file(filename):
    """下载生成的视频文件"""
    try:
        return send_file(os.path.join('clips', filename), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # 创建templates文件夹
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web界面 - 电视剧剪辑系统的Web前端
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from subtitle_analyzer import IntelligentSubtitleAnalyzer

app = Flask(__name__)

class WebInterface:
    def __init__(self):
        self.analyzer = IntelligentSubtitleAnalyzer()
        
    def get_available_files(self):
        """获取可用的字幕文件"""
        files = []
        for file in os.listdir('.'):
            if file.endswith('.txt') and any(pattern in file.lower() for pattern in ['e', 's01e', '第', '集']):
                files.append(file)
        return sorted(files)
    
    def analyze_episode(self, filename):
        """分析单集"""
        try:
            result = self.analyzer.analyze_single_episode(filename)
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

web_interface = WebInterface()

@app.route('/')
def index():
    """主页"""
    files = web_interface.get_available_files()
    return render_template('index.html', files=files)

@app.route('/api/files')
def api_files():
    """获取文件列表API"""
    files = web_interface.get_available_files()
    return jsonify({'files': files})

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """分析文件API"""
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'success': False, 'error': '文件名不能为空'})
    
    if not os.path.exists(filename):
        return jsonify({'success': False, 'error': '文件不存在'})
    
    result = web_interface.analyze_episode(filename)
    return jsonify(result)

@app.route('/api/analyze_all', methods=['POST'])
def api_analyze_all():
    """分析所有文件API"""
    try:
        from subtitle_analyzer import analyze_all_episodes_intelligently
        results = analyze_all_episodes_intelligently()
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🌐 启动Web界面...")
    print("🚀 访问地址: http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

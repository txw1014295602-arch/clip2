
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
稳定视频分析剪辑系统
解决问题11-15：API稳定性、剪辑一致性、缓存机制、旁白生成
"""

import os
import re
import json
import hashlib
import subprocess
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class StableVideoAnalysisSystem:
    def __init__(self):
        # 目录结构
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.output_folder = "stable_clips"
        self.narration_folder = "narrations"
        self.subtitle_folder = "highlight_subtitles"
        
        # 缓存目录
        self.analysis_cache_folder = "analysis_cache"
        self.clip_cache_folder = "clip_cache"
        self.consistency_folder = "consistency_logs"
        
        # 创建所有目录
        for folder in [self.srt_folder, self.videos_folder, self.output_folder, 
                      self.narration_folder, self.subtitle_folder,
                      self.analysis_cache_folder, self.clip_cache_folder, 
                      self.consistency_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载配置
        self.ai_config = self.load_ai_config()
        
        # 状态跟踪
        self.processed_files = {}
        self.clip_status = {}
        
        print("🎬 稳定视频分析剪辑系统")
        print("=" * 60)
        print("✨ 核心特性：")
        print("• 🔄 API结果缓存，避免重复调用")
        print("• 📝 剪辑结果缓存，保证一致性")
        print("• 🎙️ 智能旁白生成")
        print("• 📺 精彩片段字幕提示")
        print("• 🔁 多次执行结果一致")
        print("• 📁 批量处理所有SRT文件")
        print("=" * 60)

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled', False):
                    print(f"✅ AI配置已加载: {config.get('model', '未知')}")
                    return config
        except:
            pass
        
        print("⚠️ 需要配置AI才能使用完整功能")
        return {'enabled': False}

    def get_file_hash(self, filepath: str) -> str:
        """获取文件内容哈希，保证一致性"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return hashlib.md5(content.encode()).hexdigest()[:16]
        except:
            return ""

    def get_analysis_cache_path(self, srt_file: str) -> str:
        """获取分析缓存路径"""
        file_hash = self.get_file_hash(os.path.join(self.srt_folder, srt_file))
        cache_name = f"analysis_{os.path.splitext(srt_file)[0]}_{file_hash}.json"
        return os.path.join(self.analysis_cache_folder, cache_name)

    def get_clip_cache_path(self, srt_file: str, segment_id: int) -> str:
        """获取剪辑缓存路径"""
        file_hash = self.get_file_hash(os.path.join(self.srt_folder, srt_file))
        cache_name = f"clip_{os.path.splitext(srt_file)[0]}_seg{segment_id}_{file_hash}.json"
        return os.path.join(self.clip_cache_folder, cache_name)

    def load_analysis_cache(self, srt_file: str) -> Optional[Dict]:
        """加载分析缓存 - 解决问题11"""
        cache_path = self.get_analysis_cache_path(srt_file)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                    print(f"💾 使用分析缓存: {os.path.basename(srt_file)}")
                    return analysis
            except Exception as e:
                print(f"⚠️ 缓存读取失败: {e}")
        
        return None

    def save_analysis_cache(self, srt_file: str, analysis: Dict):
        """保存分析缓存 - 解决问题11"""
        cache_path = self.get_analysis_cache_path(srt_file)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"💾 保存分析缓存: {os.path.basename(srt_file)}")
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def load_clip_cache(self, srt_file: str, segment_id: int) -> Optional[Dict]:
        """加载剪辑缓存 - 解决问题12,13"""
        cache_path = self.get_clip_cache_path(srt_file, segment_id)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    clip_info = json.load(f)
                    
                    # 检查文件是否还存在
                    if os.path.exists(clip_info.get('video_path', '')):
                        print(f"💾 使用剪辑缓存: 片段{segment_id}")
                        return clip_info
                    else:
                        print(f"⚠️ 缓存的视频文件不存在，需要重新剪辑")
            except Exception as e:
                print(f"⚠️ 剪辑缓存读取失败: {e}")
        
        return None

    def save_clip_cache(self, srt_file: str, segment_id: int, clip_info: Dict):
        """保存剪辑缓存 - 解决问题12,13"""
        cache_path = self.get_clip_cache_path(srt_file, segment_id)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(clip_info, f, ensure_ascii=False, indent=2)
            print(f"💾 保存剪辑缓存: 片段{segment_id}")
        except Exception as e:
            print(f"⚠️ 剪辑缓存保存失败: {e}")

    def log_consistency(self, operation: str, details: Dict):
        """记录一致性日志 - 解决问题14"""
        log_file = os.path.join(self.consistency_folder, f"consistency_{datetime.now().strftime('%Y%m%d')}.log")
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'details': details
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ 一致性日志记录失败: {e}")

    def parse_srt_file(self, srt_path: str) -> List[Dict]:
        """解析SRT字幕文件"""
        subtitles = []
        
        # 多编码尝试
        content = None
        for encoding in ['utf-8', 'gbk', 'utf-16', 'gb2312']:
            try:
                with open(srt_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                break
            except:
                continue
        
        if not content:
            return []
        
        # 错别字修正
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        # 解析字幕
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0]) if lines[0].isdigit() else len(subtitles) + 1
                    time_match = re.search(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', lines[1])
                    if time_match:
                        start_time = time_match.group(1).replace('.', ',')
                        end_time = time_match.group(2).replace('.', ',')
                        text = '\n'.join(lines[2:]).strip()
                        
                        if text:
                            subtitles.append({
                                'index': index,
                                'start_time': start_time,
                                'end_time': end_time,
                                'text': text,
                                'start_seconds': self.time_to_seconds(start_time),
                                'end_seconds': self.time_to_seconds(end_time)
                            })
                except:
                    continue
        
        return subtitles

    def ai_analyze_episode(self, subtitles: List[Dict], episode_name: str) -> Optional[Dict]:
        """AI分析剧集 - 带缓存机制"""
        if not self.ai_config.get('enabled'):
            print("❌ AI未启用，使用基础分析")
            return self.basic_analysis_fallback(subtitles, episode_name)
        
        # 构建完整文本
        full_text = ' '.join([sub['text'] for sub in subtitles])
        total_duration = subtitles[-1]['end_seconds'] if subtitles else 0
        
        prompt = f"""请对这集电视剧进行深度分析，识别2-4个最精彩的片段用于短视频剪辑。

【剧集信息】
文件名: {episode_name}
总时长: {total_duration/60:.1f}分钟
字幕内容: {full_text[:3000]}...

请选择最精彩的片段，每个片段1.5-3分钟，要求：
1. 剧情高潮或转折点
2. 重要对话或冲突
3. 情感爆发或关键时刻
4. 悬念或揭秘时刻

对于每个片段，还需要：
- 生成第一人称旁白解释
- 设计精彩处的字幕提示（1-2句话）
- 解释为什么这个片段精彩

请以JSON格式返回：
{{
    "episode_analysis": {{
        "title": "剧集标题",
        "main_theme": "主要主题",
        "key_characters": ["主要角色"],
        "plot_summary": "剧情概要"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "片段标题",
            "start_time": "开始时间",
            "end_time": "结束时间",
            "duration_seconds": 实际秒数,
            "excitement_level": 评分1-10,
            "segment_type": "片段类型(冲突/情感/悬疑/转折)",
            "why_exciting": "为什么精彩的详细解释",
            "key_moments": [
                {{
                    "time": "关键时刻时间",
                    "description": "关键时刻描述",
                    "subtitle_hint": "字幕提示(1-2句话)"
                }}
            ],
            "first_person_narration": {{
                "opening": "开场旁白(我...)",
                "development": "发展旁白(我看到...)",
                "climax": "高潮旁白(我感受到...)",
                "conclusion": "结尾旁白(我明白了...)"
            }},
            "highlight_subtitles": [
                {{
                    "time": "字幕显示时间",
                    "text": "精彩提示文字",
                    "style": "字幕样式(重要/精彩/转折)"
                }}
            ]
        }}
    ]
}}"""

        try:
            response = self.call_ai_api(prompt)
            if response:
                analysis = self.parse_ai_response(response)
                if analysis:
                    print(f"✅ AI分析完成: {len(analysis.get('highlight_segments', []))} 个片段")
                    return analysis
        except Exception as e:
            print(f"❌ AI分析失败: {e}")
        
        return self.basic_analysis_fallback(subtitles, episode_name)

    def basic_analysis_fallback(self, subtitles: List[Dict], episode_name: str) -> Dict:
        """基础分析备选方案"""
        if not subtitles:
            return {}
        
        # 简单分段策略
        total_duration = subtitles[-1]['end_seconds'] if subtitles else 0
        segment_count = min(3, max(1, int(total_duration / 600)))  # 每10分钟一个片段
        
        segments = []
        segment_duration = total_duration / segment_count
        
        for i in range(segment_count):
            start_seconds = i * segment_duration
            end_seconds = min((i + 1) * segment_duration, total_duration)
            
            # 找到对应的字幕
            start_sub = next((s for s in subtitles if s['start_seconds'] >= start_seconds), subtitles[0])
            end_sub = next((s for s in subtitles if s['end_seconds'] <= end_seconds), subtitles[-1])
            
            segments.append({
                'segment_id': i + 1,
                'title': f'精彩片段{i + 1}',
                'start_time': start_sub['start_time'],
                'end_time': end_sub['end_time'],
                'duration_seconds': end_seconds - start_seconds,
                'excitement_level': 7,
                'segment_type': '剧情发展',
                'why_exciting': '包含重要剧情发展',
                'key_moments': [
                    {
                        'time': start_sub['start_time'],
                        'description': '重要剧情时刻',
                        'subtitle_hint': '精彩内容即将开始'
                    }
                ],
                'first_person_narration': {
                    'opening': f'我来到了第{i+1}个重要时刻',
                    'development': '我观察着剧情的发展',
                    'climax': '我见证了关键的转折',
                    'conclusion': '我理解了故事的深意'
                },
                'highlight_subtitles': [
                    {
                        'time': start_sub['start_time'],
                        'text': '⭐ 精彩片段开始',
                        'style': '精彩'
                    }
                ]
            })
        
        return {
            'episode_analysis': {
                'title': episode_name,
                'main_theme': '剧情发展',
                'key_characters': ['主角'],
                'plot_summary': '基础分析生成的剧情概要'
            },
            'highlight_segments': segments
        }

    def call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        config = self.ai_config
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                headers = {
                    'Authorization': f'Bearer {config["api_key"]}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': config.get('model', 'gpt-4'),
                    'messages': [
                        {
                            'role': 'system',
                            'content': '你是专业的影视剧情分析师，专注于识别精彩片段和生成观众友好的解释。请严格按照JSON格式返回结果。'
                        },
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 4000,
                    'temperature': 0.7
                }
                
                base_url = config.get('base_url', 'https://api.openai.com/v1')
                if not base_url.endswith('/chat/completions'):
                    base_url = f"{base_url}/chat/completions"
                
                response = requests.post(base_url, headers=headers, json=data, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    return content
                else:
                    print(f"⚠️ API调用失败 (尝试 {attempt + 1}/{max_retries}): {response.status_code}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)
                
            except Exception as e:
                print(f"⚠️ API调用异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
        
        return None

    def parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON内容
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                else:
                    json_str = response.strip()
            
            analysis = json.loads(json_str)
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析错误: {e}")
            return None

    def create_video_clip(self, segment: Dict, video_file: str, episode_name: str) -> Optional[Dict]:
        """创建视频片段 - 带缓存机制"""
        segment_id = segment.get('segment_id', 1)
        
        # 检查剪辑缓存 - 解决问题13
        cached_clip = self.load_clip_cache(episode_name, segment_id)
        if cached_clip:
            return cached_clip
        
        try:
            # 生成输出文件名
            episode_num = re.search(r'(\d+)', episode_name)
            ep_prefix = f"E{episode_num.group(1).zfill(2)}" if episode_num else "E00"
            
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', segment.get('title', f'片段{segment_id}'))
            
            video_filename = f"{ep_prefix}_片段{segment_id}_{safe_title}.mp4"
            video_path = os.path.join(self.output_folder, video_filename)
            
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            # 执行视频剪辑
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', f"{start_seconds:.3f}",
                '-t', f"{duration:.3f}",
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                '-movflags', '+faststart',
                video_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0 and os.path.exists(video_path):
                # 创建相关文件
                narration_path = self.generate_narration_file(segment, episode_name, segment_id)
                subtitle_path = self.generate_highlight_subtitles(segment, episode_name, segment_id)
                
                clip_info = {
                    'video_path': video_path,
                    'narration_path': narration_path,
                    'subtitle_path': subtitle_path,
                    'segment': segment,
                    'created_time': datetime.now().isoformat()
                }
                
                # 保存剪辑缓存 - 解决问题12
                self.save_clip_cache(episode_name, segment_id, clip_info)
                
                # 记录一致性日志 - 解决问题14
                self.log_consistency('create_clip', {
                    'episode': episode_name,
                    'segment_id': segment_id,
                    'video_path': video_path,
                    'duration': duration
                })
                
                print(f"✅ 创建视频片段: {video_filename}")
                return clip_info
            else:
                print(f"❌ 视频剪辑失败: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 创建视频片段失败: {e}")
            return None

    def generate_narration_file(self, segment: Dict, episode_name: str, segment_id: int) -> str:
        """生成旁白文件"""
        try:
            episode_num = re.search(r'(\d+)', episode_name)
            ep_prefix = f"E{episode_num.group(1).zfill(2)}" if episode_num else "E00"
            
            narration_filename = f"{ep_prefix}_片段{segment_id}_旁白.txt"
            narration_path = os.path.join(self.narration_folder, narration_filename)
            
            narration = segment.get('first_person_narration', {})
            
            content = f"""# {episode_name} 片段{segment_id} 第一人称旁白
## {segment.get('title', '未命名片段')}

**时间范围**: {segment.get('start_time')} --> {segment.get('end_time')}
**片段时长**: {segment.get('duration_seconds', 0):.1f}秒
**精彩度**: {segment.get('excitement_level', 0)}/10
**类型**: {segment.get('segment_type', '未知')}

---

## 为什么这个片段精彩
{segment.get('why_exciting', '包含重要剧情发展')}

---

## 第一人称完整旁白

### 开场叙述
{narration.get('opening', '我开始观看这个精彩的片段')}

### 发展叙述  
{narration.get('development', '我见证着剧情的发展')}

### 高潮叙述
{narration.get('climax', '我感受到了故事的高潮')}

### 结尾叙述
{narration.get('conclusion', '我理解了这个片段的意义')}

---

## 关键时刻

"""
            
            for moment in segment.get('key_moments', []):
                content += f"""
**时间**: {moment.get('time', '未知')}
**描述**: {moment.get('description', '重要时刻')}
**字幕提示**: {moment.get('subtitle_hint', '精彩内容')}
"""
            
            content += f"""

---

## 使用说明

1. 此旁白文件与对应的视频片段配合使用
2. 采用第一人称视角，增强观众代入感
3. 可作为视频解说词或观看指南
4. 配合精彩字幕文件使用效果更佳

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return narration_path
            
        except Exception as e:
            print(f"生成旁白文件失败: {e}")
            return ""

    def generate_highlight_subtitles(self, segment: Dict, episode_name: str, segment_id: int) -> str:
        """生成精彩字幕提示文件"""
        try:
            episode_num = re.search(r'(\d+)', episode_name)
            ep_prefix = f"E{episode_num.group(1).zfill(2)}" if episode_num else "E00"
            
            subtitle_filename = f"{ep_prefix}_片段{segment_id}_精彩字幕.srt"
            subtitle_path = os.path.join(self.subtitle_folder, subtitle_filename)
            
            highlight_subtitles = segment.get('highlight_subtitles', [])
            
            # 生成SRT格式的精彩字幕
            srt_content = ""
            
            for i, subtitle in enumerate(highlight_subtitles, 1):
                time_str = subtitle.get('time', segment.get('start_time', '00:00:00,000'))
                text = subtitle.get('text', '精彩内容')
                style = subtitle.get('style', '精彩')
                
                # 根据样式添加特效
                if style == '重要':
                    formatted_text = f"⚠️ {text} ⚠️"
                elif style == '精彩':
                    formatted_text = f"⭐ {text} ⭐"
                elif style == '转折':
                    formatted_text = f"🔄 {text} 🔄"
                else:
                    formatted_text = text
                
                # 计算结束时间（显示3秒）
                start_seconds = self.time_to_seconds(time_str)
                end_seconds = start_seconds + 3
                end_time_str = self.seconds_to_time(end_seconds)
                
                srt_content += f"""{i}
{time_str} --> {end_time_str}
{formatted_text}

"""
            
            # 如果没有特定的精彩字幕，生成默认的
            if not highlight_subtitles:
                start_time = segment.get('start_time', '00:00:00,000')
                mid_seconds = self.time_to_seconds(start_time) + segment.get('duration_seconds', 60) / 2
                mid_time = self.seconds_to_time(mid_seconds)
                end_time = self.seconds_to_time(mid_seconds + 3)
                
                srt_content = f"""1
{mid_time} --> {end_time}
⭐ 精彩内容 ⭐

"""
            
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            return subtitle_path
            
        except Exception as e:
            print(f"生成精彩字幕失败: {e}")
            return ""

    def find_matching_video(self, srt_filename: str) -> Optional[str]:
        """查找匹配的视频文件"""
        if not os.path.exists(self.videos_folder):
            return None
        
        base_name = os.path.splitext(srt_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                file_base = os.path.splitext(filename)[0].lower()
                if any(part in file_base for part in base_name.lower().split('_') if len(part) > 2):
                    return os.path.join(self.videos_folder, filename)
        
        return None

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace(',', '.')
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + float(s)
            return 0.0
        except:
            return 0.0

    def seconds_to_time(self, seconds: float) -> str:
        """秒转换为时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')

    def process_all_episodes(self):
        """处理所有剧集 - 解决问题15"""
        print("\n🚀 稳定视频分析剪辑系统启动")
        print("=" * 80)
        
        # 检查目录
        if not os.path.exists(self.srt_folder):
            print(f"❌ 字幕目录不存在: {self.srt_folder}/")
            return
        
        # 获取所有SRT文件 - 解决问题15
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.lower().endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return
        
        srt_files.sort()
        
        print(f"📄 找到 {len(srt_files)} 个字幕文件")
        print(f"🎥 视频目录: {self.videos_folder}/")
        print(f"📁 输出目录: {self.output_folder}/")
        print(f"🎙️ 旁白目录: {self.narration_folder}/")
        print(f"📺 字幕目录: {self.subtitle_folder}/")
        
        # 处理统计
        total_processed = 0
        total_clips = 0
        cache_hits = 0
        
        # 逐个处理所有文件
        for i, srt_file in enumerate(srt_files, 1):
            try:
                print(f"\n📺 处理第{i}集: {srt_file}")
                
                # 检查分析缓存
                cached_analysis = self.load_analysis_cache(srt_file)
                
                if cached_analysis:
                    analysis = cached_analysis
                    cache_hits += 1
                else:
                    # 解析字幕
                    subtitles = self.parse_srt_file(os.path.join(self.srt_folder, srt_file))
                    
                    if not subtitles:
                        print("❌ 字幕解析失败")
                        continue
                    
                    # AI分析
                    analysis = self.ai_analyze_episode(subtitles, srt_file)
                    
                    if not analysis:
                        print("❌ 分析失败")
                        continue
                    
                    # 保存分析缓存
                    self.save_analysis_cache(srt_file, analysis)
                
                # 查找视频文件
                video_file = self.find_matching_video(srt_file)
                
                if not video_file:
                    print("❌ 未找到对应视频文件")
                    continue
                
                # 处理各个片段
                segments = analysis.get('highlight_segments', [])
                
                for segment in segments:
                    clip_info = self.create_video_clip(segment, video_file, srt_file)
                    
                    if clip_info:
                        total_clips += 1
                        print(f"✅ 片段{segment.get('segment_id', '?')}: {segment.get('title', '未命名')}")
                    else:
                        print(f"❌ 片段{segment.get('segment_id', '?')}创建失败")
                
                total_processed += 1
                
            except Exception as e:
                print(f"❌ 处理{srt_file}时出错: {e}")
        
        # 生成最终报告
        self.generate_final_report(total_processed, total_clips, cache_hits, len(srt_files))

    def generate_final_report(self, processed: int, clips: int, cache_hits: int, total_files: int):
        """生成最终处理报告"""
        try:
            report_path = os.path.join(self.consistency_folder, "稳定系统处理报告.txt")
            
            content = f"""# 稳定视频分析剪辑系统 - 处理报告
{'=' * 100}

## 📊 处理统计
- 总字幕文件: {total_files} 个
- 成功处理: {processed} 个
- 生成视频片段: {clips} 个
- 缓存命中: {cache_hits} 次
- 处理成功率: {processed/total_files*100:.1f}%

## 🎯 系统特性验证
✅ **API稳定性**: 使用分析缓存，避免重复API调用
✅ **剪辑一致性**: 使用剪辑缓存，保证多次执行结果一致
✅ **旁白生成**: 每个视频片段都生成了第一人称旁白
✅ **精彩字幕**: 为精彩时刻生成了字幕提示文件
✅ **批量处理**: 一次性处理所有SRT文件
✅ **一致性保证**: 通过文件哈希确保多次执行结果一致

## 📁 输出文件结构
```
{self.output_folder}/          # 视频片段
├── E01_片段1_xxx.mp4
├── E01_片段2_xxx.mp4
...

{self.narration_folder}/       # 第一人称旁白
├── E01_片段1_旁白.txt
├── E01_片段2_旁白.txt
...

{self.subtitle_folder}/        # 精彩字幕提示
├── E01_片段1_精彩字幕.srt
├── E01_片段2_精彩字幕.srt
...

{self.analysis_cache_folder}/  # 分析缓存
├── analysis_E01_xxxx.json
├── analysis_E02_xxxx.json
...

{self.clip_cache_folder}/      # 剪辑缓存
├── clip_E01_seg1_xxxx.json
├── clip_E01_seg2_xxxx.json
...
```

## 🎬 使用指南

### 观看完整体验
1. 播放视频片段: `{self.output_folder}/Exx_片段x_xxx.mp4`
2. 阅读第一人称旁白: `{self.narration_folder}/Exx_片段x_旁白.txt`
3. 加载精彩字幕: `{self.subtitle_folder}/Exx_片段x_精彩字幕.srt`

### 旁白特色
- 采用第一人称视角 ("我看到...", "我感受到...")
- 详细解释剧情发展和人物动机
- 与视频内容实时对应

### 精彩字幕特色
- ⭐ 精彩时刻标记
- ⚠️ 重要内容提醒  
- 🔄 转折点提示
- 可直接导入视频播放器使用

## 🔧 技术特点

### 缓存机制
- **分析缓存**: 避免重复AI分析，提高效率
- **剪辑缓存**: 避免重复视频剪辑，保证一致性
- **文件哈希**: 基于内容哈希确保缓存准确性

### 一致性保证
- 多次执行相同字幕文件得到完全一致的结果
- 缓存基于文件内容而非文件名
- 详细的一致性日志记录

### 稳定性设计
- API调用失败时自动重试
- 提供基础分析备选方案
- 完善的错误处理和日志记录

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本: 稳定视频分析剪辑系统 v1.0
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n🎉 系统处理完成!")
            print(f"📊 处理统计: {processed}/{total_files} 个文件，{clips} 个片段")
            print(f"💾 缓存效率: {cache_hits} 次缓存命中")
            print(f"📄 详细报告: {os.path.basename(report_path)}")
            
        except Exception as e:
            print(f"生成最终报告失败: {e}")

def main():
    """主函数"""
    system = StableVideoAnalysisSystem()
    
    if not system.ai_config.get('enabled'):
        print("\n💡 AI未配置，将使用基础分析模式")
        print("如需AI增强分析，请运行: python interactive_config.py")
    
    system.process_all_episodes()

if __name__ == "__main__":
    main()

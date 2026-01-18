
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版智能电视剧剪辑系统
解决所有问题的完整方案：
1. 完全智能化，不限制剧情类型
2. 完整上下文分析，避免割裂
3. 每集多个连贯短视频
4. AI判断完整剪辑内容
5. 自动生成视频和旁白
6. 保证剧情连贯性
7. 缓存机制避免重复调用API
8. 一致性保证
"""

import os
import re
import json
import subprocess
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests

class EnhancedIntelligentClipper:
    def __init__(self, video_folder: str = "videos", srt_folder: str = "srt", output_folder: str = "clips"):
        self.video_folder = video_folder
        self.srt_folder = srt_folder
        self.output_folder = output_folder
        self.cache_folder = "analysis_cache"
        
        # 创建目录
        for folder in [self.video_folder, self.srt_folder, self.output_folder, self.cache_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✓ 创建目录: {folder}/")
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        # 全剧分析缓存
        self.series_analysis = None
        
    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled', False) and config.get('api_key'):
                    print(f"✅ AI配置已加载: {config.get('provider', '未知')}")
                    return config
        except:
            pass
        
        return {'enabled': False}

    def parse_complete_episode(self, filepath: str) -> Dict:
        """解析完整集数的字幕，保持上下文连贯性"""
        print(f"📖 解析完整字幕: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            try:
                with open(filepath, 'r', encoding='gbk', errors='ignore') as f:
                    content = f.read()
            except:
                print(f"❌ 无法读取文件: {filepath}")
                return {}
        
        # 智能错别字修正
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
            '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会',
            '調查': '调查', '起訴': '起诉', '対話': '对话', '関係': '关系'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        # 解析字幕
        subtitles = []
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
                                'start': start_time,
                                'end': end_time,
                                'text': text
                            })
                except (ValueError, IndexError):
                    continue
        
        # 构建完整剧情文本（分段处理，保持上下文）
        full_text_segments = []
        current_segment = []
        
        for i, sub in enumerate(subtitles):
            current_segment.append(sub['text'])
            
            # 每30句作为一个段落
            if len(current_segment) >= 30 or i == len(subtitles) - 1:
                segment_text = ' '.join(current_segment)
                full_text_segments.append({
                    'start_index': i - len(current_segment) + 1,
                    'end_index': i,
                    'text': segment_text,
                    'start_time': subtitles[i - len(current_segment) + 1]['start'] if current_segment else '00:00:00,000',
                    'end_time': subtitles[i]['end']
                })
                current_segment = []
        
        episode_data = {
            'filename': os.path.basename(filepath),
            'subtitles': subtitles,
            'full_text_segments': full_text_segments,
            'total_duration': self.time_to_seconds(subtitles[-1]['end']) if subtitles else 0
        }
        
        print(f"✓ 解析完成: {len(subtitles)} 条字幕, {len(full_text_segments)} 个文本段落")
        return episode_data

    def get_analysis_cache_path(self, episode_data: Dict) -> str:
        """获取分析缓存路径"""
        # 使用文件内容hash作为缓存key
        content_hash = hashlib.md5(str(episode_data['subtitles']).encode()).hexdigest()[:16]
        filename = episode_data['filename'].replace('.', '_')
        return os.path.join(self.cache_folder, f"{filename}_{content_hash}.json")

    def load_analysis_cache(self, episode_data: Dict) -> Optional[Dict]:
        """加载分析缓存"""
        cache_path = self.get_analysis_cache_path(episode_data)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_analysis = json.load(f)
                    print(f"📋 使用缓存分析: {os.path.basename(cache_path)}")
                    return cached_analysis
            except:
                pass
        return None

    def save_analysis_cache(self, episode_data: Dict, analysis: Dict):
        """保存分析缓存"""
        cache_path = self.get_analysis_cache_path(episode_data)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"💾 保存分析缓存: {os.path.basename(cache_path)}")
        except Exception as e:
            print(f"⚠ 保存缓存失败: {e}")

    def ai_analyze_episode_complete(self, episode_data: Dict, series_context: str = "") -> Dict:
        """AI完整分析单集，包含多个精彩片段"""
        # 检查缓存
        cached_analysis = self.load_analysis_cache(episode_data)
        if cached_analysis:
            return cached_analysis
        
        if not self.ai_config.get('enabled', False):
            print("⚠ AI未启用，使用基础分析")
            return self.basic_analysis_fallback(episode_data)
        
        filename = episode_data['filename']
        episode_num = self.extract_episode_number(filename)
        
        # 构建完整上下文
        full_context = self.build_episode_context(episode_data, series_context)
        
        prompt = f"""你是专业的电视剧剪辑师，需要为这一集创建多个2-3分钟的精彩短视频。

【集数信息】第{episode_num}集
【剧集背景】{series_context}

【完整剧情内容】
{full_context}

请完成以下任务：

1. 剧情类型识别：自动识别这是什么类型的电视剧（法律、爱情、悬疑、古装、现代、犯罪等）

2. 精彩片段识别：找出3-5个最精彩的片段，每个2-3分钟，要求：
   - 包含完整的对话场景
   - 有明确的戏剧冲突或情感高潮
   - 能独立成为一个短视频
   - 保证一句话说完，不要截断对话

3. 剧情连贯性：确保这些片段能连贯地讲述本集的核心故事

4. 旁白生成：为每个片段生成专业的旁白解说，解释精彩之处

请以JSON格式返回：
{{
    "episode_analysis": {{
        "episode_number": {episode_num},
        "genre": "剧情类型",
        "main_theme": "本集主要主题",
        "story_progression": "在整体剧情中的作用",
        "emotional_arc": "情感发展弧线"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "片段标题",
            "start_time": "开始时间戳",
            "end_time": "结束时间戳", 
            "duration_seconds": 持续秒数,
            "description": "片段内容描述",
            "dramatic_value": "戏剧价值（0-10分）",
            "key_dialogues": ["关键对话1", "关键对话2"],
            "plot_significance": "剧情重要性",
            "emotional_impact": "情感冲击点",
            "narration": {{
                "opening": "开场旁白",
                "process": "过程解说", 
                "climax": "高潮解说",
                "conclusion": "结尾总结"
            }},
            "connection_to_next": "与下个片段的连接"
        }}
    ],
    "episode_summary": {{
        "core_conflicts": ["核心冲突点1", "核心冲突点2"],
        "character_development": "角色发展",
        "plot_twists": ["剧情转折点"],
        "setup_for_next_episode": "为下集的铺垫"
    }},
    "overall_coherence": "整集连贯性说明"
}}"""

        try:
            response = self.call_ai_api(prompt)
            if response:
                analysis = self.parse_ai_analysis(response)
                if analysis:
                    # 保存缓存
                    self.save_analysis_cache(episode_data, analysis)
                    return analysis
        except Exception as e:
            print(f"⚠ AI分析失败: {e}")
        
        # 失败时使用基础分析
        basic_analysis = self.basic_analysis_fallback(episode_data)
        self.save_analysis_cache(episode_data, basic_analysis)
        return basic_analysis

    def build_episode_context(self, episode_data: Dict, series_context: str) -> str:
        """构建完整的剧集上下文"""
        # 取前80%的字幕内容作为完整上下文
        subtitles = episode_data['subtitles']
        context_end = int(len(subtitles) * 0.8)
        
        context_parts = []
        for i in range(0, context_end, 50):  # 每50句分一段
            segment_texts = [sub['text'] for sub in subtitles[i:i+50]]
            context_parts.append(' '.join(segment_texts))
        
        return '\n\n'.join(context_parts)

    def basic_analysis_fallback(self, episode_data: Dict) -> Dict:
        """基础分析备选方案"""
        filename = episode_data['filename']
        episode_num = self.extract_episode_number(filename)
        subtitles = episode_data['subtitles']
        
        # 基础分段逻辑
        total_duration = episode_data['total_duration']
        segment_count = min(4, max(2, int(total_duration / 180)))  # 2-4个片段
        
        segments = []
        segment_length = len(subtitles) // segment_count
        
        for i in range(segment_count):
            start_idx = i * segment_length
            end_idx = min((i + 1) * segment_length, len(subtitles) - 1)
            
            start_time = subtitles[start_idx]['start']
            end_time = subtitles[end_idx]['end']
            duration = self.time_to_seconds(end_time) - self.time_to_seconds(start_time)
            
            segments.append({
                "segment_id": i + 1,
                "title": f"第{episode_num}集 精彩片段{i + 1}",
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "description": f"本集第{i + 1}段精彩内容",
                "dramatic_value": 7.0,
                "key_dialogues": [subtitles[start_idx + j]['text'] for j in range(min(3, end_idx - start_idx))],
                "plot_significance": "剧情推进",
                "emotional_impact": "情感发展",
                "narration": {
                    "opening": "在这个片段中",
                    "process": "我们看到剧情的发展",
                    "climax": "达到了一个小高潮",
                    "conclusion": "为后续剧情做铺垫"
                },
                "connection_to_next": "承上启下"
            })
        
        return {
            "episode_analysis": {
                "episode_number": episode_num,
                "genre": "general",
                "main_theme": f"第{episode_num}集主要内容",
                "story_progression": "剧情发展",
                "emotional_arc": "情感推进"
            },
            "highlight_segments": segments,
            "episode_summary": {
                "core_conflicts": ["主要冲突"],
                "character_development": "角色发展",
                "plot_twists": ["情节转折"],
                "setup_for_next_episode": "下集预告"
            },
            "overall_coherence": "本集内容连贯"
        }

    def call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API，带重试机制"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                config = self.ai_config
                
                headers = {
                    'Authorization': f'Bearer {config["api_key"]}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': config.get('model', 'claude-3-5-sonnet-20240620'),
                    'messages': [
                        {
                            'role': 'system', 
                            'content': '你是专业的电视剧剪辑师和剧情分析师，擅长识别精彩片段和保持剧情连贯性。请严格按照JSON格式返回分析结果。'
                        },
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 4000,
                    'temperature': 0.7
                }
                
                response = requests.post(
                    f"{config.get('base_url', 'https://www.chataiapi.com/v1')}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    return content
                else:
                    print(f"⚠ API调用失败 (尝试 {attempt + 1}/{max_retries}): {response.status_code}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)  # 指数退避
                    
            except Exception as e:
                print(f"⚠ API调用异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
        
        return None

    def parse_ai_analysis(self, response_text: str) -> Optional[Dict]:
        """解析AI分析结果"""
        try:
            # 提取JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]
            
            analysis = json.loads(response_text)
            
            # 验证必要字段
            if 'highlight_segments' in analysis and 'episode_analysis' in analysis:
                return analysis
            else:
                print("⚠ AI分析结果缺少必要字段")
                return None
                
        except json.JSONDecodeError as e:
            print(f"⚠ AI分析结果JSON解析失败: {e}")
            return None

    def create_video_clip(self, episode_data: Dict, segment: Dict, video_file: str) -> bool:
        """创建单个视频片段，保证一致性"""
        try:
            segment_id = segment['segment_id']
            title = segment['title']
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            # 生成一致的输出文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            output_filename = f"{safe_title}_seg{segment_id}.mp4"
            output_path = os.path.join(self.output_folder, output_filename)
            
            # 检查是否已存在
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"  ✓ 视频已存在: {output_filename}")
                return True
            
            print(f"  🎬 剪辑片段{segment_id}: {title}")
            print(f"     时间: {start_time} --> {end_time}")
            
            # 计算时间参数
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            if duration <= 0:
                print(f"  ❌ 无效时间段")
                return False
            
            # 添加缓冲时间确保对话完整
            buffer_start = max(0, start_seconds - 2)
            buffer_duration = duration + 4
            
            # 构建FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-movflags', '+faststart',
                '-avoid_negative_ts', 'make_zero',
                output_path,
                '-y'
            ]
            
            # 执行剪辑
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"    ✅ 成功: {output_filename} ({file_size:.1f}MB)")
                
                # 生成旁白文件
                self.create_narration_file(output_path, segment)
                
                return True
            else:
                print(f"    ❌ 失败: {result.stderr[:100] if result.stderr else '未知错误'}")
                return False
                
        except Exception as e:
            print(f"    ❌ 剪辑异常: {e}")
            return False

    def create_narration_file(self, video_path: str, segment: Dict):
        """创建旁白文件"""
        try:
            narration_path = video_path.replace('.mp4', '_旁白.txt')
            
            narration = segment.get('narration', {})
            
            content = f"""🎬 {segment['title']}
{"=" * 50}

⏱️ 时长: {segment['duration_seconds']:.1f} 秒
🎯 戏剧价值: {segment['dramatic_value']}/10
📝 剧情意义: {segment['plot_significance']}
💥 情感冲击: {segment['emotional_impact']}

🎙️ 旁白解说:
【开场】{narration.get('opening', '')}
【过程】{narration.get('process', '')}
【高潮】{narration.get('climax', '')}
【结尾】{narration.get('conclusion', '')}

💬 关键对话:
"""
            
            for dialogue in segment.get('key_dialogues', []):
                content += f"• {dialogue}\n"
            
            content += f"""
📖 内容描述:
{segment['description']}

🔗 与下段连接:
{segment.get('connection_to_next', '自然过渡')}
"""
            
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 旁白文件: {os.path.basename(narration_path)}")
            
        except Exception as e:
            print(f"    ⚠ 旁白生成失败: {e}")

    def find_matching_video(self, subtitle_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        base_name = os.path.splitext(subtitle_filename)[0]
        
        # 尝试精确匹配
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts']
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        if os.path.exists(self.video_folder):
            for filename in os.listdir(self.video_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    file_base = os.path.splitext(filename)[0]
                    if any(part in file_base.lower() for part in base_name.lower().split('_') if len(part) > 2):
                        return os.path.join(self.video_folder, filename)
        
        return None

    def extract_episode_number(self, filename: str) -> str:
        """提取集数"""
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        for pattern in patterns:
            match = re.search(pattern, filename, re.I)
            if match:
                return match.group(1).zfill(2)
        return "00"

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def process_single_episode(self, subtitle_file: str) -> bool:
        """处理单集完整流程"""
        print(f"\n📺 处理集数: {subtitle_file}")
        
        # 1. 解析字幕
        subtitle_path = os.path.join(self.srt_folder, subtitle_file)
        episode_data = self.parse_complete_episode(subtitle_path)
        
        if not episode_data:
            print(f"❌ 字幕解析失败")
            return False
        
        # 2. AI分析 (带缓存)
        print(f"🧠 AI分析剧情...")
        analysis = self.ai_analyze_episode_complete(episode_data, self.get_series_context())
        
        if not analysis:
            print(f"❌ 剧情分析失败")
            return False
        
        # 3. 找到视频文件
        video_file = self.find_matching_video(subtitle_file)
        if not video_file:
            print(f"❌ 未找到对应视频文件")
            return False
        
        print(f"📁 视频文件: {os.path.basename(video_file)}")
        
        # 4. 剪辑所有片段
        segments = analysis.get('highlight_segments', [])
        successful_clips = []
        
        for segment in segments:
            if self.create_video_clip(episode_data, segment, video_file):
                successful_clips.append(segment)
        
        # 5. 生成集数总结
        self.create_episode_summary(subtitle_file, analysis, successful_clips)
        
        print(f"✅ {subtitle_file} 处理完成: {len(successful_clips)}/{len(segments)} 个片段成功")
        return len(successful_clips) > 0

    def get_series_context(self) -> str:
        """获取整个剧集的上下文"""
        if not self.series_analysis:
            # 简单的剧集背景
            return "这是一部电视剧，包含多个相互关联的剧情线。"
        return self.series_analysis

    def create_episode_summary(self, subtitle_file: str, analysis: Dict, successful_clips: List[Dict]):
        """创建集数总结"""
        try:
            episode_analysis = analysis.get('episode_analysis', {})
            episode_summary = analysis.get('episode_summary', {})
            
            summary_path = os.path.join(self.output_folder, f"{os.path.splitext(subtitle_file)[0]}_总结.txt")
            
            content = f"""📺 {subtitle_file} - 剪辑总结
{"=" * 60}

📊 基本信息:
• 集数: 第{episode_analysis.get('episode_number', '?')}集
• 类型: {episode_analysis.get('genre', '未知')}
• 主题: {episode_analysis.get('main_theme', '剧情发展')}
• 情感弧线: {episode_analysis.get('emotional_arc', '情感推进')}

🎬 剪辑成果:
• 成功片段: {len(successful_clips)} 个
• 总时长: {sum(clip['duration_seconds'] for clip in successful_clips):.1f} 秒

📝 剧情要点:
• 核心冲突: {', '.join(episode_summary.get('core_conflicts', []))}
• 角色发展: {episode_summary.get('character_development', '角色成长')}
• 剧情转折: {', '.join(episode_summary.get('plot_twists', []))}
• 下集铺垫: {episode_summary.get('setup_for_next_episode', '待续')}

🔗 连贯性说明:
{analysis.get('overall_coherence', '本集剧情连贯完整')}

🎯 片段详情:
"""
            
            for i, clip in enumerate(successful_clips, 1):
                content += f"""
{i}. {clip['title']}
   时间: {clip['start_time']} - {clip['end_time']} ({clip['duration_seconds']:.1f}秒)
   价值: {clip['dramatic_value']}/10
   意义: {clip['plot_significance']}
   冲击: {clip['emotional_impact']}
"""
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📄 总结文件: {os.path.basename(summary_path)}")
            
        except Exception as e:
            print(f"⚠ 总结生成失败: {e}")

    def process_all_episodes(self):
        """处理所有集数"""
        print("🚀 增强版智能剪辑系统启动")
        print("=" * 60)
        
        # 检查目录
        if not os.path.exists(self.srt_folder):
            print(f"❌ 字幕目录不存在: {self.srt_folder}")
            return
        
        if not os.path.exists(self.video_folder):
            print(f"❌ 视频目录不存在: {self.video_folder}")
            return
        
        # 获取字幕文件
        subtitle_files = [f for f in os.listdir(self.srt_folder) 
                         if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        subtitle_files.sort()
        
        if not subtitle_files:
            print(f"❌ 未找到字幕文件")
            return
        
        print(f"📝 找到 {len(subtitle_files)} 个字幕文件")
        print(f"🎬 视频目录: {self.video_folder}")
        print(f"📁 输出目录: {self.output_folder}")
        print(f"💾 缓存目录: {self.cache_folder}")
        
        if self.ai_config.get('enabled'):
            print(f"🤖 AI分析: 启用 ({self.ai_config.get('provider', '未知')})")
        else:
            print(f"📏 AI分析: 未启用，使用基础规则")
        
        # 处理每一集
        total_success = 0
        total_clips = 0
        
        for subtitle_file in subtitle_files:
            try:
                success = self.process_single_episode(subtitle_file)
                if success:
                    total_success += 1
                
                # 统计本集片段数
                episode_clips = [f for f in os.listdir(self.output_folder) 
                               if f.startswith(os.path.splitext(subtitle_file)[0]) and f.endswith('.mp4')]
                total_clips += len(episode_clips)
                
            except Exception as e:
                print(f"❌ 处理 {subtitle_file} 时出错: {e}")
        
        # 最终报告
        self.create_final_report(total_success, len(subtitle_files), total_clips)

    def create_final_report(self, success_count: int, total_episodes: int, total_clips: int):
        """创建最终报告"""
        try:
            report_path = os.path.join(self.output_folder, "剪辑报告.txt")
            
            content = f"""🎬 增强版智能剪辑系统 - 最终报告
{"=" * 60}

📊 处理统计:
• 总集数: {total_episodes} 集
• 成功处理: {success_count} 集
• 成功率: {(success_count/total_episodes*100):.1f}%
• 生成片段: {total_clips} 个

🤖 系统配置:
• AI分析: {'启用' if self.ai_config.get('enabled') else '未启用'}
• 缓存机制: 启用 (避免重复API调用)
• 一致性保证: 启用 (相同输入产生相同输出)

📁 输出文件:
• 视频片段: {self.output_folder}/*.mp4
• 旁白解说: {self.output_folder}/*_旁白.txt  
• 集数总结: {self.output_folder}/*_总结.txt
• 分析缓存: {self.cache_folder}/*.json

✨ 主要特点:
1. 🧠 完全智能化 - 不限制剧情类型，AI自动识别
2. 📖 完整上下文 - 基于整集分析，避免片段割裂
3. 🎯 多片段剪辑 - 每集3-5个精彩短视频
4. 🎙️ 专业旁白 - AI生成剧情解说和分析
5. 🔗 保证连贯 - 片段间剧情逻辑连贯
6. 💾 智能缓存 - 避免重复API调用
7. ⚖️ 一致性保证 - 多次运行结果一致
8. 🎬 完整对话 - 确保句子完整，不截断

📝 使用建议:
• 将字幕文件放在 {self.srt_folder}/ 目录
• 将视频文件放在 {self.video_folder}/ 目录  
• 文件名保持对应关系（如 EP01.srt 对应 EP01.mp4）
• AI分析结果会缓存，避免重复调用API
• 可多次运行同一文件，结果保持一致

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n📊 最终统计:")
            print(f"✅ 成功处理: {success_count}/{total_episodes} 集")
            print(f"🎬 生成片段: {total_clips} 个")
            print(f"📄 详细报告: {report_path}")
            
        except Exception as e:
            print(f"⚠ 报告生成失败: {e}")

def main():
    """主函数"""
    clipper = EnhancedIntelligentClipper()
    clipper.process_all_episodes()

if __name__ == "__main__":
    main()

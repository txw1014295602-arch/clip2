
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整AI智能剪辑系统
解决所有需求：
1. 每集多个精彩短视频，AI判断完整内容
2. 实际剪辑生成视频文件
3. videos/和srt/目录结构
4. 生成旁白解说文件
"""

import os
import re
import json
import subprocess
import hashlib
from typing import List, Dict, Optional
from datetime import datetime

class CompleteAIClipper:
    def __init__(self):
        self.srt_folder = "srt"
        self.video_folder = "videos"  
        self.output_folder = "ai_clips"
        self.cache_folder = "analysis_cache"
        
        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        # 剧集上下文
        self.series_context = []
        
        print("🤖 完整AI智能剪辑系统启动")
        print("=" * 60)
        print("✨ 功能特性：")
        print("• 每集多个精彩短视频，AI智能判断内容")
        print("• 实际剪辑生成视频文件")
        print("• 标准目录结构：videos/ + srt/")
        print("• 自动生成专业旁白解说")
        print("• 完整剧情连贯性保证")
        print("=" * 60)

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled', False) and config.get('api_key'):
                    print(f"✅ AI配置已加载: {config.get('model', '未知模型')}")
                    return config
        except:
            pass
        
        print("⚠️ AI未配置，将使用基础规则分析")
        return {'enabled': False}

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """智能解析字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")
        
        # 尝试多种编码
        content = None
        for encoding in ['utf-8', 'gbk', 'utf-16', 'gb2312']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    break
            except:
                continue
        
        if not content:
            print("❌ 字幕文件读取失败")
            return []
        
        # 智能错别字修正
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        # 解析字幕条目
        subtitles = []
        
        # 支持SRT格式
        if '-->' in content:
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
                                    'text': text,
                                    'start_seconds': self._time_to_seconds(start_time),
                                    'end_seconds': self._time_to_seconds(end_time)
                                })
                    except:
                        continue
        
        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def ai_analyze_episode(self, subtitles: List[Dict], episode_name: str) -> Optional[Dict]:
        """AI分析一集，生成多个精彩片段"""
        if not self.ai_config.get('enabled', False):
            print("⚠️ AI未启用，使用基础分析")
            return self.basic_analysis_fallback(subtitles, episode_name)
        
        # 检查缓存
        cache_path = self._get_cache_path(episode_name, subtitles)
        cached_analysis = self._load_cache(cache_path)
        if cached_analysis:
            print(f"📂 使用缓存分析: {episode_name}")
            return cached_analysis
        
        episode_num = self._extract_episode_number(episode_name)
        
        # 构建完整剧情文本
        full_script = self._build_full_script(subtitles)
        
        # 构建上下文信息
        context_info = self._build_context(episode_num)
        
        # AI分析提示词
        prompt = f"""你是专业的电视剧剧情分析师。请分析这一集并为短视频剪辑提供建议。

【当前集数】第{episode_num}集
【剧集上下文】{context_info}

【完整剧情内容】
{full_script}

请分析这一集并生成多个精彩短视频片段，每个片段1-3分钟。

要求：
1. 每个片段要有完整的剧情结构（开始-发展-高潮-结尾）
2. 选择最具吸引力和代表性的内容
3. 保证片段之间的连贯性
4. 每个片段都要能独立成篇，同时融入整体故事

请返回JSON格式：
{{
    "episode_analysis": {{
        "episode_number": "{episode_num}",
        "drama_genre": "自动识别的剧情类型",
        "main_theme": "本集主要主题",
        "key_characters": ["主要角色列表"],
        "story_significance": "在整个剧集中的重要性"
    }},
    "highlight_segments": [
        {{
            "segment_id": 1,
            "title": "片段标题",
            "start_time": "HH:MM:SS,mmm",
            "end_time": "HH:MM:SS,mmm",
            "duration_seconds": 实际秒数,
            "segment_type": "剧情类型(冲突/情感/悬疑/转折等)",
            "selection_reason": "选择这个片段的原因",
            "story_completeness": "剧情完整性说明",
            "key_dialogues": [
                {{"timestamp": "HH:MM:SS,mmm", "speaker": "角色", "line": "重要台词", "significance": "台词重要性"}}
            ],
            "emotional_arc": "情感发展轨迹",
            "visual_highlights": "视觉亮点",
            "audience_hook": "吸引观众的要点"
        }}
    ],
    "episode_continuity": {{
        "previous_connection": "与前集的联系",
        "next_episode_setup": "为下集的铺垫",
        "story_threads": ["持续的故事线索"]
    }},
    "narration_suggestions": {{
        "overall_tone": "整体旁白风格",
        "key_points_to_explain": ["需要解释的关键点"],
        "emotional_guidance": "情感引导建议"
    }}
}}

分析原则：
- 优先选择戏剧冲突强烈的片段
- 确保每个片段有完整的故事弧线
- 重视角色发展和情感变化
- 考虑视觉效果和对话质量
- 保持与整体剧情的连贯性"""

        try:
            print(f"🤖 AI深度分析中...")
            response = self._call_ai_api(prompt)
            
            if response:
                analysis = self._parse_ai_response(response)
                if analysis and self._validate_analysis(analysis, subtitles):
                    # 保存缓存
                    self._save_cache(cache_path, analysis)
                    
                    # 更新剧集上下文
                    self._update_series_context(analysis, episode_name)
                    
                    return analysis
            
            print("⚠️ AI分析失败，使用基础分析")
            return self.basic_analysis_fallback(subtitles, episode_name)
            
        except Exception as e:
            print(f"❌ AI分析出错: {e}")
            return self.basic_analysis_fallback(subtitles, episode_name)

    def basic_analysis_fallback(self, subtitles: List[Dict], episode_name: str) -> Dict:
        """基础分析备选方案"""
        episode_num = self._extract_episode_number(episode_name)
        
        # 智能片段识别
        segments = self._identify_segments(subtitles)
        
        return {
            "episode_analysis": {
                "episode_number": episode_num,
                "drama_genre": "通用剧情",
                "main_theme": f"第{episode_num}集核心剧情",
                "key_characters": ["主要角色"],
                "story_significance": "重要剧情发展"
            },
            "highlight_segments": segments,
            "episode_continuity": {
                "previous_connection": "与前集的自然延续",
                "next_episode_setup": "为下集剧情发展铺垫",
                "story_threads": ["主线剧情"]
            },
            "narration_suggestions": {
                "overall_tone": "专业解说",
                "key_points_to_explain": ["核心剧情", "角色关系"],
                "emotional_guidance": "情感共鸣引导"
            }
        }

    def _identify_segments(self, subtitles: List[Dict]) -> List[Dict]:
        """智能识别精彩片段"""
        segments = []
        
        # 关键词评分
        keywords = {
            '冲突': ['争论', '吵架', '打斗', '对抗', '冲突', '矛盾'],
            '情感': ['爱', '恨', '情', '心', '感动', '痛苦'],
            '悬疑': ['真相', '秘密', '发现', '线索', '调查'],
            '转折': ['突然', '没想到', '原来', '竟然', '反转']
        }
        
        # 评分每个字幕
        scored_subtitles = []
        for i, subtitle in enumerate(subtitles):
            score = 0
            text = subtitle['text']
            
            # 关键词评分
            for category, words in keywords.items():
                for word in words:
                    if word in text:
                        score += 2
            
            # 情感强度评分
            score += text.count('！') * 1.5
            score += text.count('？') * 1
            
            if score > 3:
                scored_subtitles.append((i, score, subtitle))
        
        # 聚类成片段
        if scored_subtitles:
            scored_subtitles.sort(key=lambda x: x[1], reverse=True)
            
            # 选择前3个高分区域
            for i, (center_idx, score, center_sub) in enumerate(scored_subtitles[:3]):
                # 扩展到合适长度
                start_idx = max(0, center_idx - 20)
                end_idx = min(len(subtitles) - 1, center_idx + 20)
                
                # 确保最少60秒
                while end_idx < len(subtitles) - 1:
                    duration = subtitles[end_idx]['end_seconds'] - subtitles[start_idx]['start_seconds']
                    if duration >= 60:
                        break
                    end_idx += 1
                
                duration = subtitles[end_idx]['end_seconds'] - subtitles[start_idx]['start_seconds']
                
                segments.append({
                    "segment_id": i + 1,
                    "title": f"精彩片段{i + 1}",
                    "start_time": subtitles[start_idx]['start'],
                    "end_time": subtitles[end_idx]['end'],
                    "duration_seconds": duration,
                    "segment_type": "核心剧情",
                    "selection_reason": f"基于关键词评分({score:.1f})选择",
                    "story_completeness": "包含完整对话和情节发展",
                    "key_dialogues": [
                        {"timestamp": center_sub['start'], "speaker": "角色", "line": center_sub['text'][:50], "significance": "核心对话"}
                    ],
                    "emotional_arc": "情感发展",
                    "visual_highlights": "精彩画面",
                    "audience_hook": "吸引观众的关键内容"
                })
        
        return segments

    def create_episode_clips(self, analysis: Dict, video_file: str, episode_name: str) -> List[str]:
        """为一集创建多个短视频"""
        created_clips = []
        
        episode_num = analysis['episode_analysis']['episode_number']
        segments = analysis['highlight_segments']
        
        print(f"\n🎬 开始剪辑第{episode_num}集")
        print(f"📁 源视频: {os.path.basename(video_file)}")
        print(f"📊 计划创建 {len(segments)} 个片段")
        
        for segment in segments:
            clip_file = self._create_single_clip(segment, video_file, episode_num, analysis)
            if clip_file:
                created_clips.append(clip_file)
                
                # 生成旁白文件
                self._generate_narration_file(segment, clip_file, analysis)
        
        print(f"✅ 第{episode_num}集完成，创建了 {len(created_clips)} 个短视频")
        return created_clips

    def _create_single_clip(self, segment: Dict, video_file: str, episode_num: str, analysis: Dict) -> Optional[str]:
        """创建单个短视频片段"""
        try:
            segment_id = segment['segment_id']
            title = segment['title']
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            output_name = f"E{episode_num}_{segment_id:02d}_{safe_title}.mp4"
            output_path = os.path.join(self.output_folder, output_name)
            
            print(f"  🎬 创建片段{segment_id}: {title}")
            print(f"  ⏱️ 时间: {start_time} --> {end_time}")
            print(f"  📏 时长: {segment['duration_seconds']:.1f}秒")
            
            # 转换时间为秒
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            # 添加缓冲时间确保完整性
            buffer_start = max(0, start_seconds - 1)
            buffer_duration = duration + 2
            
            # FFmpeg剪辑命令
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
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"    ✅ 创建成功: {output_name} ({file_size:.1f}MB)")
                
                # 添加专业标题
                self._add_title_overlay(output_path, segment, analysis)
                
                # 生成详细说明文件
                self._create_clip_description(output_path, segment, analysis, episode_num)
                
                return output_path
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"
                print(f"    ❌ 剪辑失败: {error_msg}")
                return None
                
        except Exception as e:
            print(f"❌ 创建片段出错: {e}")
            return None

    def _generate_narration_file(self, segment: Dict, clip_file: str, analysis: Dict):
        """生成旁白解说文件"""
        try:
            narration_path = clip_file.replace('.mp4', '_旁白.txt')
            
            # 基于AI分析生成专业旁白
            narration_data = analysis.get('narration_suggestions', {})
            
            # 构建旁白内容
            opening = f"接下来我们看到的是{segment['title']}。"
            
            process = f"{segment['selection_reason']}，"
            if segment.get('emotional_arc'):
                process += f"这个片段展现了{segment['emotional_arc']}。"
            
            highlight = f"最精彩的部分是{segment.get('audience_hook', '剧情高潮')}，"
            if segment.get('key_dialogues'):
                key_dialogue = segment['key_dialogues'][0]
                highlight += f"特别是这句话：'{key_dialogue['line']}'。"
            
            ending = f"这个片段{segment.get('story_completeness', '展现了完整的故事发展')}。"
            
            full_narration = f"{opening} {process} {highlight} {ending}"
            
            # 生成旁白文件
            content = f"""🎙️ 短视频旁白解说
{"=" * 50}

📺 片段信息:
• 标题: {segment['title']}
• 时长: {segment['duration_seconds']:.1f} 秒
• 类型: {segment['segment_type']}

🎯 旁白内容:

【开场白 (0-3秒)】
{opening}

【过程解说 (3-8秒)】
{process}

【亮点强调 (8-11秒)】
{highlight}

【结尾总结 (11-12秒)】
{ending}

【完整旁白】
{full_narration}

🎨 解说要点:
• 整体风格: {narration_data.get('overall_tone', '专业解说')}
• 情感引导: {narration_data.get('emotional_guidance', '引起观众共鸣')}
• 关键点: {', '.join(narration_data.get('key_points_to_explain', ['剧情发展']))}

📝 使用说明:
• 可配合AI语音合成工具生成音频
• 建议语速: 每分钟160-180字
• 语调: 根据片段情感调整
• 停顿: 在关键信息后适当停顿

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(narration_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    🎙️ 旁白文件: {os.path.basename(narration_path)}")
            
        except Exception as e:
            print(f"    ⚠️ 旁白生成失败: {e}")

    def find_matching_video(self, episode_name: str) -> Optional[str]:
        """智能匹配视频文件"""
        if not os.path.exists(self.video_folder):
            return None
        
        base_name = os.path.splitext(episode_name)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 提取集数模糊匹配
        episode_patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        episode_num = None
        
        for pattern in episode_patterns:
            match = re.search(pattern, base_name, re.I)
            if match:
                episode_num = match.group(1)
                break
        
        if episode_num:
            for filename in os.listdir(self.video_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    for pattern in episode_patterns:
                        match = re.search(pattern, filename, re.I)
                        if match and match.group(1).zfill(2) == episode_num.zfill(2):
                            return os.path.join(self.video_folder, filename)
        
        return None

    def process_all_episodes(self):
        """处理所有集数"""
        print("\n🚀 开始完整智能剪辑")
        print("=" * 60)
        
        # 获取字幕文件
        srt_files = []
        for filename in os.listdir(self.srt_folder):
            if filename.lower().endswith(('.srt', '.txt')) and not filename.startswith('.'):
                srt_files.append(filename)
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return
        
        srt_files.sort()
        print(f"📄 找到 {len(srt_files)} 个字幕文件")
        
        # 检查视频目录
        video_files = []
        if os.path.exists(self.video_folder):
            video_files = [f for f in os.listdir(self.video_folder) 
                          if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
        
        if not video_files:
            print(f"❌ {self.video_folder}/ 目录中未找到视频文件")
            return
        
        print(f"🎬 找到 {len(video_files)} 个视频文件")
        
        total_clips = 0
        all_episodes = []
        
        for srt_file in srt_files:
            try:
                print(f"\n📺 处理: {srt_file}")
                
                # 解析字幕
                srt_path = os.path.join(self.srt_folder, srt_file)
                subtitles = self.parse_subtitle_file(srt_path)
                
                if not subtitles:
                    print(f"❌ 字幕解析失败")
                    continue
                
                # AI分析
                analysis = self.ai_analyze_episode(subtitles, srt_file)
                
                if not analysis:
                    print(f"❌ 分析失败")
                    continue
                
                # 寻找对应视频
                video_file = self.find_matching_video(srt_file)
                
                if not video_file:
                    print(f"⚠️ 未找到对应视频文件")
                    continue
                
                # 创建多个短视频
                episode_clips = self.create_episode_clips(analysis, video_file, srt_file)
                
                if episode_clips:
                    total_clips += len(episode_clips)
                    all_episodes.append({
                        'file': srt_file,
                        'analysis': analysis,
                        'clips': episode_clips
                    })
                    print(f"✅ {srt_file} 处理完成，创建 {len(episode_clips)} 个短视频")
                else:
                    print(f"❌ {srt_file} 剪辑失败")
                    
            except Exception as e:
                print(f"❌ 处理 {srt_file} 时出错: {e}")
        
        # 生成完整报告
        self._generate_final_report(all_episodes, total_clips, len(srt_files))

    # 辅助方法
    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.ai_config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.ai_config.get('model', 'gpt-3.5-turbo'),
                'messages': [
                    {'role': 'system', 'content': '你是专业的电视剧剧情分析师，擅长识别精彩片段。请严格按照JSON格式返回分析结果。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 3000,
                'temperature': 0.7
            }
            
            base_url = self.ai_config.get('base_url', 'https://api.openai.com/v1')
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                return content
            else:
                print(f"API调用失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API调用异常: {e}")
            return None

    def _parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
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
            print(f"JSON解析错误: {e}")
            return None

    def _validate_analysis(self, analysis: Dict, subtitles: List[Dict]) -> bool:
        """验证分析结果"""
        try:
            if 'highlight_segments' not in analysis:
                return False
            
            segments = analysis['highlight_segments']
            if not segments:
                return False
            
            # 验证每个片段
            subtitle_start = min(sub['start_seconds'] for sub in subtitles)
            subtitle_end = max(sub['end_seconds'] for sub in subtitles)
            
            for segment in segments:
                if not all(key in segment for key in ['start_time', 'end_time', 'title']):
                    return False
                
                start_seconds = self._time_to_seconds(segment['start_time'])
                end_seconds = self._time_to_seconds(segment['end_time'])
                
                if start_seconds >= end_seconds:
                    return False
                
                # 修正超出范围的时间
                if start_seconds < subtitle_start or end_seconds > subtitle_end:
                    closest_start = min(subtitles, key=lambda s: abs(s['start_seconds'] - start_seconds))
                    closest_end = min(subtitles, key=lambda s: abs(s['end_seconds'] - end_seconds))
                    
                    segment['start_time'] = closest_start['start']
                    segment['end_time'] = closest_end['end']
                    segment['duration_seconds'] = closest_end['end_seconds'] - closest_start['start_seconds']
            
            return True
            
        except Exception as e:
            print(f"验证分析结果出错: {e}")
            return False

    def _time_to_seconds(self, time_str: str) -> float:
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

    def _extract_episode_number(self, filename: str) -> str:
        """提取集数"""
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)', r'(\d+)']
        for pattern in patterns:
            match = re.search(pattern, filename, re.I)
            if match:
                return match.group(1).zfill(2)
        return "01"

    def _build_full_script(self, subtitles: List[Dict]) -> str:
        """构建完整剧情文本"""
        scenes = []
        current_scene = []
        last_time = 0
        
        for subtitle in subtitles:
            if subtitle['start_seconds'] - last_time > 30 and current_scene:
                scene_text = '\n'.join([sub['text'] for sub in current_scene])
                scenes.append(f"[{current_scene[0]['start']} - {current_scene[-1]['end']}]\n{scene_text}")
                current_scene = []
            
            current_scene.append(subtitle)
            last_time = subtitle['end_seconds']
        
        if current_scene:
            scene_text = '\n'.join([sub['text'] for sub in current_scene])
            scenes.append(f"[{current_scene[0]['start']} - {current_scene[-1]['end']}]\n{scene_text}")
        
        return '\n\n=== 场景分割 ===\n\n'.join(scenes)

    def _build_context(self, current_episode: str) -> str:
        """构建上下文信息"""
        if not self.series_context:
            return "这是剧集分析的开始，暂无前集上下文。"
        
        context_parts = []
        context_parts.append("【前集剧情回顾】")
        
        for prev_ep in self.series_context[-2:]:  # 最近2集
            context_parts.append(f"• {prev_ep['episode']}: {prev_ep.get('main_theme', '未知')}")
        
        return '\n'.join(context_parts)

    def _update_series_context(self, analysis: Dict, episode_name: str):
        """更新剧集上下文"""
        episode_summary = {
            'episode': episode_name,
            'main_theme': analysis.get('episode_analysis', {}).get('main_theme', ''),
            'key_characters': analysis.get('episode_analysis', {}).get('key_characters', [])
        }
        
        self.series_context.append(episode_summary)
        
        # 只保留最近3集的上下文
        if len(self.series_context) > 3:
            self.series_context = self.series_context[-3:]

    def _get_cache_path(self, episode_name: str, subtitles: List[Dict]) -> str:
        """获取缓存路径"""
        content_hash = hashlib.md5(str(subtitles).encode()).hexdigest()[:16]
        safe_name = re.sub(r'[^\w\-_]', '_', episode_name)
        return os.path.join(self.cache_folder, f"{safe_name}_{content_hash}.json")

    def _load_cache(self, cache_path: str) -> Optional[Dict]:
        """加载缓存"""
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def _save_cache(self, cache_path: str, analysis: Dict):
        """保存缓存"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def _add_title_overlay(self, video_path: str, segment: Dict, analysis: Dict):
        """添加标题叠层"""
        try:
            temp_path = video_path.replace('.mp4', '_temp.mp4')
            
            title = segment['title']
            segment_type = segment.get('segment_type', '')
            
            # 清理文本
            clean_title = title.replace("'", "").replace('"', '')[:40]
            clean_type = segment_type.replace("'", "").replace('"', '')[:20]
            
            # 添加标题滤镜
            filter_text = (
                f"drawtext=text='{clean_title}':fontsize=24:fontcolor=white:"
                f"x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.7:boxborderw=5:"
                f"enable='between(t,0,3)',"
                f"drawtext=text='{clean_type}':fontsize=18:fontcolor=yellow:"
                f"x=(w-text_w)/2:y=90:box=1:boxcolor=black@0.6:boxborderw=4:"
                f"enable='between(t,1,3)'"
            )
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_text,
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'fast',
                temp_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                os.replace(temp_path, video_path)
                print(f"    ✓ 添加标题完成")
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
        except Exception as e:
            print(f"    ⚠ 添加标题失败: {e}")

    def _create_clip_description(self, video_path: str, segment: Dict, analysis: Dict, episode_num: str):
        """创建片段说明文件"""
        try:
            desc_path = video_path.replace('.mp4', '_说明.txt')
            
            content = f"""📺 {segment['title']}
{"=" * 60}

📊 基本信息:
• 集数: 第{episode_num}集
• 片段: {segment['segment_id']}/{len(analysis['highlight_segments'])}
• 时间: {segment['start_time']} --> {segment['end_time']}
• 时长: {segment['duration_seconds']:.1f} 秒
• 类型: {segment['segment_type']}

🎯 选择理由:
{segment['selection_reason']}

📝 故事完整性:
{segment['story_completeness']}

💫 情感弧线:
{segment.get('emotional_arc', '情感发展轨迹')}

🎬 视觉亮点:
{segment.get('visual_highlights', '精彩画面')}

🎯 观众吸引点:
{segment.get('audience_hook', '核心吸引内容')}

🗣️ 重要对话:
"""
            
            for dialogue in segment.get('key_dialogues', []):
                content += f"[{dialogue['timestamp']}] {dialogue['speaker']}: {dialogue['line']}\n"
                content += f"重要性: {dialogue['significance']}\n\n"
            
            content += f"""
🔗 剧集连贯性:
• 前集联系: {analysis.get('episode_continuity', {}).get('previous_connection', '自然延续')}
• 下集铺垫: {analysis.get('episode_continuity', {}).get('next_episode_setup', '剧情发展')}

📱 短视频优化建议:
• 适合平台: 抖音、快手、B站等
• 观看体验: 独立完整，无需前置知识
• 传播价值: 高质量剧情内容，易引起共鸣

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 说明文件: {os.path.basename(desc_path)}")
            
        except Exception as e:
            print(f"    ⚠️ 说明文件生成失败: {e}")

    def _generate_final_report(self, all_episodes: List[Dict], total_clips: int, total_episodes: int):
        """生成最终报告"""
        if not all_episodes:
            return
        
        report_path = os.path.join(self.output_folder, "完整剪辑报告.txt")
        
        content = f"""🤖 完整AI智能剪辑报告
{"=" * 80}

📊 整体统计:
• 处理集数: {len(all_episodes)}/{total_episodes} 集
• 成功率: {(len(all_episodes)/total_episodes*100):.1f}%
• 创建短视频: {total_clips} 个
• AI分析: {'启用' if self.ai_config.get('enabled') else '基础规则'}

📺 每集详情:
"""
        
        total_duration = 0
        
        for i, episode in enumerate(all_episodes, 1):
            analysis = episode['analysis']
            clips = episode['clips']
            
            episode_num = analysis['episode_analysis']['episode_number']
            drama_genre = analysis['episode_analysis'].get('drama_genre', '通用剧情')
            segments = analysis['highlight_segments']
            
            episode_duration = sum(seg['duration_seconds'] for seg in segments)
            total_duration += episode_duration
            
            content += f"""
{i}. 第{episode_num}集 - {drama_genre}
   原文件: {episode['file']}
   片段数: {len(segments)} 个
   总时长: {episode_duration:.1f} 秒 ({episode_duration/60:.1f} 分钟)
   视频文件: {len(clips)} 个
   
   片段详情:
"""
            for seg in segments:
                content += f"   • {seg['title']} ({seg['duration_seconds']:.1f}s) - {seg['segment_type']}\n"
        
        avg_clips_per_episode = total_clips / len(all_episodes) if all_episodes else 0
        avg_duration = total_duration / total_clips if total_clips else 0
        
        content += f"""
📈 质量分析:
• 平均每集片段数: {avg_clips_per_episode:.1f} 个
• 平均片段时长: {avg_duration:.1f} 秒 ({avg_duration/60:.1f} 分钟)
• 总剪辑时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)

📁 输出文件结构:
{self.output_folder}/
├── E01_01_片段标题.mp4          # 视频文件
├── E01_01_片段标题_说明.txt      # 详细说明
├── E01_01_片段标题_旁白.txt      # 旁白解说
└── ...

💡 使用建议:
• 所有短视频都有独立的旁白解说文件
• 说明文件包含详细的剧情分析和制作信息
• 建议按集数顺序发布，保持剧情连贯性
• 可根据平台特点选择合适的片段类型发布

🎯 成功特点:
• ✅ 每集多个精彩短视频，AI智能判断内容
• ✅ 实际剪辑生成完整视频文件
• ✅ 规范的videos/和srt/目录结构
• ✅ 专业旁白解说文件
• ✅ 跨集剧情连贯性保证

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本: 完整AI智能剪辑系统 v2.0
"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📄 完整剪辑报告已保存: {report_path}")
        except Exception as e:
            print(f"⚠️ 报告保存失败: {e}")


def main():
    """主函数"""
    clipper = CompleteAIClipper()
    
    print("\n请选择操作:")
    print("1. 🚀 开始完整智能剪辑")
    print("2. ⚙️ 配置AI设置")
    print("3. 📁 检查文件状态")
    print("4. ❌ 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == '1':
                clipper.process_all_episodes()
                break
            elif choice == '2':
                configure_ai()
            elif choice == '3':
                check_file_status(clipper)
            elif choice == '4':
                print("👋 感谢使用！")
                break
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断")
            break
        except Exception as e:
            print(f"❌ 操作错误: {e}")


def configure_ai():
    """配置AI设置"""
    print("\n⚙️ AI配置设置")
    print("=" * 40)
    
    config = {
        'enabled': True,
        'base_url': input("API地址 (默认: https://api.openai.com/v1): ").strip() or "https://api.openai.com/v1",
        'api_key': input("API密钥: ").strip(),
        'model': input("模型名称 (默认: gpt-3.5-turbo): ").strip() or "gpt-3.5-turbo"
    }
    
    if config['api_key']:
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ AI配置保存成功")
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    else:
        print("❌ API密钥不能为空")


def check_file_status(clipper):
    """检查文件状态"""
    print("\n📁 文件状态检查")
    print("=" * 40)
    
    # 检查字幕文件
    srt_count = 0
    if os.path.exists(clipper.srt_folder):
        srt_files = [f for f in os.listdir(clipper.srt_folder) 
                    if f.lower().endswith(('.srt', '.txt'))]
        srt_count = len(srt_files)
        print(f"📄 字幕文件: {srt_count} 个")
        for f in srt_files[:3]:
            print(f"  • {f}")
        if srt_count > 3:
            print(f"  ... 等共 {srt_count} 个")
    else:
        print(f"❌ 字幕目录不存在: {clipper.srt_folder}/")
    
    # 检查视频文件
    video_count = 0
    if os.path.exists(clipper.video_folder):
        video_files = [f for f in os.listdir(clipper.video_folder) 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
        video_count = len(video_files)
        print(f"🎬 视频文件: {video_count} 个")
        for f in video_files[:3]:
            print(f"  • {f}")
        if video_count > 3:
            print(f"  ... 等共 {video_count} 个")
    else:
        print(f"❌ 视频目录不存在: {clipper.video_folder}/")
    
    print(f"\n状态总结:")
    print(f"• 准备就绪: {'✅' if srt_count > 0 and video_count > 0 else '❌'}")
    print(f"• AI配置: {'✅' if os.path.exists('.ai_config.json') else '❌'}")


if __name__ == "__main__":
    main()

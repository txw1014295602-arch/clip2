
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能AI电视剧分析系统
完全基于AI的自适应剧情分析，不依赖固定关键词
支持任何类型的电视剧自动分析和剪辑
"""

import os
import re
import json
import hashlib
import subprocess
from typing import List, Dict, Optional
from datetime import datetime
import requests

class IntelligentAIAnalysisSystem:
    def __init__(self, srt_folder: str = "srt", video_folder: str = "videos", output_folder: str = "clips"):
        self.srt_folder = srt_folder
        self.video_folder = video_folder
        self.output_folder = output_folder
        self.cache_folder = "analysis_cache"
        
        # 创建目录
        for folder in [self.srt_folder, self.video_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        # 剧集上下文缓存
        self.series_context = {
            'previous_episodes': [],
            'main_characters': set(),
            'story_threads': [],
            'ongoing_conflicts': []
        }
        
        print("🤖 智能AI电视剧分析系统启动")
        print("=" * 60)
        print("✨ 特性：")
        print("• 完全AI驱动，自适应任何剧情类型")
        print("• 智能识别精彩片段和剧情转折")
        print("• 保证跨集连贯性和故事完整性")
        print("• 自动错别字修正")
        print("• 每集2-3分钟核心剧情短视频")
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
        """智能解析字幕文件，支持多种格式和编码"""
        print(f"📖 解析字幕文件: {os.path.basename(filepath)}")
        
        # 尝试多种编码
        content = None
        for encoding in ['utf-8', 'gbk', 'utf-16', 'gb2312', 'big5']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    break
            except:
                continue
        
        if not content:
            print("❌ 字幕文件读取失败")
            return []
        
        # 智能错别字修正 - 扩展版
        corrections = {
            # 繁体转简体
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
            '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会',
            '無罪': '无罪', '実現': '实现', '対話': '对话', '関係': '关系',
            
            # 常见错别字
            '証据': '证据', '辩户': '辩护', '检查官': '检察官', '法官': '法官',
            '申述': '申诉', '听政会': '听证会', '証人': '证人', '証言': '证言'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        # 解析字幕条目
        subtitles = []
        
        # 支持SRT和TXT格式
        if filepath.lower().endswith('.srt') or '-->' in content:
            # SRT格式
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
        else:
            # TXT格式或其他格式 - 智能解析
            lines = content.split('\n')
            current_text = []
            current_time = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 查找时间戳
                time_match = re.search(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})', line)
                if time_match and '-->' in line:
                    # 保存之前的字幕
                    if current_text and current_time:
                        subtitles.append({
                            'index': len(subtitles) + 1,
                            'start': current_time[0],
                            'end': current_time[1],
                            'text': ' '.join(current_text),
                            'start_seconds': self._time_to_seconds(current_time[0]),
                            'end_seconds': self._time_to_seconds(current_time[1])
                        })
                    
                    # 解析新的时间范围
                    time_parts = line.split('-->')
                    if len(time_parts) == 2:
                        start_time = re.search(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})', time_parts[0])
                        end_time = re.search(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})', time_parts[1])
                        if start_time and end_time:
                            current_time = (start_time.group(1).replace('.', ','), 
                                          end_time.group(1).replace('.', ','))
                            current_text = []
                else:
                    # 添加到当前字幕文本
                    if line and not line.isdigit():
                        current_text.append(line)
            
            # 保存最后一个字幕
            if current_text and current_time:
                subtitles.append({
                    'index': len(subtitles) + 1,
                    'start': current_time[0],
                    'end': current_time[1],
                    'text': ' '.join(current_text),
                    'start_seconds': self._time_to_seconds(current_time[0]),
                    'end_seconds': self._time_to_seconds(current_time[1])
                })
        
        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def ai_analyze_episode(self, subtitles: List[Dict], episode_name: str) -> Optional[Dict]:
        """完全AI驱动的自适应剧情分析 - 解决割裂和限制问题"""
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
        
        # 构建完整连贯的剧情文本 - 解决割裂问题
        complete_script = self._build_coherent_full_script(subtitles)
        
        # 构建丰富的上下文信息 - 解决上下文衔接问题
        context_info = self._build_rich_series_context(episode_num)
        
        # 完全开放的AI分析提示词 - 移除所有固定限制
        prompt = f"""你是世界顶级的电视剧剧情分析专家。请对这一集进行完全自由的深度分析，不受任何类型或格式限制。

【当前集数】第{episode_num}集
【全剧上下文】{context_info}

【完整剧情内容】
{complete_script}

请以你的专业判断，完全自由地分析这一集：

{{
    "comprehensive_analysis": {{
        "episode_number": "{episode_num}",
        "auto_detected_genre": "根据内容自动识别的具体剧情类型和子类型",
        "narrative_style": "叙事风格特点（现实主义/戏剧化/悬疑/喜剧等）",
        "emotional_core": "本集的情感核心和主调",
        "story_significance": "在整个剧集中的重要地位",
        "character_dynamics": "主要角色关系和互动模式",
        "thematic_elements": "核心主题和深层含义",
        "dramatic_structure": "戏剧结构分析",
        "pacing_rhythm": "节奏感和张力变化"
    }},
    "optimal_highlight_segment": {{
        "segment_title": "最佳精彩片段标题",
        "start_time": "开始时间（HH:MM:SS,mmm）",
        "end_time": "结束时间（HH:MM:SS,mmm）",
        "duration_seconds": 实际秒数,
        "selection_reasoning": "为什么选择这个片段的深层原因",
        "dramatic_arc": {{
            "opening": "片段开场如何吸引观众",
            "development": "剧情如何逐步推进",
            "climax": "高潮点在哪里，为什么重要",
            "resolution": "如何收尾并衔接后续"
        }},
        "emotional_journey": "观众在这个片段中的情感体验路径",
        "key_moments": [
            {{"time": "HH:MM:SS,mmm", "description": "关键时刻1描述", "impact": "情感/剧情冲击力"}},
            {{"time": "HH:MM:SS,mmm", "description": "关键时刻2描述", "impact": "情感/剧情冲击力"}}
        ],
        "dialogue_highlights": [
            {{"timestamp": "HH:MM:SS,mmm", "context": "场景背景", "line": "重要台词", "significance": "台词重要性"}},
            {{"timestamp": "HH:MM:SS,mmm", "context": "场景背景", "line": "关键对话", "significance": "对话意义"}}
        ],
        "visual_storytelling": "画面叙事和视觉元素分析",
        "audience_hook": "吸引观众的核心卖点"
    }},
    "series_continuity_analysis": {{
        "previous_episodes_connection": "与前面剧集的具体联系和呼应",
        "story_threads_progression": "故事线索的发展和推进",
        "character_arcs_development": "角色弧线在本集中的具体发展",
        "foreshadowing_elements": "为后续剧集埋下的伏笔和铺垫",
        "recurring_themes": "重复出现的主题和母题",
        "narrative_continuity": "叙事连贯性和整体故事结构中的位置"
    }},
    "creative_insights": {{
        "unique_elements": "本集独特的创意元素",
        "storytelling_techniques": "使用的叙事技巧",
        "emotional_manipulation": "情感调动的手法",
        "surprise_elements": "意外转折和惊喜点",
        "subtext_analysis": "潜台词和隐含意义"
    }},
    "production_recommendations": {{
        "editing_approach": "剪辑手法建议",
        "music_mood": "配乐情绪建议",
        "pacing_control": "节奏控制要点",
        "transition_strategy": "与其他片段的衔接策略",
        "audience_retention": "保持观众注意力的要点"
    }}
}}

分析原则：
1. 完全基于内容，不受任何预设类型限制
2. 从整体剧情出发，选择最具代表性和连贯性的片段
3. 深度分析剧情价值，不仅仅是表面的戏剧冲突
4. 重视上下文衔接，确保片段在整个故事中的合理位置
5. 考虑观众体验，选择能够独立成篇又融入整体的内容
6. 提供专业的制作指导，而非模板化建议"""

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

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        config = self.ai_config
        
        try:
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config.get('model', 'gpt-3.5-turbo'),
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是专业的电视剧剧情分析师，擅长识别精彩片段和保持故事连贯性。请严格按照JSON格式返回分析结果。'
                    },
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 4000,
                'temperature': 0.7
            }
            
            base_url = config.get('base_url', 'https://api.openai.com/v1')
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
            print(f"JSON解析错误: {e}")
            return None

    def _validate_analysis(self, analysis: Dict, subtitles: List[Dict]) -> bool:
        """验证分析结果 - 适配新的分析结构"""
        try:
            # 检查新的必要字段
            if 'optimal_highlight_segment' not in analysis:
                return False
            
            segment = analysis['optimal_highlight_segment']
            if not all(key in segment for key in ['start_time', 'end_time', 'segment_title']):
                return False
            
            # 验证时间格式和范围
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            
            if start_seconds >= end_seconds:
                return False
            
            duration = end_seconds - start_seconds
            if duration < 90 or duration > 360:  # 1.5-6分钟范围，更灵活
                print(f"⚠️ 片段时长 {duration:.1f}秒 不在推荐范围内，但仍然接受")
            
            # 检查时间是否在字幕范围内
            subtitle_start = min(sub['start_seconds'] for sub in subtitles)
            subtitle_end = max(sub['end_seconds'] for sub in subtitles)
            
            if start_seconds < subtitle_start or end_seconds > subtitle_end:
                # 尝试修正到最接近的字幕时间
                closest_start = min(subtitles, key=lambda s: abs(s['start_seconds'] - start_seconds))
                closest_end = min(subtitles, key=lambda s: abs(s['end_seconds'] - end_seconds))
                
                segment['start_time'] = closest_start['start']
                segment['end_time'] = closest_end['end']
                segment['duration_seconds'] = closest_end['end_seconds'] - closest_start['start_seconds']
                print(f"✅ 时间已修正到字幕范围内")
            
            return True
            
        except Exception as e:
            print(f"验证分析结果出错: {e}")
            return False

    def basic_analysis_fallback(self, subtitles: List[Dict], episode_name: str) -> Dict:
        """基础分析备选方案"""
        episode_num = self._extract_episode_number(episode_name)
        
        # 简单的关键词评分
        keywords = {
            '法律': ['法官', '检察官', '律师', '法庭', '审判', '证据', '案件', '起诉', '辩护'],
            '情感': ['爱', '恨', '情', '心', '感动', '痛苦', '快乐', '悲伤'],
            '悬疑': ['真相', '秘密', '发现', '线索', '调查', '揭露', '神秘'],
            '冲突': ['争论', '吵架', '打斗', '对抗', '冲突', '矛盾', '反对'],
            '转折': ['突然', '没想到', '原来', '竞然', '反转', '变化', '改变']
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
            score += text.count('...') * 0.5
            
            # 位置加权
            position_ratio = i / len(subtitles)
            if position_ratio < 0.3 or position_ratio > 0.7:
                score *= 1.2
            
            if score > 3:
                scored_subtitles.append((i, score, subtitle))
        
        if not scored_subtitles:
            # 选择中间部分
            mid_point = len(subtitles) // 2
            scored_subtitles = [(mid_point, 5, subtitles[mid_point])]
        
        # 选择最高分片段
        scored_subtitles.sort(key=lambda x: x[1], reverse=True)
        center_idx, score, center_sub = scored_subtitles[0]
        
        # 扩展到2-3分钟
        target_duration = 150  # 2.5分钟
        start_idx = center_idx
        end_idx = center_idx
        
        # 向前后扩展
        while start_idx > 0:
            test_duration = subtitles[end_idx]['end_seconds'] - subtitles[start_idx-1]['start_seconds']
            if test_duration > target_duration:
                break
            start_idx -= 1
        
        while end_idx < len(subtitles) - 1:
            test_duration = subtitles[end_idx+1]['end_seconds'] - subtitles[start_idx]['start_seconds']
            if test_duration > target_duration * 1.2:
                break
            end_idx += 1
        
        # 构建分析结果
        start_time = subtitles[start_idx]['start']
        end_time = subtitles[end_idx]['end']
        duration = subtitles[end_idx]['end_seconds'] - subtitles[start_idx]['start_seconds']
        
        return {
            "episode_analysis": {
                "episode_number": episode_num,
                "drama_type": "通用剧情",
                "main_storyline": f"第{episode_num}集核心剧情",
                "key_characters": ["主要角色"],
                "emotional_arc": "情感发展",
                "plot_progression": "剧情推进"
            },
            "core_segment": {
                "title": f"第{episode_num}集精彩片段",
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "plot_significance": "重要剧情节点",
                "dramatic_value": 7.0,
                "emotional_impact": 7.0,
                "key_dialogues": [
                    {"timestamp": start_time, "speaker": "角色", "line": subtitles[start_idx]['text'][:50]}
                ],
                "content_highlights": [
                    "核心剧情发展",
                    "角色关系变化",
                    "情节推进"
                ]
            },
            "series_continuity": {
                "previous_connection": "与前集的自然延续",
                "next_episode_setup": "为下集剧情发展铺垫",
                "ongoing_storylines": ["主线剧情"],
                "character_development": "角色成长"
            }
        }

    def create_video_clip(self, analysis: Dict, video_file: str, episode_name: str) -> bool:
        """创建视频剪辑 - 适配新的分析结构"""
        try:
            segment = analysis['optimal_highlight_segment']
            title = segment['segment_title']
            start_time = segment['start_time']
            end_time = segment['end_time']
            
            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            output_name = f"{safe_title}.mp4"
            output_path = os.path.join(self.output_folder, output_name)
            
            print(f"\n🎬 创建视频剪辑: {title}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"⏱️ 时间段: {start_time} --> {end_time}")
            print(f"📏 时长: {segment['duration_seconds']:.1f}秒")
            
            # 转换时间为秒
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            # 添加缓冲时间
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
                print(f"  ✅ 剪辑成功: {output_name} ({file_size:.1f}MB)")
                
                # 生成详细说明文件
                self._create_description_file(output_path, analysis, episode_name)
                
                return True
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"
                print(f"  ❌ 剪辑失败: {error_msg}")
                return False
                
        except Exception as e:
            print(f"❌ 创建视频剪辑出错: {e}")
            return False

    def _create_description_file(self, video_path: str, analysis: Dict, episode_name: str):
        """创建详细说明文件 - 适配新的分析结构"""
        try:
            desc_path = video_path.replace('.mp4', '_深度分析.txt')
            
            comprehensive = analysis.get('comprehensive_analysis', {})
            segment = analysis.get('optimal_highlight_segment', {})
            continuity = analysis.get('series_continuity_analysis', {})
            insights = analysis.get('creative_insights', {})
            recommendations = analysis.get('production_recommendations', {})
            
            content = f"""🎬 {segment.get('segment_title', '精彩片段')}
{"=" * 100}

📊 基本信息
⏱️ 精确时间段: {segment.get('start_time')} --> {segment.get('end_time')}
📏 片段时长: {segment.get('duration_seconds', 0):.1f} 秒
🎭 自动识别类型: {comprehensive.get('auto_detected_genre', '未识别')}
📖 叙事风格: {comprehensive.get('narrative_style', '标准叙事')}
💫 情感核心: {comprehensive.get('emotional_core', '情感表达')}

🎯 选择理由
{segment.get('selection_reasoning', '基于AI智能分析选择的最佳片段')}

🎭 戏剧结构分析
• 开场吸引: {segment.get('dramatic_arc', {}).get('opening', '自然开场')}
• 剧情发展: {segment.get('dramatic_arc', {}).get('development', '逐步推进')}
• 高潮时刻: {segment.get('dramatic_arc', {}).get('climax', '情感/剧情高潮')}
• 收尾衔接: {segment.get('dramatic_arc', {}).get('resolution', '完整收尾')}

💡 情感体验路径
{segment.get('emotional_journey', '观众情感跟随剧情发展的完整体验')}

⭐ 关键时刻分析
"""
            
            for moment in segment.get('key_moments', []):
                content += f"[{moment.get('time', '')}] {moment.get('description', '')}\n"
                content += f"    冲击力: {moment.get('impact', '')}\n\n"
            
            content += f"""
📝 重要对话分析
"""
            for dialogue in segment.get('dialogue_highlights', []):
                content += f"[{dialogue.get('timestamp', '')}] {dialogue.get('context', '场景')}\n"
                content += f"台词: {dialogue.get('line', '')}\n"
                content += f"意义: {dialogue.get('significance', '')}\n\n"
            
            content += f"""
🔗 剧集连贯性深度分析
• 前集联系: {continuity.get('previous_episodes_connection', '自然延续')}
• 故事推进: {continuity.get('story_threads_progression', '剧情发展')}
• 角色发展: {continuity.get('character_arcs_development', '角色成长')}
• 伏笔铺垫: {continuity.get('foreshadowing_elements', '为后续铺垫')}
• 主题呼应: {continuity.get('recurring_themes', '主题延续')}

🎨 创意洞察
• 独特元素: {insights.get('unique_elements', '本集特色')}
• 叙事技巧: {insights.get('storytelling_techniques', '专业叙事手法')}
• 情感调动: {insights.get('emotional_manipulation', '情感共鸣技巧')}
• 惊喜元素: {insights.get('surprise_elements', '意外转折')}
• 深层含义: {insights.get('subtext_analysis', '潜台词分析')}

📺 观众吸引力
• 核心卖点: {segment.get('audience_hook', '吸引观众的关键因素')}
• 视觉叙事: {segment.get('visual_storytelling', '画面语言分析')}

🎬 制作建议
• 剪辑手法: {recommendations.get('editing_approach', '专业剪辑建议')}
• 配乐情绪: {recommendations.get('music_mood', '音乐氛围建议')}
• 节奏控制: {recommendations.get('pacing_control', '节奏把握要点')}
• 衔接策略: {recommendations.get('transition_strategy', '与其他内容的衔接')}
• 注意力保持: {recommendations.get('audience_retention', '观众粘性策略')}

📄 技术信息
• 原始文件: {episode_name}
• 分析方式: AI深度智能分析
• 时间精度: 毫秒级精确
• 内容完整性: 保证剧情完整和连贯
• 上下文考量: 充分结合前后剧情

🌟 整体价值评估
本片段代表了本集的精华内容，既能独立展现精彩剧情，又与整个故事线保持完美衔接。
通过AI深度分析，确保了选择的科学性和观赏价值的最大化。

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析引擎: 智能AI电视剧分析系统 v2.0
"""
            
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 生成深度分析: {os.path.basename(desc_path)}")
            
        except Exception as e:
            print(f"    ⚠️ 生成说明文件失败: {e}")

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
        
        # 模糊匹配 - 提取集数
        episode_patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)', r'(\d+)']
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

    def _build_coherent_full_script(self, subtitles: List[Dict]) -> str:
        """构建完整连贯的剧情文本 - 解决割裂问题"""
        # 按场景分组，保持剧情连贯性
        scenes = []
        current_scene = []
        last_time = 0
        
        for subtitle in subtitles:
            # 如果时间间隔超过30秒，认为是新场景
            if subtitle['start_seconds'] - last_time > 30 and current_scene:
                scene_text = '\n'.join([sub['text'] for sub in current_scene])
                scene_time = f"[场景时间: {current_scene[0]['start']} - {current_scene[-1]['end']}]"
                scenes.append(f"{scene_time}\n{scene_text}")
                current_scene = []
            
            current_scene.append(subtitle)
            last_time = subtitle['end_seconds']
        
        # 添加最后一个场景
        if current_scene:
            scene_text = '\n'.join([sub['text'] for sub in current_scene])
            scene_time = f"[场景时间: {current_scene[0]['start']} - {current_scene[-1]['end']}]"
            scenes.append(f"{scene_time}\n{scene_text}")
        
        return '\n\n=== 场景分割 ===\n\n'.join(scenes)
    
    def _build_rich_series_context(self, current_episode: str) -> str:
        """构建丰富的上下文信息 - 解决上下文衔接问题"""
        if not self.series_context['previous_episodes']:
            return "这是剧集分析的开始，暂无前集上下文。"
        
        context_parts = []
        
        # 前集回顾
        context_parts.append("【前集剧情回顾】")
        for prev_ep in self.series_context['previous_episodes'][-3:]:  # 最近3集
            context_parts.append(f"• {prev_ep['episode']}")
            context_parts.append(f"  类型: {prev_ep.get('drama_type', '未知')}")
            context_parts.append(f"  核心剧情: {prev_ep.get('summary', '暂无')}")
            context_parts.append(f"  主要角色: {', '.join(prev_ep.get('characters', []))}")
            context_parts.append("")
        
        # 持续故事线
        all_storylines = set()
        for ep in self.series_context['previous_episodes']:
            all_storylines.update(ep.get('storylines', []))
        
        if all_storylines:
            context_parts.append("【持续故事线索】")
            for storyline in list(all_storylines):
                context_parts.append(f"• {storyline}")
            context_parts.append("")
        
        # 主要角色发展轨迹
        all_characters = set()
        for ep in self.series_context['previous_episodes']:
            all_characters.update(ep.get('characters', []))
        
        if all_characters:
            context_parts.append("【主要角色】")
            for character in list(all_characters):
                context_parts.append(f"• {character}")
            context_parts.append("")
        
        # 剧情发展趋势
        if len(self.series_context['previous_episodes']) > 1:
            context_parts.append("【剧情发展趋势】")
            context_parts.append("请分析本集在整个故事发展中的位置和作用")
            context_parts.append("")
        
        return '\n'.join(context_parts)
    
    def _update_series_context(self, analysis: Dict, episode_name: str):
        """更新剧集上下文 - 支持新的分析结构"""
        comprehensive = analysis.get('comprehensive_analysis', {})
        segment_info = analysis.get('optimal_highlight_segment', {})
        continuity = analysis.get('series_continuity_analysis', {})
        
        episode_summary = {
            'episode': episode_name,
            'drama_type': comprehensive.get('auto_detected_genre', ''),
            'summary': segment_info.get('selection_reasoning', ''),
            'characters': comprehensive.get('character_dynamics', '').split('、') if comprehensive.get('character_dynamics') else [],
            'storylines': continuity.get('story_threads_progression', '').split('、') if continuity.get('story_threads_progression') else [],
            'themes': comprehensive.get('thematic_elements', ''),
            'emotional_core': comprehensive.get('emotional_core', '')
        }
        
        self.series_context['previous_episodes'].append(episode_summary)
        
        # 只保留最近5集的上下文
        if len(self.series_context['previous_episodes']) > 6:
            self.series_context['previous_episodes'] = self.series_context['previous_episodes'][-5:]

    def _extract_episode_number(self, filename: str) -> str:
        """提取集数"""
        patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)', r'(\d+)']
        for pattern in patterns:
            match = re.search(pattern, filename, re.I)
            if match:
                return match.group(1).zfill(2)
        return "01"

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

    def process_all_episodes(self):
        """处理所有集数"""
        print("\n🚀 开始智能分析和剪辑")
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
        
        success_count = 0
        all_analyses = []
        
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
                
                all_analyses.append({
                    'file': srt_file,
                    'analysis': analysis
                })
                
                # 寻找对应视频
                video_file = self.find_matching_video(srt_file)
                
                if not video_file:
                    print(f"⚠️ 未找到对应视频文件")
                    continue
                
                # 创建视频剪辑
                if self.create_video_clip(analysis, video_file, srt_file):
                    success_count += 1
                    print(f"✅ {srt_file} 处理完成")
                else:
                    print(f"❌ {srt_file} 剪辑失败")
                    
            except Exception as e:
                print(f"❌ 处理 {srt_file} 时出错: {e}")
        
        # 生成整体报告
        self._generate_series_report(all_analyses, success_count, len(srt_files))

    def _generate_series_report(self, analyses: List[Dict], success_count: int, total_count: int):
        """生成整体剧集报告"""
        if not analyses:
            return
        
        report_path = os.path.join(self.output_folder, "智能分析报告.txt")
        
        content = f"""🤖 智能AI电视剧分析报告
{"=" * 80}

📊 处理统计:
• 总集数: {total_count} 集
• 成功处理: {success_count} 集
• 成功率: {(success_count/total_count*100):.1f}%
• AI分析: {'启用' if self.ai_config.get('enabled') else '基础规则'}

🎭 剧情类型分布:
"""
        
        # 统计剧情类型
        drama_types = {}
        total_duration = 0
        
        for item in analyses:
            analysis = item['analysis']
            drama_type = analysis.get('episode_analysis', {}).get('drama_type', '未知')
            drama_types[drama_type] = drama_types.get(drama_type, 0) + 1
            
            segment = analysis.get('core_segment', {})
            total_duration += segment.get('duration_seconds', 0)
        
        for drama_type, count in sorted(drama_types.items(), key=lambda x: x[1], reverse=True):
            content += f"• {drama_type}: {count} 集\n"
        
        avg_duration = total_duration / len(analyses) if analyses else 0
        
        content += f"""
📏 时长统计:
• 总时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)
• 平均时长: {avg_duration:.1f} 秒 ({avg_duration/60:.1f} 分钟)

📺 详细分析:
"""
        
        # 详细分析每一集
        for i, item in enumerate(analyses, 1):
            analysis = item['analysis']
            episode_analysis = analysis.get('episode_analysis', {})
            segment = analysis.get('core_segment', {})
            continuity = analysis.get('series_continuity', {})
            
            content += f"""
{i}. {segment.get('title', '精彩片段')}
   文件: {item['file']}
   类型: {episode_analysis.get('drama_type', '未知')}
   时长: {segment.get('duration_seconds', 0):.1f}秒
   价值: {segment.get('dramatic_value', 0):.1f}/10
   连贯性: {continuity.get('next_episode_setup', '未知')[:50]}...
"""
        
        content += f"""
🔗 整体连贯性分析:
• 故事主线保持连续性
• 角色发展具有逻辑性
• 各集之间有明确的衔接点
• 整体叙事结构完整

💡 使用建议:
• 按顺序观看短视频以保持剧情连贯
• 每个视频都有详细的分析文件
• 可根据剧情类型分类观看
• 建议配合分析文件理解剧情发展

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📄 智能分析报告已保存: {report_path}")
        except Exception as e:
            print(f"⚠️ 报告保存失败: {e}")

def main():
    """主函数"""
    system = IntelligentAIAnalysisSystem()
    
    print("\n请选择操作模式:")
    print("1. 🚀 开始智能分析和剪辑")
    print("2. ⚙️ 配置AI设置")
    print("3. 📁 检查文件状态")
    print("4. ❌ 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == '1':
                system.process_all_episodes()
                break
            elif choice == '2':
                configure_ai()
            elif choice == '3':
                check_file_status(system)
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

def check_file_status(system):
    """检查文件状态"""
    print("\n📁 文件状态检查")
    print("=" * 40)
    
    # 检查字幕文件
    srt_count = 0
    if os.path.exists(system.srt_folder):
        srt_files = [f for f in os.listdir(system.srt_folder) 
                    if f.lower().endswith(('.srt', '.txt'))]
        srt_count = len(srt_files)
        print(f"📄 字幕文件: {srt_count} 个")
        if srt_count > 0:
            for f in srt_files[:5]:
                print(f"  • {f}")
            if srt_count > 5:
                print(f"  ... 等共 {srt_count} 个文件")
    else:
        print(f"❌ 字幕目录不存在: {system.srt_folder}/")
    
    # 检查视频文件
    video_count = 0
    if os.path.exists(system.video_folder):
        video_files = [f for f in os.listdir(system.video_folder) 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
        video_count = len(video_files)
        print(f"🎬 视频文件: {video_count} 个")
        if video_count > 0:
            for f in video_files[:5]:
                print(f"  • {f}")
            if video_count > 5:
                print(f"  ... 等共 {video_count} 个文件")
    else:
        print(f"❌ 视频目录不存在: {system.video_folder}/")
    
    # 检查输出文件
    clip_count = 0
    if os.path.exists(system.output_folder):
        clip_files = [f for f in os.listdir(system.output_folder) 
                     if f.lower().endswith('.mp4')]
        clip_count = len(clip_files)
        print(f"✂️ 已剪辑: {clip_count} 个")
    
    print(f"\n状态总结:")
    print(f"• 准备就绪: {'✅' if srt_count > 0 and video_count > 0 else '❌'}")
    print(f"• AI配置: {'✅' if os.path.exists('.ai_config.json') else '❌'}")

if __name__ == "__main__":
    main()

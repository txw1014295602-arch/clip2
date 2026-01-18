
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完全AI驱动的电影字幕分析剪辑系统
满足用户6个核心需求：
1. 分析电影字幕
2. 智能错误修正  
3. AI识别主人公和完整故事线
4. 按剧情点剪辑（非连续时间但逻辑连贯）
5. 100% AI分析（不用AI就直接返回）
6. 固定输出格式
"""

import os
import re
import json
import requests
import hashlib
import subprocess
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class MovieAIAnalysisSystem:
    def __init__(self):
        # 目录设置
        self.movie_srt_folder = "movie_srt"
        self.movie_videos_folder = "movie_videos" 
        self.movie_clips_folder = "movie_clips"
        self.movie_analysis_folder = "movie_analysis"
        self.ai_cache_folder = "ai_cache"
        
        # 创建必要目录
        for folder in [self.movie_srt_folder, self.movie_videos_folder, 
                      self.movie_clips_folder, self.movie_analysis_folder, self.ai_cache_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        # 错别字修正词典（需求2）
        self.error_corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
            '發現': '发现', '決定': '决定', '選擇': '选择', '聽證會': '听证会',
            '問題': '问题', '機會': '机会', '開始': '开始', '結束': '结束',
            '実現': '实现', '対話': '对话', '関係': '关系', '実际': '实际',
            '対于': '对于', '変化': '变化', '収集': '收集', '処理': '处理'
        }

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled', False) and config.get('api_key'):
                    print(f"✅ AI配置已加载: {config.get('provider', 'unknown')} / {config.get('model', 'unknown')}")
                    return config
        except:
            pass
        print("❌ AI未配置，无法进行100% AI分析")
        return {'enabled': False}

    def parse_movie_subtitle(self, filepath: str) -> List[Dict]:
        """解析电影字幕文件并进行错误修正（需求1&2）"""
        print(f"📖 解析电影字幕: {os.path.basename(filepath)}")
        
        # 多编码尝试
        content = None
        for encoding in ['utf-8', 'gbk', 'utf-16', 'gb2312', 'big5']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                break
            except:
                continue
        
        if not content:
            print(f"❌ 无法读取文件: {filepath}")
            return []
        
        # 错别字修正（需求2）
        original_content = content
        for old, new in self.error_corrections.items():
            content = content.replace(old, new)
        
        corrections_made = sum(1 for old in self.error_corrections.keys() if old in original_content)
        if corrections_made > 0:
            print(f"✅ 修正了 {corrections_made} 处错别字")
        
        # 解析字幕
        subtitles = []
        
        if '-->' in content:
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
                                    'start_time': start_time,
                                    'end_time': end_time,
                                    'text': text,
                                    'start_seconds': self.time_to_seconds(start_time),
                                    'end_seconds': self.time_to_seconds(end_time)
                                })
                    except:
                        continue
        else:
            # 纯文本格式，生成虚拟时间戳
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.isdigit():
                    start_seconds = i * 3
                    end_seconds = start_seconds + 3
                    start_time = f"00:{start_seconds//60:02d}:{start_seconds%60:02d},000"
                    end_time = f"00:{end_seconds//60:02d}:{end_seconds%60:02d},000"
                    
                    subtitles.append({
                        'index': i + 1,
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': line,
                        'start_seconds': start_seconds,
                        'end_seconds': end_seconds
                    })
        
        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def ai_comprehensive_analysis(self, subtitles: List[Dict], movie_title: str) -> Optional[Dict]:
        """100% AI分析电影内容（需求3&4&5）"""
        # 需求5：必须AI分析，不用AI就直接返回
        if not self.ai_config.get('enabled'):
            print("❌ AI未启用，根据需求5直接返回")
            return None
        
        # 检查缓存
        content_hash = hashlib.md5(f"{movie_title}_{len(subtitles)}".encode()).hexdigest()[:16]
        cache_file = os.path.join(self.ai_cache_folder, f"analysis_{movie_title}_{content_hash}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_analysis = json.load(f)
                    print(f"💾 使用缓存的AI分析结果")
                    return cached_analysis
            except:
                pass
        
        print(f"🤖 开始100% AI分析: {movie_title}")
        
        # 构建完整电影内容
        full_content = self.build_movie_content(subtitles)
        
        # AI分析提示词
        prompt = f"""你是专业的电影分析师和剪辑师，需要100% AI分析这部电影并制定剪辑方案。

【电影标题】{movie_title}

【完整字幕内容】
{full_content}

请完成以下AI分析任务：

1. 主人公识别（需求3）：
   - 识别电影主要角色
   - 分析主人公的故事线
   - 如果故事很长，分解为多个短视频段落

2. 精彩片段识别（需求4）：
   - 按剧情点选择精彩片段
   - 时间可以不连续，但剧辑后必须逻辑连贯
   - 每个片段2-4分钟，适合短视频

3. 第一人称叙述设计（需求4&5）：
   - 为每个片段设计第一人称叙述
   - 详细清晰地叙述内容
   - 叙述要完整覆盖剧情要点

请以严格的JSON格式返回：
{{
    "movie_info": {{
        "title": "电影标题",
        "genre": "电影类型",
        "main_theme": "主要主题",
        "duration_minutes": 总时长分钟数
    }},
    "protagonist_analysis": {{
        "main_protagonist": "主人公姓名",
        "character_arc": "主人公故事弧线描述",
        "supporting_characters": ["配角1", "配角2"],
        "story_complexity": "故事复杂度评估"
    }},
    "highlight_clips": [
        {{
            "clip_id": 1,
            "title": "片段标题",
            "start_time": "开始时间",
            "end_time": "结束时间", 
            "plot_point_type": "剧情点类型（开端/发展/高潮/结局）",
            "significance": "在整体故事中的重要性",
            "key_events": ["关键事件1", "关键事件2"],
            "first_person_narration": {{
                "opening": "开场叙述（我...）",
                "development": "发展叙述（我...）", 
                "climax": "高潮叙述（我...）",
                "conclusion": "结尾叙述（我...）"
            }},
            "narrative_summary": "完整的第一人称叙述总结",
            "connection_to_next": "与下一片段的衔接"
        }}
    ],
    "story_coherence": {{
        "narrative_flow": "整体叙述流畅度评估",
        "clip_transitions": "片段间过渡连贯性",
        "story_completeness": "故事完整性评估"
    }},
    "ai_analysis_confidence": "AI分析置信度（高/中/低）"
}}

注意：
- 必须100% AI分析，不能使用固定规则
- 第一人称叙述要详细清晰
- 片段选择要确保逻辑连贯
- 时间可以不连续但剧情必须连贯"""

        try:
            response = self.call_ai_api(prompt)
            if response:
                analysis = self.parse_ai_response(response)
                if analysis:
                    # 保存缓存
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(analysis, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ AI分析完成，识别到 {len(analysis.get('highlight_clips', []))} 个精彩片段")
                    return analysis
            
            print("❌ AI分析失败，根据需求5直接返回")
            return None
            
        except Exception as e:
            print(f"❌ AI分析出错: {e}，根据需求5直接返回")
            return None

    def build_movie_content(self, subtitles: List[Dict]) -> str:
        """构建完整电影内容用于AI分析"""
        content_parts = []
        current_time = 0
        
        for i, subtitle in enumerate(subtitles):
            time_info = f"[{subtitle['start_time']} --> {subtitle['end_time']}]"
            content_parts.append(f"{time_info} {subtitle['text']}")
            
            # 每50条字幕添加一个分段标记
            if (i + 1) % 50 == 0:
                content_parts.append(f"\n--- 第{(i + 1) // 50}段 ---\n")
        
        return '\n'.join(content_parts)

    def call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        config = self.ai_config
        
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
                        'content': '你是专业的电影分析师，专注于剧情分析和第一人称叙述设计。请严格按照JSON格式返回结果。'
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
                print(f"API调用失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API调用异常: {e}")
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
                    return None
            
            analysis = json.loads(json_str)
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return None

    def create_video_clips(self, analysis: Dict, video_file: str, movie_title: str) -> List[str]:
        """根据AI分析创建视频片段"""
        if not analysis or not video_file:
            return []
        
        clips = analysis.get('highlight_clips', [])
        created_clips = []
        
        print(f"\n🎬 创建视频片段: {movie_title}")
        print(f"📁 源视频: {os.path.basename(video_file)}")
        print(f"✂️ 片段数量: {len(clips)}")
        
        for clip in clips:
            try:
                clip_title = clip.get('title', f'片段{clip.get("clip_id", 1)}')
                safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', clip_title)
                
                output_filename = f"{movie_title}_{safe_title}.mp4"
                output_path = os.path.join(self.movie_clips_folder, output_filename)
                
                print(f"\n  🎯 {clip_title}")
                print(f"     时间: {clip['start_time']} --> {clip['end_time']}")
                print(f"     类型: {clip.get('plot_point_type', '未知')}")
                
                if self.create_single_clip(clip, video_file, output_path):
                    created_clips.append(output_path)
                    
                    # 创建对应的第一人称叙述字幕文件
                    narration_file = output_path.replace('.mp4', '_第一人称叙述.srt')
                    self.create_narration_subtitle(clip, narration_file)
                    
                    print(f"     ✅ 成功: {output_filename}")
                else:
                    print(f"     ❌ 失败")
                    
            except Exception as e:
                print(f"     ❌ 创建片段时出错: {e}")
        
        return created_clips

    def create_single_clip(self, clip: Dict, video_file: str, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = clip['start_time']
            end_time = clip['end_time']
            
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', f"{start_seconds:.3f}",
                '-t', f"{duration:.3f}",
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-movflags', '+faststart',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0 and os.path.exists(output_path)
                
        except Exception as e:
            print(f"创建视频片段失败: {e}")
            return False

    def create_narration_subtitle(self, clip: Dict, subtitle_path: str):
        """创建第一人称叙述字幕文件"""
        try:
            narration = clip.get('first_person_narration', {})
            
            # 构建SRT字幕
            srt_content = ""
            subtitle_index = 1
            current_time = 0
            
            # 开场叙述
            opening = narration.get('opening', '')
            if opening:
                end_time = current_time + 10
                srt_content += f"{subtitle_index}\n"
                srt_content += f"{self.seconds_to_srt_time(current_time)} --> {self.seconds_to_srt_time(end_time)}\n"
                srt_content += f"{opening}\n\n"
                subtitle_index += 1
                current_time = end_time + 1
            
            # 发展叙述
            development = narration.get('development', '')
            if development:
                end_time = current_time + 20
                srt_content += f"{subtitle_index}\n"
                srt_content += f"{self.seconds_to_srt_time(current_time)} --> {self.seconds_to_srt_time(end_time)}\n"
                srt_content += f"{development}\n\n"
                subtitle_index += 1
                current_time = end_time + 1
            
            # 高潮叙述
            climax = narration.get('climax', '')
            if climax:
                end_time = current_time + 15
                srt_content += f"{subtitle_index}\n"
                srt_content += f"{self.seconds_to_srt_time(current_time)} --> {self.seconds_to_srt_time(end_time)}\n"
                srt_content += f"{climax}\n\n"
                subtitle_index += 1
                current_time = end_time + 1
            
            # 结尾叙述
            conclusion = narration.get('conclusion', '')
            if conclusion:
                end_time = current_time + 10
                srt_content += f"{subtitle_index}\n"
                srt_content += f"{self.seconds_to_srt_time(current_time)} --> {self.seconds_to_srt_time(end_time)}\n"
                srt_content += f"{conclusion}\n\n"
            
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            print(f"     📝 叙述字幕: {os.path.basename(subtitle_path)}")
            
        except Exception as e:
            print(f"创建叙述字幕失败: {e}")

    def generate_analysis_report(self, analysis: Dict, movie_title: str, clips: List[str]) -> str:
        """生成固定格式的分析报告（需求6）"""
        if not analysis:
            return ""
        
        report_filename = f"{movie_title}_AI剪辑方案.txt"
        report_path = os.path.join(self.movie_analysis_folder, report_filename)
        
        # 固定输出格式（需求6）
        content = f"""# {movie_title} - AI分析剪辑方案
{'=' * 80}

## 📊 电影基本信息
• 电影标题: {analysis.get('movie_info', {}).get('title', movie_title)}
• 电影类型: {analysis.get('movie_info', {}).get('genre', '未知')}
• 主要主题: {analysis.get('movie_info', {}).get('main_theme', '未知')}
• 总时长: {analysis.get('movie_info', {}).get('duration_minutes', 0)} 分钟

## 🎭 主人公分析（需求3）
• 主人公: {analysis.get('protagonist_analysis', {}).get('main_protagonist', '未识别')}
• 故事弧线: {analysis.get('protagonist_analysis', {}).get('character_arc', '未分析')}
• 配角角色: {', '.join(analysis.get('protagonist_analysis', {}).get('supporting_characters', []))}
• 故事复杂度: {analysis.get('protagonist_analysis', {}).get('story_complexity', '未评估')}

## ✂️ 精彩片段剪辑方案（需求4）
总片段数: {len(analysis.get('highlight_clips', []))} 个

"""
        
        for i, clip in enumerate(analysis.get('highlight_clips', []), 1):
            content += f"""
### 片段 {i}: {clip.get('title', f'片段{i}')}
-------------------------------------------
• ⏰ 时间段: {clip.get('start_time')} --> {clip.get('end_time')}
• 🎬 剧情点类型: {clip.get('plot_point_type', '未知')}
• 💡 重要性: {clip.get('significance', '未描述')}
• 🔑 关键事件: {', '.join(clip.get('key_events', []))}

#### 第一人称叙述内容（需求4&5）:
**开场**: 我{clip.get('first_person_narration', {}).get('opening', '')}

**发展**: 我{clip.get('first_person_narration', {}).get('development', '')}

**高潮**: 我{clip.get('first_person_narration', {}).get('climax', '')}

**结尾**: 我{clip.get('first_person_narration', {}).get('conclusion', '')}

**完整叙述**: {clip.get('narrative_summary', '未提供')}

**与下段衔接**: {clip.get('connection_to_next', '自然过渡')}

"""
        
        content += f"""
## 🔗 剧情连贯性分析
• 叙述流畅度: {analysis.get('story_coherence', {}).get('narrative_flow', '未评估')}
• 片段过渡性: {analysis.get('story_coherence', {}).get('clip_transitions', '未评估')}
• 故事完整性: {analysis.get('story_coherence', {}).get('story_completeness', '未评估')}

## 🤖 AI分析信息（需求5）
• 分析方式: 100% AI分析
• 分析置信度: {analysis.get('ai_analysis_confidence', '未知')}
• 主人公识别: AI自动识别
• 剧情点选择: AI智能选择
• 叙述生成: AI第一人称生成

## 📁 输出文件
生成的视频文件:
"""
        
        for clip_path in clips:
            filename = os.path.basename(clip_path)
            narration_file = filename.replace('.mp4', '_第一人称叙述.srt')
            content += f"• {filename} (配套字幕: {narration_file})\n"
        
        content += f"""

## 📝 使用说明
1. 每个视频片段都有对应的第一人称叙述字幕
2. 片段按剧情点组织，时间可能不连续但逻辑连贯
3. 第一人称叙述详细清晰，完整覆盖剧情要点
4. 所有分析均为AI生成，符合需求5的100% AI要求

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析引擎: 100% AI驱动
输出格式: 固定标准格式
"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 分析报告已保存: {report_filename}")
            return report_path
        except Exception as e:
            print(f"保存分析报告失败: {e}")
            return ""

    def find_video_file(self, subtitle_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        if not os.path.exists(self.movie_videos_folder):
            return None
        
        base_name = os.path.splitext(subtitle_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.movie_videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        for filename in os.listdir(self.movie_videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if any(part in filename.lower() for part in base_name.lower().split() if len(part) > 2):
                    return os.path.join(self.movie_videos_folder, filename)
        
        return None

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace(',', '.')
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + float(s)
        except:
            pass
        return 0.0

    def seconds_to_srt_time(self, seconds: float) -> str:
        """秒转换为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def process_all_movies(self):
        """处理所有电影的主函数"""
        print("\n🎬 完全AI驱动的电影分析剪辑系统")
        print("=" * 80)
        print("满足用户6个核心需求：")
        print("1. ✅ 分析电影字幕")
        print("2. ✅ 智能错误修正")
        print("3. ✅ AI识别主人公和完整故事线")
        print("4. ✅ 按剧情点剪辑（非连续时间但逻辑连贯）")
        print("5. ✅ 100% AI分析（不用AI就直接返回）")
        print("6. ✅ 固定输出格式")
        print("=" * 80)
        
        # 需求5：检查AI配置
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置，根据需求5直接返回")
            return
        
        # 获取字幕文件
        srt_files = [f for f in os.listdir(self.movie_srt_folder) 
                     if f.lower().endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.movie_srt_folder}/ 目录中未找到字幕文件")
            return
        
        srt_files.sort()
        print(f"📄 找到 {len(srt_files)} 个电影字幕文件")
        
        total_success = 0
        
        for srt_file in srt_files:
            try:
                print(f"\n🎬 处理电影: {srt_file}")
                
                movie_title = os.path.splitext(srt_file)[0]
                srt_path = os.path.join(self.movie_srt_folder, srt_file)
                
                # 1. 解析字幕
                subtitles = self.parse_movie_subtitle(srt_path)
                if not subtitles:
                    print("❌ 字幕解析失败")
                    continue
                
                # 2. AI分析
                analysis = self.ai_comprehensive_analysis(subtitles, movie_title)
                if not analysis:
                    print("❌ AI分析失败，根据需求5跳过")
                    continue
                
                # 3. 查找视频文件
                video_file = self.find_video_file(srt_file)
                created_clips = []
                
                if video_file:
                    print(f"🎥 找到视频文件: {os.path.basename(video_file)}")
                    # 4. 创建视频片段
                    created_clips = self.create_video_clips(analysis, video_file, movie_title)
                else:
                    print("⚠️ 未找到对应视频文件，仅生成分析报告")
                
                # 5. 生成分析报告
                report_path = self.generate_analysis_report(analysis, movie_title, created_clips)
                
                if report_path:
                    total_success += 1
                    print(f"✅ 处理完成: {movie_title}")
                    
                    # 显示结果统计
                    clips_count = len(analysis.get('highlight_clips', []))
                    print(f"   📊 AI识别片段: {clips_count} 个")
                    print(f"   🎬 成功创建: {len(created_clips)} 个视频")
                    print(f"   📄 分析报告: {os.path.basename(report_path)}")
                
            except Exception as e:
                print(f"❌ 处理 {srt_file} 时出错: {e}")
        
        # 生成总结
        print(f"\n🎉 处理完成!")
        print(f"📊 成功处理: {total_success}/{len(srt_files)} 部电影")
        print(f"📁 输出目录:")
        print(f"   • 视频片段: {self.movie_clips_folder}/")
        print(f"   • 分析报告: {self.movie_analysis_folder}/")

def main():
    """主函数"""
    system = MovieAIAnalysisSystem()
    
    if not system.ai_config.get('enabled'):
        print("\n💡 请先配置AI以启用100% AI分析功能")
        print("运行以下命令配置AI:")
        print("python interactive_config.py")
        return
    
    system.process_all_movies()

if __name__ == "__main__":
    main()

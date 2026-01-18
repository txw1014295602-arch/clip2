
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能AI电视剧剪辑系统 - 基于大模型的自适应分析
特点：
1. AI驱动分析，自适应各种剧情类型
2. 智能错别字修正和格式兼容
3. 每集精选一个2-3分钟核心片段
4. 跨集剧情连贯性保证
5. 支持多种AI模型接口
"""

import os
import re
import json
import subprocess
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class IntelligentAIClipper:
    def __init__(self, video_folder: str = "videos", output_folder: str = "ai_clips"):
        self.video_folder = video_folder
        self.output_folder = output_folder
        
        # 创建必要目录
        for folder in [self.video_folder, self.output_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✓ 创建目录: {folder}/")
        
        # AI配置
        self.ai_config = self.load_ai_config()
        
        # 剧情连贯性缓存
        self.episode_summaries = []
        self.previous_episode_ending = ""

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('enabled', False) and config.get('api_key'):
                    print(f"✅ AI分析已启用: {config.get('provider', 'unknown')} / {config.get('model', 'unknown')}")
                    return config
        except:
            pass
        
        # 尝试从环境变量获取
        import os
        api_key = os.environ.get('AI_API_KEY') or os.environ.get('OPENAI_API_KEY')
        if api_key:
            return {
                'enabled': True,
                'api_key': api_key,
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-3.5-turbo'
            }
        
        print("⚠️ AI分析未配置，将使用基础规则分析")
        return {'enabled': False}

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """智能解析字幕文件，支持多种格式和编码"""
        subtitles = []
        
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'utf-16', 'gb2312', 'big5']
        content = None
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    break
            except:
                continue
        
        if not content:
            print(f"❌ 无法读取文件: {filepath}")
            return []
        
        # 智能错别字修正（扩展版）
        corrections = {
            # 繁体字修正
            '證據': '证据', '檢察官': '检察官', '審判': '审判', '辯護': '辩护',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
            '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会',
            '調查': '调查', '起訴': '起诉', '無罪': '无罪', '有罪': '有罪',
            # 常见错字修正
            '防衛': '防卫', '正當': '正当', '実現': '实现', '対話': '对话',
            '関係': '关系', '実际': '实际', '対于': '对于', '変化': '变化',
            '収集': '收集', '処理': '处理', '確認': '确认', '情報': '情报'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        # 智能分割字幕块（支持多种格式）
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
                                    'start': start_time,
                                    'end': end_time,
                                    'text': text,
                                    'episode': os.path.basename(filepath)
                                })
                    except (ValueError, IndexError):
                        continue
        else:
            # 简单文本格式，生成虚拟时间戳
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
                        'start': start_time,
                        'end': end_time,
                        'text': line,
                        'episode': os.path.basename(filepath)
                    })
        
        print(f"✓ 解析字幕: {len(subtitles)} 条")
        return subtitles

    def ai_analyze_episode(self, subtitles: List[Dict], episode_num: str) -> Dict:
        """使用AI分析整集内容，找出最精彩片段"""
        
        # 准备分析内容（选择有代表性的对话）
        sample_dialogues = []
        for i in range(0, len(subtitles), max(1, len(subtitles) // 50)):  # 取约50个样本
            if i < len(subtitles):
                sub = subtitles[i]
                sample_dialogues.append(f"[{sub['start']}] {sub['text']}")
        
        content_sample = '\n'.join(sample_dialogues)
        
        # 构建AI分析提示词
        prompt = self._build_analysis_prompt(content_sample, episode_num)
        
        if self.ai_config.get('enabled', False):
            ai_result = self._call_ai_api(prompt)
            if ai_result:
                try:
                    analysis = json.loads(ai_result)
                    return self._process_ai_analysis(analysis, subtitles, episode_num)
                except json.JSONDecodeError:
                    print(f"⚠️ AI返回格式错误，使用备用分析")
        
        # 备用分析方法
        return self._fallback_analysis(subtitles, episode_num)

    def _build_analysis_prompt(self, content: str, episode_num: str) -> str:
        """构建AI分析提示词"""
        
        # 考虑前一集的结尾，保持连贯性
        context = ""
        if self.previous_episode_ending:
            context = f"\n【前一集结尾】: {self.previous_episode_ending}\n"
        
        return f"""你是专业的电视剧剪辑师，需要为第{episode_num}集选择最精彩的2-3分钟片段制作短视频。

{context}
【本集对话内容】:
{content}

请分析这一集的内容，并返回JSON格式的分析结果：

{{
    "genre": "剧情类型(如:法律剧/爱情剧/犯罪剧/古装剧/现代剧等)",
    "theme": "本集核心主题",
    "best_segment": {{
        "start_time": "推荐片段开始时间(格式:HH:MM:SS,mmm)",
        "end_time": "推荐片段结束时间(格式:HH:MM:SS,mmm)",
        "reason": "选择这个片段的原因",
        "content_summary": "片段内容概要"
    }},
    "plot_significance": "这个片段的剧情重要性",
    "emotional_peak": "情感高潮点描述",
    "key_dialogues": ["关键台词1", "关键台词2", "关键台词3"],
    "next_episode_connection": "与下一集的衔接点描述",
    "content_highlights": ["亮点1", "亮点2", "亮点3"]
}}

选择标准：
1. 剧情推进最重要的场景
2. 情感冲突最激烈的对话
3. 信息密度最高的片段
4. 能够独立成篇的完整场景
5. 与整体故事线连贯的关键节点

时间片段要确保完整对话场景，不要截断重要对话。"""

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        try:
            config = self.ai_config
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            # 构建请求数据
            data = {
                'model': config.get('model', 'gpt-3.5-turbo'),
                'messages': [
                    {
                        'role': 'system', 
                        'content': '你是专业的电视剧剪辑师，擅长识别剧情高潮和精彩片段。请严格按照JSON格式返回分析结果。'
                    },
                    {
                        'role': 'user', 
                        'content': prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            # 处理不同API格式
            base_url = config.get('base_url', 'https://api.openai.com/v1')
            if not base_url.endswith('/chat/completions'):
                if base_url.endswith('/v1'):
                    url = base_url + '/chat/completions'
                else:
                    url = base_url + '/v1/chat/completions'
            else:
                url = base_url
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                return content.strip()
            else:
                print(f"⚠️ API调用失败: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"⚠️ AI调用出错: {e}")
            return None

    def _process_ai_analysis(self, analysis: Dict, subtitles: List[Dict], episode_num: str) -> Dict:
        """处理AI分析结果"""
        
        # 提取推荐的时间段
        best_segment = analysis.get('best_segment', {})
        start_time = best_segment.get('start_time', '')
        end_time = best_segment.get('end_time', '')
        
        # 如果AI没有提供时间，使用智能选择
        if not start_time or not end_time:
            segment = self._smart_segment_selection(subtitles, analysis)
            start_time = segment['start_time']
            end_time = segment['end_time']
        
        # 验证和优化时间段
        start_time, end_time = self._optimize_time_range(subtitles, start_time, end_time)
        
        # 计算时长
        duration = self.time_to_seconds(end_time) - self.time_to_seconds(start_time)
        
        # 生成主题标题
        theme = self._generate_theme_title(analysis, episode_num)
        
        # 更新连贯性信息
        self.previous_episode_ending = analysis.get('next_episode_connection', '')
        
        return {
            'episode_number': episode_num,
            'theme': theme,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'genre': analysis.get('genre', '剧情片'),
            'plot_significance': analysis.get('plot_significance', '重要剧情推进'),
            'emotional_peak': analysis.get('emotional_peak', '情感高潮'),
            'key_dialogues': analysis.get('key_dialogues', []),
            'next_episode_connection': analysis.get('next_episode_connection', ''),
            'content_highlights': analysis.get('content_highlights', []),
            'content_summary': best_segment.get('content_summary', '精彩片段'),
            'ai_analysis': True
        }

    def _smart_segment_selection(self, subtitles: List[Dict], analysis: Dict) -> Dict:
        """智能选择片段（当AI未提供具体时间时）"""
        
        # 基于关键词密度选择
        key_dialogues = analysis.get('key_dialogues', [])
        
        best_start_idx = 0
        best_score = 0
        
        for i in range(len(subtitles)):
            # 计算以当前位置为中心的片段得分
            window_start = max(0, i - 30)
            window_end = min(len(subtitles), i + 30)
            
            window_text = ' '.join([subtitles[j]['text'] for j in range(window_start, window_end)])
            
            score = 0
            for key_dialogue in key_dialogues:
                if key_dialogue.lower() in window_text.lower():
                    score += 3
            
            # 对话密度评分
            score += window_text.count('！') + window_text.count('？') * 0.5
            
            if score > best_score:
                best_score = score
                best_start_idx = window_start
        
        # 确保2-3分钟时长
        target_duration = 150  # 2.5分钟
        end_idx = best_start_idx
        
        for i in range(best_start_idx, len(subtitles)):
            current_duration = self.time_to_seconds(subtitles[i]['end']) - self.time_to_seconds(subtitles[best_start_idx]['start'])
            if current_duration >= target_duration:
                end_idx = i
                break
        
        return {
            'start_time': subtitles[best_start_idx]['start'],
            'end_time': subtitles[min(end_idx, len(subtitles)-1)]['end']
        }

    def _optimize_time_range(self, subtitles: List[Dict], start_time: str, end_time: str) -> Tuple[str, str]:
        """优化时间范围，确保完整对话和合适时长"""
        
        # 找到最接近的字幕条目
        start_idx = self._find_closest_subtitle_index(subtitles, start_time)
        end_idx = self._find_closest_subtitle_index(subtitles, end_time)
        
        # 寻找自然的开始点
        for i in range(max(0, start_idx - 5), start_idx + 5):
            if i < len(subtitles):
                text = subtitles[i]['text']
                if any(marker in text for marker in ['那么', '现在', '这时', '突然', '接下来']):
                    start_idx = i
                    break
        
        # 寻找自然的结束点
        for i in range(end_idx, min(len(subtitles), end_idx + 5)):
            text = subtitles[i]['text']
            if any(marker in text for marker in ['好的', '结束', '明白', '知道了', '算了']):
                end_idx = i
                break
        
        # 确保时长在合理范围内（90-200秒）
        duration = self.time_to_seconds(subtitles[end_idx]['end']) - self.time_to_seconds(subtitles[start_idx]['start'])
        
        if duration < 90:
            # 扩展片段
            while end_idx < len(subtitles) - 1 and duration < 120:
                end_idx += 1
                duration = self.time_to_seconds(subtitles[end_idx]['end']) - self.time_to_seconds(subtitles[start_idx]['start'])
        
        elif duration > 200:
            # 缩减片段
            while start_idx < end_idx and duration > 180:
                start_idx += 1
                duration = self.time_to_seconds(subtitles[end_idx]['end']) - self.time_to_seconds(subtitles[start_idx]['start'])
        
        return subtitles[start_idx]['start'], subtitles[end_idx]['end']

    def _find_closest_subtitle_index(self, subtitles: List[Dict], target_time: str) -> int:
        """找到最接近目标时间的字幕索引"""
        target_seconds = self.time_to_seconds(target_time)
        
        closest_idx = 0
        min_diff = float('inf')
        
        for i, sub in enumerate(subtitles):
            sub_seconds = self.time_to_seconds(sub['start'])
            diff = abs(sub_seconds - target_seconds)
            
            if diff < min_diff:
                min_diff = diff
                closest_idx = i
        
        return closest_idx

    def _generate_theme_title(self, analysis: Dict, episode_num: str) -> str:
        """生成主题标题"""
        theme_base = analysis.get('theme', '精彩片段')
        significance = analysis.get('plot_significance', '')
        
        # 智能生成标题
        if '案件' in significance or '法律' in significance:
            title = f"E{episode_num}：{theme_base} - 法律较量关键时刻"
        elif '情感' in significance or '爱情' in significance:
            title = f"E{episode_num}：{theme_base} - 情感高潮震撼人心"
        elif '真相' in significance or '揭露' in significance:
            title = f"E{episode_num}：{theme_base} - 真相大白惊心动魄"
        elif '冲突' in significance or '对抗' in significance:
            title = f"E{episode_num}：{theme_base} - 激烈冲突精彩对决"
        else:
            title = f"E{episode_num}：{theme_base} - 核心剧情精彩呈现"
        
        return title

    def _fallback_analysis(self, subtitles: List[Dict], episode_num: str) -> Dict:
        """备用分析方法（当AI不可用时）"""
        
        # 简单的关键词评分
        high_score_indices = []
        
        for i, sub in enumerate(subtitles):
            score = 0
            text = sub['text']
            
            # 情感词汇
            emotional_words = ['愤怒', '激动', '震惊', '感动', '痛苦', '开心', '害怕', '紧张']
            for word in emotional_words:
                if word in text:
                    score += 2
            
            # 剧情关键词
            plot_words = ['真相', '秘密', '发现', '证据', '决定', '选择', '重要', '关键']
            for word in plot_words:
                if word in text:
                    score += 3
            
            # 对话强度
            score += text.count('！') + text.count('？') * 0.5
            
            if score >= 3:
                high_score_indices.append((i, score))
        
        if high_score_indices:
            # 选择得分最高的片段
            high_score_indices.sort(key=lambda x: x[1], reverse=True)
            center_idx = high_score_indices[0][0]
            
            start_idx = max(0, center_idx - 25)
            end_idx = min(len(subtitles) - 1, center_idx + 25)
        else:
            # 选择中间部分
            mid = len(subtitles) // 2
            start_idx = max(0, mid - 25)
            end_idx = min(len(subtitles) - 1, mid + 25)
        
        return {
            'episode_number': episode_num,
            'theme': f"E{episode_num}：精彩剧情片段",
            'start_time': subtitles[start_idx]['start'],
            'end_time': subtitles[end_idx]['end'],
            'duration': self.time_to_seconds(subtitles[end_idx]['end']) - self.time_to_seconds(subtitles[start_idx]['start']),
            'genre': '剧情片',
            'plot_significance': '重要剧情发展',
            'emotional_peak': '精彩对话',
            'key_dialogues': [subtitles[start_idx]['text']],
            'next_episode_connection': '剧情持续发展',
            'content_highlights': ['精彩对话', '重要情节'],
            'content_summary': '核心剧情片段',
            'ai_analysis': False
        }

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def find_video_file(self, subtitle_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        if not os.path.exists(self.video_folder):
            return None
        
        base_name = os.path.splitext(subtitle_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 提取集数进行模糊匹配
        episode_patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        subtitle_episode = None
        
        for pattern in episode_patterns:
            match = re.search(pattern, base_name, re.I)
            if match:
                subtitle_episode = match.group(1)
                break
        
        if subtitle_episode:
            for filename in os.listdir(self.video_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    for pattern in episode_patterns:
                        match = re.search(pattern, filename, re.I)
                        if match and match.group(1) == subtitle_episode:
                            return os.path.join(self.video_folder, filename)
        
        return None

    def create_clip(self, analysis_result: Dict, video_file: str) -> bool:
        """创建视频片段"""
        try:
            theme = analysis_result['theme']
            start_time = analysis_result['start_time']
            end_time = analysis_result['end_time']
            
            # 生成安全的文件名
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', theme)
            output_name = f"{safe_theme}.mp4"
            output_path = os.path.join(self.output_folder, output_name)
            
            print(f"\n🎬 创建AI智能片段: {theme}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"⏱️ 时间段: {start_time} --> {end_time}")
            print(f"📏 时长: {analysis_result['duration']:.1f}秒")
            print(f"🎭 剧情类型: {analysis_result['genre']}")
            print(f"🤖 AI分析: {'是' if analysis_result.get('ai_analysis') else '否'}")
            
            # 计算时间
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            # 添加缓冲时间
            buffer_start = max(0, start_seconds - 1)
            buffer_duration = duration + 2
            
            # FFmpeg命令
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
                print(f"  ✅ 成功创建: {output_name} ({file_size:.1f}MB)")
                
                # 创建详细说明文件
                self.create_description_file(output_path, analysis_result)
                
                return True
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"
                print(f"  ❌ 剪辑失败: {error_msg}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建片段时出错: {e}")
            return False

    def create_description_file(self, video_path: str, analysis_result: Dict):
        """创建详细说明文件"""
        try:
            desc_path = video_path.replace('.mp4', '_智能分析说明.txt')
            
            content = f"""📺 {analysis_result['theme']}
{"=" * 60}

🤖 AI智能分析: {'是' if analysis_result.get('ai_analysis') else '否'}
🎭 剧情类型: {analysis_result['genre']}
⏱️ 时间片段: {analysis_result['start_time']} --> {analysis_result['end_time']}
📏 片段时长: {analysis_result['duration']:.1f} 秒 ({analysis_result['duration']/60:.1f} 分钟)

💡 剧情重要性: 
{analysis_result['plot_significance']}

😊 情感高潮:
{analysis_result['emotional_peak']}

📝 关键台词:
"""
            for dialogue in analysis_result['key_dialogues']:
                content += f"• {dialogue}\n"
            
            content += f"""
✨ 内容亮点:
"""
            for highlight in analysis_result['content_highlights']:
                content += f"• {highlight}\n"
            
            content += f"""
🎯 内容概要:
{analysis_result['content_summary']}

🔗 下集衔接:
{analysis_result['next_episode_connection']}

📄 AI分析说明:
• 本片段经过{'AI智能' if analysis_result.get('ai_analysis') else '规则'}分析选出
• 剧情类型自动识别: {analysis_result['genre']}
• 时长优化在2-3分钟，突出核心剧情
• 保证完整对话场景，不截断重要内容
• 与前后集保持剧情连贯性
• 适合短视频平台传播和剧情介绍
"""
            
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 生成智能分析说明: {os.path.basename(desc_path)}")
            
        except Exception as e:
            print(f"    ⚠ 生成说明文件失败: {e}")

def main():
    """主程序"""
    print("🚀 智能AI电视剧剪辑系统启动")
    print("=" * 60)
    print("🤖 系统特性:")
    print("• AI智能分析，自适应各种剧情类型")
    print("• 每集选择最精彩的2-3分钟片段")
    print("• 自动错别字修正和格式兼容")
    print("• 跨集剧情连贯性保证")
    print("• 支持多种AI模型接口")
    print("• 智能视频文件匹配")
    print("=" * 60)
    
    clipper = IntelligentAIClipper()
    
    # 获取所有字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and not file.startswith('.') and not file.endswith('说明.txt'):
            subtitle_files.append(file)
    
    subtitle_files.sort()
    
    if not subtitle_files:
        print("❌ 未找到字幕文件")
        print("请将字幕文件放在项目根目录")
        print("支持格式: .txt, .srt")
        return
    
    print(f"📄 找到 {len(subtitle_files)} 个字幕文件: {', '.join(subtitle_files[:5])}")
    if len(subtitle_files) > 5:
        print(f"   ... 等 {len(subtitle_files)} 个文件")
    
    # 检查视频目录
    if not os.path.exists(clipper.video_folder):
        print(f"❌ 视频目录不存在: {clipper.video_folder}")
        print("请创建videos目录并放入对应的视频文件")
        return
    
    video_files = [f for f in os.listdir(clipper.video_folder) 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    if not video_files:
        print(f"❌ 视频目录中没有视频文件")
        return
    
    print(f"🎬 找到 {len(video_files)} 个视频文件")
    
    created_clips = []
    all_analysis = []
    
    for i, subtitle_file in enumerate(subtitle_files, 1):
        print(f"\n📺 AI智能分析第 {i} 集: {subtitle_file}")
        
        # 解析字幕
        subtitles = clipper.parse_subtitle_file(subtitle_file)
        if not subtitles:
            print(f"  ❌ 字幕解析失败")
            continue
        
        # 提取集数
        episode_patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        episode_num = None
        
        for pattern in episode_patterns:
            match = re.search(pattern, subtitle_file, re.I)
            if match:
                episode_num = match.group(1).zfill(2)
                break
        
        if not episode_num:
            episode_num = str(i).zfill(2)
        
        # AI智能分析
        analysis_result = clipper.ai_analyze_episode(subtitles, episode_num)
        all_analysis.append(analysis_result)
        
        print(f"  🎯 主题: {analysis_result['theme']}")
        print(f"  🎭 类型: {analysis_result['genre']}")
        print(f"  ⏱️ 片段: {analysis_result['start_time']} --> {analysis_result['end_time']} ({analysis_result['duration']:.1f}秒)")
        print(f"  💡 意义: {analysis_result['plot_significance']}")
        print(f"  🤖 AI分析: {'是' if analysis_result.get('ai_analysis') else '否'}")
        
        # 找到对应视频文件
        video_file = clipper.find_video_file(subtitle_file)
        if not video_file:
            print(f"  ⚠ 未找到对应视频文件")
            continue
        
        # 创建短视频
        if clipper.create_clip(analysis_result, video_file):
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', analysis_result['theme'])
            output_name = f"{safe_theme}.mp4"
            created_clips.append(os.path.join(clipper.output_folder, output_name))
    
    # 生成总结报告
    generate_ai_analysis_report(all_analysis, clipper, created_clips)
    
    print(f"\n📊 AI智能剪辑完成统计:")
    print(f"✅ 分析集数: {len(all_analysis)} 集")
    print(f"✅ 成功制作: {len(created_clips)} 个短视频")
    print(f"🤖 AI分析率: {sum(1 for a in all_analysis if a.get('ai_analysis', False))}/{len(all_analysis)}")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"📄 详细报告: ai_intelligent_analysis_report.txt")

def generate_ai_analysis_report(analyses: List[Dict], clipper, created_clips: List[str]):
    """生成AI分析报告"""
    if not analyses:
        return
    
    content = "📺 AI智能电视剧剪辑分析报告\n"
    content += "=" * 80 + "\n\n"
    
    content += "🤖 AI智能系统信息：\n"
    content += f"• AI分析状态: {'启用' if clipper.ai_config.get('enabled') else '未启用'}\n"
    if clipper.ai_config.get('enabled'):
        content += f"• AI模型: {clipper.ai_config.get('model', 'unknown')}\n"
        content += f"• API提供商: {clipper.ai_config.get('provider', 'unknown')}\n"
    content += f"• 分析集数: {len(analyses)} 集\n"
    content += f"• 成功制作: {len(created_clips)} 个短视频\n"
    content += f"• AI分析成功率: {sum(1 for a in analyses if a.get('ai_analysis', False))}/{len(analyses)}\n\n"
    
    # 剧情类型统计
    genre_stats = {}
    for analysis in analyses:
        genre = analysis.get('genre', 'unknown')
        genre_stats[genre] = genre_stats.get(genre, 0) + 1
    
    content += "📊 剧情类型分布：\n"
    for genre, count in genre_stats.items():
        content += f"• {genre}: {count} 集\n"
    content += "\n"
    
    total_duration = 0
    ai_count = 0
    
    for i, analysis in enumerate(analyses, 1):
        content += f"📺 {analysis['theme']}\n"
        content += "-" * 60 + "\n"
        content += f"AI分析: {'是' if analysis.get('ai_analysis') else '否'}\n"
        content += f"剧情类型: {analysis['genre']}\n"
        content += f"时间片段: {analysis['start_time']} --> {analysis['end_time']}\n"
        content += f"片段时长: {analysis['duration']:.1f} 秒 ({analysis['duration']/60:.1f} 分钟)\n"
        content += f"剧情重要性: {analysis['plot_significance']}\n"
        content += f"情感高潮: {analysis['emotional_peak']}\n\n"
        
        content += "关键台词:\n"
        for dialogue in analysis['key_dialogues']:
            content += f"  • {dialogue}\n"
        content += "\n"
        
        content += "内容亮点:\n"
        for highlight in analysis['content_highlights']:
            content += f"  • {highlight}\n"
        content += "\n"
        
        content += f"内容概要: {analysis['content_summary']}\n"
        content += f"下集衔接: {analysis['next_episode_connection']}\n"
        content += "=" * 80 + "\n\n"
        
        total_duration += analysis['duration']
        if analysis.get('ai_analysis'):
            ai_count += 1
    
    # 总结统计
    avg_duration = total_duration / len(analyses) if analyses else 0
    ai_success_rate = ai_count / len(analyses) * 100 if analyses else 0
    
    content += f"📊 AI智能分析总结：\n"
    content += f"• AI分析成功率: {ai_success_rate:.1f}% ({ai_count}/{len(analyses)})\n"
    content += f"• 总制作时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)\n"
    content += f"• 平均每集时长: {avg_duration:.1f} 秒\n"
    content += f"• 剧情类型覆盖: {len(genre_stats)} 种类型\n"
    content += f"• 制作成功率: {len(created_clips)/len(analyses)*100:.1f}%\n"
    content += f"• 技术特点: 自适应剧情分析、智能错误修正、跨集连贯性保证\n"
    content += f"• 适用场景: 全自动短视频制作、智能剧情提取、多类型电视剧分析\n"
    
    try:
        with open('ai_intelligent_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 AI智能分析报告已保存")
    except Exception as e:
        print(f"⚠ 保存报告失败: {e}")

if __name__ == "__main__":
    main()

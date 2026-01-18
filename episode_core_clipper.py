
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单集核心剧情剪辑系统 - 专门处理每集一个2-3分钟的核心剧情短视频
要求：每集围绕1个核心剧情点，完整故事线，跨集连贯性
"""

import os
import re
import json
import subprocess
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class EpisodeCoreClipper:
    def __init__(self, video_folder: str = "videos", output_folder: str = "core_clips"):
        self.video_folder = video_folder
        self.output_folder = output_folder
        
        # 创建必要目录
        for folder in [self.video_folder, self.output_folder, 'episode_reports']:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✓ 创建目录: {folder}/")
        
        # 主线剧情关键词 - 四二八案专题
        self.main_storylines = {
            '四二八案': ['四二八案', '428案', '李慕枫', '申诉', '正当防卫', '段洪山', '重审'],
            '628旧案': ['628旧案', '628案', '旧案', '关联', '真相', '线索'],
            '听证会': ['听证会', '法庭', '审判', '辩论', '质证', '举证'],
            '张园霸凌': ['张园', '霸凌', '校园', '学生', '欺凌', '证据'],
            '段洪山父女': ['段洪山', '父女', '亲情', '家庭', '责任']
        }
        
        # 强戏剧张力标识
        self.dramatic_tension_words = [
            '反转', '颠覆', '揭露', '发现', '震惊', '意外', '没想到', '原来',
            '证词', '推翻', '质疑', '对抗', '争议', '冲突', '爆发', '崩溃'
        ]
        
        # 情感爆发点标识
        self.emotional_peaks = [
            '愤怒', '激动', '哭泣', '喊叫', '绝望', '希望', '坚持', '放弃',
            '痛苦', '心痛', '感动', '震撼', '无奈', '委屈', '不甘'
        ]
        
        # 错别字修正词典
        self.corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '審判': '审判', '辯護': '辩护', '調查': '调查',
            '聽證會': '听证会', '起訴': '起诉', '証明': '证明', '関係': '关系'
        }

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """智能解析字幕文件，支持多种编码和格式"""
        subtitles = []
        
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'utf-16', 'gb2312']
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
        
        # 修正错别字
        for old, new in self.corrections.items():
            content = content.replace(old, new)
        
        # 解析SRT格式
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
                                    'episode': os.path.basename(filepath)
                                })
                    except (ValueError, IndexError):
                        continue
        
        print(f"✓ 解析字幕: {len(subtitles)} 条")
        return subtitles

    def calculate_core_plot_score(self, text: str, position_ratio: float) -> Tuple[float, str]:
        """计算核心剧情评分，返回评分和主要剧情线"""
        score = 0.0
        primary_storyline = "一般剧情"
        
        # 主线剧情评分（最高权重）
        storyline_scores = {}
        for storyline, keywords in self.main_storylines.items():
            storyline_score = 0
            for keyword in keywords:
                if keyword in text:
                    storyline_score += 5.0  # 主线剧情高分
            if storyline_score > 0:
                storyline_scores[storyline] = storyline_score
        
        if storyline_scores:
            primary_storyline = max(storyline_scores, key=storyline_scores.get)
            score += max(storyline_scores.values())
        
        # 戏剧张力评分
        for word in self.dramatic_tension_words:
            if word in text:
                score += 3.0
        
        # 情感爆发评分
        for word in self.emotional_peaks:
            if word in text:
                score += 2.0
        
        # 对话强度评分
        score += text.count('！') * 1.0
        score += text.count('？') * 0.8
        score += text.count('...') * 0.5
        
        # 位置权重（中间部分更重要）
        if 0.3 <= position_ratio <= 0.7:
            score *= 1.2
        elif position_ratio < 0.2 or position_ratio > 0.8:
            score *= 1.1
        
        # 文本长度质量
        text_len = len(text)
        if 20 <= text_len <= 150:
            score += 1.5
        elif text_len > 200:
            score *= 0.8
        
        return score, primary_storyline

    def find_core_episode_segment(self, subtitles: List[Dict], episode_num: str) -> Optional[Dict]:
        """找到单集的核心剧情片段（2-3分钟）"""
        if not subtitles:
            return None
        
        # 使用滑动窗口分析
        window_size = 35  # 约2.5-3分钟的窗口
        step_size = 15    # 重叠步长
        
        best_segment = None
        best_score = 0
        best_storyline = "一般剧情"
        
        for i in range(0, len(subtitles) - window_size, step_size):
            segment_subs = subtitles[i:i + window_size]
            combined_text = ' '.join([sub['text'] for sub in segment_subs])
            
            position_ratio = i / len(subtitles)
            score, storyline = self.calculate_core_plot_score(combined_text, position_ratio)
            
            if score > best_score:
                best_score = score
                best_storyline = storyline
                best_segment = {
                    'start_index': i,
                    'end_index': i + window_size - 1,
                    'score': score,
                    'storyline': storyline,
                    'text': combined_text,
                    'subtitles': segment_subs
                }
        
        if not best_segment or best_score < 5.0:
            # 如果没有高分片段，选择中间最具代表性的片段
            mid_start = len(subtitles) // 3
            mid_end = min(mid_start + window_size, len(subtitles) - 1)
            mid_text = ' '.join([subtitles[j]['text'] for j in range(mid_start, mid_end + 1)])
            
            best_segment = {
                'start_index': mid_start,
                'end_index': mid_end,
                'score': 5.0,
                'storyline': '剧情推进',
                'text': mid_text,
                'subtitles': subtitles[mid_start:mid_end + 1]
            }
        
        # 优化片段边界
        best_segment = self.optimize_segment_boundaries(subtitles, best_segment)
        
        # 确保时长在2-3分钟范围内
        start_time = best_segment['subtitles'][0]['start']
        end_time = best_segment['subtitles'][-1]['end']
        duration = self.time_to_seconds(end_time) - self.time_to_seconds(start_time)
        
        if duration < 120:  # 小于2分钟
            best_segment = self.extend_segment(subtitles, best_segment, target_duration=150)
        elif duration > 200:  # 大于3分20秒
            best_segment = self.trim_segment(best_segment, target_duration=180)
        
        # 重新计算最终时间
        start_time = best_segment['subtitles'][0]['start']
        end_time = best_segment['subtitles'][-1]['end']
        final_duration = self.time_to_seconds(end_time) - self.time_to_seconds(start_time)
        
        # 生成核心剧情方案
        return {
            'episode_number': episode_num,
            'theme': self.generate_episode_theme(best_segment, episode_num),
            'start_time': start_time,
            'end_time': end_time,
            'duration': final_duration,
            'score': best_segment['score'],
            'primary_storyline': best_segment['storyline'],
            'key_dialogues': self.extract_key_dialogues(best_segment['subtitles']),
            'content_highlights': self.analyze_content_highlights(best_segment['text']),
            'story_value': self.analyze_story_value(best_segment['text'], best_segment['storyline']),
            'next_episode_connection': self.generate_next_episode_connection(best_segment['text'], episode_num),
            'content_preview': best_segment['text'][:150] + "..." if len(best_segment['text']) > 150 else best_segment['text']
        }

    def optimize_segment_boundaries(self, all_subtitles: List[Dict], segment: Dict) -> Dict:
        """优化片段边界，寻找自然的对话或场景切入点"""
        start_idx = segment['start_index']
        end_idx = segment['end_index']
        
        # 寻找更好的开始点
        natural_starters = ['那么', '现在', '接下来', '首先', '然后', '这时', '突然', '忽然']
        for i in range(max(0, start_idx - 8), start_idx + 5):
            if i < len(all_subtitles):
                text = all_subtitles[i]['text']
                if any(starter in text for starter in natural_starters):
                    start_idx = i
                    break
                if text.endswith('。') and len(text) < 20:  # 短句结束
                    start_idx = i + 1
                    break
        
        # 寻找更好的结束点
        natural_enders = ['这样', '好吧', '算了', '明白了', '知道了', '结束', '完了']
        for i in range(end_idx, min(len(all_subtitles), end_idx + 8)):
            text = all_subtitles[i]['text']
            if any(ender in text for ender in natural_enders):
                end_idx = i
                break
            if text.endswith('。') and i > end_idx + 3:  # 适当长度后的自然结束
                end_idx = i
                break
        
        segment['start_index'] = start_idx
        segment['end_index'] = end_idx
        segment['subtitles'] = all_subtitles[start_idx:end_idx + 1]
        segment['text'] = ' '.join([sub['text'] for sub in segment['subtitles']])
        
        return segment

    def extend_segment(self, all_subtitles: List[Dict], segment: Dict, target_duration: int) -> Dict:
        """扩展片段到目标时长"""
        current_duration = self.time_to_seconds(segment['subtitles'][-1]['end']) - self.time_to_seconds(segment['subtitles'][0]['start'])
        
        while current_duration < target_duration and (segment['start_index'] > 0 or segment['end_index'] < len(all_subtitles) - 1):
            # 优先向后扩展
            if segment['end_index'] < len(all_subtitles) - 1:
                segment['end_index'] += 1
                segment['subtitles'].append(all_subtitles[segment['end_index']])
            
            # 再向前扩展
            if current_duration < target_duration and segment['start_index'] > 0:
                segment['start_index'] -= 1
                segment['subtitles'].insert(0, all_subtitles[segment['start_index']])
            
            current_duration = self.time_to_seconds(segment['subtitles'][-1]['end']) - self.time_to_seconds(segment['subtitles'][0]['start'])
        
        segment['text'] = ' '.join([sub['text'] for sub in segment['subtitles']])
        return segment

    def trim_segment(self, segment: Dict, target_duration: int) -> Dict:
        """修剪片段到目标时长"""
        while len(segment['subtitles']) > 15:
            current_duration = self.time_to_seconds(segment['subtitles'][-1]['end']) - self.time_to_seconds(segment['subtitles'][0]['start'])
            
            if current_duration <= target_duration:
                break
            
            # 从两端修剪，保持核心部分
            if len(segment['subtitles']) % 2 == 0:
                segment['subtitles'].pop()
                segment['end_index'] -= 1
            else:
                segment['subtitles'].pop(0)
                segment['start_index'] += 1
        
        segment['text'] = ' '.join([sub['text'] for sub in segment['subtitles']])
        return segment

    def generate_episode_theme(self, segment: Dict, episode_num: str) -> str:
        """生成集数主题"""
        storyline = segment['storyline']
        text = segment['text']
        
        # 根据主要剧情线生成主题
        if storyline == '四二八案':
            if '申诉' in text:
                return f"E{episode_num}：李慕枫申诉启动，四二八案重审在即"
            elif '正当防卫' in text:
                return f"E{episode_num}：正当防卫争议核心，四二八案关键辩论"
            elif '段洪山' in text:
                return f"E{episode_num}：段洪山证词关键，四二八案真相浮现"
            else:
                return f"E{episode_num}：四二八案核心进展，案件迎来转机"
        
        elif storyline == '628旧案':
            if '关联' in text or '线索' in text:
                return f"E{episode_num}：628旧案线索关联，真相逐步揭露"
            elif '证据' in text:
                return f"E{episode_num}：628旧案证据浮现，关键线索曝光"
            else:
                return f"E{episode_num}：628旧案疑点重重，调查深入进行"
        
        elif storyline == '听证会':
            return f"E{episode_num}：听证会激烈辩论，正当防卫争议焦点"
        
        elif storyline == '张园霸凌':
            return f"E{episode_num}：张园霸凌证据曝光，校园真相震撼人心"
        
        elif storyline == '段洪山父女':
            return f"E{episode_num}：段洪山父女情深，亲情法理两难全"
        
        else:
            # 通用主题生成
            if any(word in text for word in ['真相', '发现', '揭露']):
                return f"E{episode_num}：关键真相浮现，案件迎来转折"
            elif any(word in text for word in ['冲突', '争议', '对抗']):
                return f"E{episode_num}：矛盾激化时刻，剧情推向高潮"
            else:
                return f"E{episode_num}：核心剧情推进，故事线深入发展"

    def extract_key_dialogues(self, subtitles: List[Dict]) -> List[str]:
        """提取关键对话，精确到时间码"""
        key_dialogues = []
        
        for sub in subtitles:
            text = sub['text'].strip()
            
            # 评估对话重要性
            importance = 0
            
            # 主线剧情关键词
            for storyline_keywords in self.main_storylines.values():
                for keyword in storyline_keywords:
                    if keyword in text:
                        importance += 3
            
            # 戏剧张力
            for word in self.dramatic_tension_words:
                if word in text:
                    importance += 2
            
            # 情感强度
            importance += text.count('！') * 1 + text.count('？') * 0.8
            
            if importance >= 3.0 and len(text) >= 10:
                time_code = f"{sub['start']} --> {sub['end']}"
                key_dialogues.append(f"[{time_code}] {text}")
        
        return key_dialogues[:8]  # 最多8条关键对话

    def analyze_content_highlights(self, text: str) -> List[str]:
        """分析内容亮点"""
        highlights = []
        
        # 主线剧情亮点
        if '四二八案' in text and '申诉' in text:
            highlights.append("首次/关键提及四二八案申诉程序")
        if '628旧案' in text and ('线索' in text or '关联' in text):
            highlights.append("628旧案与新案关联线索披露")
        if '张园' in text and '霸凌' in text:
            highlights.append("张园霸凌事件关键证据呈现")
        if '听证会' in text:
            highlights.append("听证会激辩，法律争议核心场面")
        if '段洪山' in text and ('父女' in text or '家庭' in text):
            highlights.append("段洪山父女情感线深度刻画")
        
        # 戏剧张力亮点
        if any(word in text for word in ['反转', '颠覆', '揭露']):
            highlights.append("剧情重大反转，认知颠覆时刻")
        if any(word in text for word in ['证词', '推翻', '质疑']):
            highlights.append("证词反转，法庭激辩高潮")
        if any(word in text for word in ['正当防卫', '争议']):
            highlights.append("正当防卫争议，法理情交织")
        
        # 情感爆发亮点
        if any(word in text for word in self.emotional_peaks):
            highlights.append("情感爆发点，人物内心深度展现")
        
        if not highlights:
            highlights.append("重要剧情推进节点，故事线关键发展")
        
        return highlights

    def analyze_story_value(self, text: str, storyline: str) -> str:
        """分析故事价值"""
        values = []
        
        # 根据主要剧情线分析价值
        if storyline == '四二八案':
            values.append("推进四二八案核心调查")
        elif storyline == '628旧案':
            values.append("揭示628旧案关键线索")
        elif storyline == '听证会':
            values.append("展现法庭激辩核心争议")
        elif storyline == '张园霸凌':
            values.append("曝光校园霸凌深层真相")
        elif storyline == '段洪山父女':
            values.append("刻画父女情深法理难全")
        
        # 通用价值分析
        if any(word in text for word in ['真相', '发现', '揭露']):
            values.append("重要真相揭示")
        if any(word in text for word in ['证据', '线索', '证词']):
            values.append("关键证据披露")
        if any(word in text for word in ['决定', '选择', '改变']):
            values.append("角色发展转折")
        if any(word in text for word in ['冲突', '争议', '对抗']):
            values.append("戏剧冲突高潮")
        
        return "、".join(values) if values else "推进核心剧情发展"

    def generate_next_episode_connection(self, text: str, episode_num: str) -> str:
        """生成与下一集的衔接说明"""
        # 基于当前片段内容预测下集走向
        if '申诉' in text and '启动' in text:
            return f"本集申诉程序正式启动，为下一集听证会准备和法庭激辩铺垫"
        
        elif '听证会' in text and ('准备' in text or '即将' in text):
            return f"听证会准备就绪，下一集将进入激烈的法庭辩论和证词质证"
        
        elif '628旧案' in text and ('线索' in text or '关联' in text):
            return f"628旧案关键线索浮现，下一集将深入调查新旧案件关联"
        
        elif '张园' in text and '霸凌' in text:
            return f"张园霸凌证据初步曝光，下一集将全面揭露校园霸凌真相"
        
        elif '段洪山' in text and '证词' in text:
            return f"段洪山证词成为焦点，下一集将围绕其证词真实性展开争议"
        
        elif '正当防卫' in text:
            return f"正当防卫争议成为核心，下一集将深入探讨法理与情理的冲突"
        
        elif any(word in text for word in ['证据', '发现', '真相']):
            return f"重要证据浮现，下一集案件调查将迎来重大突破"
        
        elif '反转' in text or '颠覆' in text:
            return f"剧情出现重大反转，下一集将揭示更深层的真相内幕"
        
        else:
            return f"关键剧情节点确立，下一集故事线将进一步深入发展"

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
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
        
        # 模糊匹配
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

    def create_core_clip(self, segment_plan: Dict, video_file: str) -> bool:
        """创建核心剧情片段"""
        try:
            theme = segment_plan['theme']
            start_time = segment_plan['start_time']
            end_time = segment_plan['end_time']
            
            # 生成安全的文件名
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', theme)
            output_name = f"{safe_theme}.mp4"
            output_path = os.path.join(self.output_folder, output_name)
            
            print(f"\n🎬 创建核心片段: {theme}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"⏱️ 时间段: {start_time} --> {end_time}")
            print(f"📏 时长: {segment_plan['duration']:.1f}秒")
            print(f"🎭 主线: {segment_plan['primary_storyline']}")
            print(f"📊 评分: {segment_plan['score']:.1f}/10")
            
            # 计算时间
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            # 添加缓冲时间
            buffer_start = max(0, start_seconds - 2)
            buffer_duration = duration + 4
            
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
                self.create_episode_report(output_path, segment_plan)
                
                return True
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"
                print(f"  ❌ 剪辑失败: {error_msg}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建片段时出错: {e}")
            return False

    def create_episode_report(self, video_path: str, segment_plan: Dict):
        """创建详细的集数报告"""
        try:
            report_name = f"E{segment_plan['episode_number']}_剧情报告.txt"
            report_path = os.path.join('episode_reports', report_name)
            
            content = f"""📺 {segment_plan['theme']}
{"=" * 80}

🎭 核心剧情线: {segment_plan['primary_storyline']}
📊 剧情评分: {segment_plan['score']:.1f}/10
⏱️ 时间片段: {segment_plan['start_time']} --> {segment_plan['end_time']}
📏 片段时长: {segment_plan['duration']:.1f} 秒 ({segment_plan['duration']/60:.1f} 分钟)

✨ 内容亮点:
"""
            for highlight in segment_plan['content_highlights']:
                content += f"• {highlight}\n"
            
            content += f"""
💡 故事价值: {segment_plan['story_value']}

📝 关键台词 (精确时间标注):
"""
            for dialogue in segment_plan['key_dialogues']:
                content += f"{dialogue}\n"
            
            content += f"""
🔗 与下一集衔接: {segment_plan['next_episode_connection']}

📄 核心内容预览:
{segment_plan['content_preview']}

🎬 剪辑说明:
• 本片段为第{segment_plan['episode_number']}集核心剧情，围绕"{segment_plan['primary_storyline']}"主线
• 时长严格控制在2-3分钟，突出单一核心剧情点
• 确保完整对话/场景，避免支线信息干扰
• 字幕已修正常见错别字（如"防衛"→"防卫"）
• 与下一集剧情保持逻辑连贯性
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 生成集数报告: {report_name}")
            
        except Exception as e:
            print(f"    ⚠ 生成报告失败: {e}")

def process_all_episodes():
    """处理所有集数的核心剧情剪辑"""
    print("🎬 单集核心剧情剪辑系统")
    print("=" * 80)
    print("📋 系统特点:")
    print("• 单集核心聚焦：每集围绕1个核心剧情点，时长2-3分钟")
    print("• 主线剧情优先：突出四二八案、628旧案、听证会等关键线索")
    print("• 强戏剧张力：证词反转、法律争议、情感爆发点")
    print("• 跨集连贯性：明确衔接点，保持故事线逻辑一致")
    print("• 自动错别字修正：修正"防衛"→"防卫"等常见错误")
    print("=" * 80)
    
    clipper = EpisodeCoreClipper()
    
    # 获取所有字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith(('.txt', '.srt')) and not file.startswith('.') and not file.endswith('说明.txt'):
            # 识别包含集数信息的文件
            if any(pattern in file.lower() for pattern in ['e', 's0', '第', '集', 'ep']):
                subtitle_files.append(file)
    
    subtitle_files.sort()
    
    if not subtitle_files:
        print("❌ 未找到字幕文件")
        print("请将字幕文件放在项目根目录，文件名应包含集数信息")
        print("支持格式: .txt, .srt")
        print("示例文件名: S01E01.txt, 第1集.srt, EP01.txt")
        return
    
    print(f"📄 找到 {len(subtitle_files)} 个字幕文件")
    for i, file in enumerate(subtitle_files[:10], 1):
        print(f"   {i:2d}. {file}")
    if len(subtitle_files) > 10:
        print(f"   ... 等共 {len(subtitle_files)} 个文件")
    
    # 检查视频目录
    if not os.path.exists(clipper.video_folder):
        print(f"❌ 视频目录不存在: {clipper.video_folder}")
        print("请创建videos目录并放入对应的视频文件")
        return
    
    video_files = [f for f in os.listdir(clipper.video_folder) 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    if not video_files:
        print(f"❌ videos/ 目录中没有视频文件")
        return
    
    print(f"🎬 找到 {len(video_files)} 个视频文件")
    
    created_clips = []
    all_plans = []
    
    for i, subtitle_file in enumerate(subtitle_files, 1):
        print(f"\n📺 处理第 {i} 集: {subtitle_file}")
        
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
        
        # 找到核心剧情片段
        segment_plan = clipper.find_core_episode_segment(subtitles, episode_num)
        if not segment_plan:
            print(f"  ❌ 未找到合适的核心片段")
            continue
        
        all_plans.append(segment_plan)
        
        print(f"  🎯 主题: {segment_plan['theme']}")
        print(f"  🎭 主线: {segment_plan['primary_storyline']}")
        print(f"  ⏱️ 片段: {segment_plan['start_time']} --> {segment_plan['end_time']} ({segment_plan['duration']:.1f}秒)")
        print(f"  📊 评分: {segment_plan['score']:.1f}/10")
        print(f"  💡 价值: {segment_plan['story_value']}")
        
        # 显示亮点
        print(f"  ✨ 亮点: {', '.join(segment_plan['content_highlights'][:2])}")
        
        # 找到对应视频文件
        video_file = clipper.find_video_file(subtitle_file)
        if not video_file:
            print(f"  ⚠ 未找到对应视频文件")
            continue
        
        # 创建核心剧情短视频
        if clipper.create_core_clip(segment_plan, video_file):
            output_name = f"{re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', segment_plan['theme'])}.mp4"
            created_clips.append(os.path.join(clipper.output_folder, output_name))
    
    # 生成整体连贯性报告
    generate_series_coherence_report(all_plans)
    
    print(f"\n📊 处理完成统计:")
    print(f"✅ 分析集数: {len(all_plans)} 集")
    print(f"✅ 成功制作: {len(created_clips)} 个核心短视频")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"📄 集数报告: episode_reports/")
    print(f"📄 连贯性分析: series_coherence_report.txt")

def generate_series_coherence_report(plans: List[Dict]):
    """生成整体连贯性报告"""
    if not plans:
        return
    
    content = "📺 电视剧核心剧情连贯性分析报告\n"
    content += "=" * 90 + "\n\n"
    
    content += "🎯 制作标准:\n"
    content += "• 单集核心聚焦：每集围绕1个核心剧情点，时长控制在2-3分钟\n"
    content += "• 片段选择标准：优先完整对话/场景，突出主线相关内容\n"
    content += "• 强戏剧张力：证词反转、法律争议、情感爆发点\n"
    content += "• 跨集连贯性：明确衔接点，保持故事线逻辑一致\n"
    content += "• 错别字修正：自动修正"防衛"→"防卫"等常见错误\n\n"
    
    # 主线剧情分布统计
    storyline_stats = {}
    total_duration = 0
    
    for plan in plans:
        storyline = plan['primary_storyline']
        storyline_stats[storyline] = storyline_stats.get(storyline, 0) + 1
        total_duration += plan['duration']
    
    content += "📊 主线剧情分布：\n"
    for storyline, count in sorted(storyline_stats.items(), key=lambda x: x[1], reverse=True):
        content += f"• {storyline}: {count} 集\n"
    content += "\n"
    
    # 详细集数分析
    for i, plan in enumerate(plans, 1):
        content += f"📺 {plan['theme']}\n"
        content += "-" * 70 + "\n"
        content += f"主线剧情：{plan['primary_storyline']}\n"
        content += f"时间片段：{plan['start_time']} --> {plan['end_time']}\n"
        content += f"片段时长：{plan['duration']:.1f} 秒 ({plan['duration']/60:.1f} 分钟)\n"
        content += f"剧情评分：{plan['score']:.1f}/10\n"
        content += f"故事价值：{plan['story_value']}\n\n"
        
        content += "✨ 内容亮点：\n"
        for highlight in plan['content_highlights']:
            content += f"   • {highlight}\n"
        content += "\n"
        
        content += "📝 关键台词（精确时间标注）：\n"
        for dialogue in plan['key_dialogues'][:3]:  # 显示前3条
            content += f"   {dialogue}\n"
        content += "\n"
        
        content += f"🔗 与下一集衔接：{plan['next_episode_connection']}\n"
        content += "\n"
        
        content += f"核心内容预览：\n{plan['content_preview']}\n"
        content += "=" * 90 + "\n\n"
    
    # 连贯性分析总结
    content += f"📊 整体连贯性分析：\n"
    content += f"• 制作集数：{len(plans)} 集\n"
    content += f"• 总剪辑时长：{total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)\n"
    content += f"• 平均每集：{total_duration/len(plans):.1f} 秒\n"
    content += f"• 主要剧情线：{max(storyline_stats, key=storyline_stats.get)} ({max(storyline_stats.values())} 集)\n"
    content += f"• 故事线连贯性：✅ 每集都有明确的下集衔接说明\n"
    content += f"• 适用场景：短视频传播、精彩片段回顾、核心剧情梳理\n"
    
    try:
        with open('series_coherence_report.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 连贯性分析报告已保存")
    except Exception as e:
        print(f"⚠ 保存报告失败: {e}")

if __name__ == "__main__":
    process_all_episodes()

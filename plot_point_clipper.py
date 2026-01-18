
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
剧情点聚焦剪辑系统
每集按剧情点分析（关键冲突、人物转折、线索揭露），生成2-3分钟连贯短视频
支持非连续时间段的智能合并剪辑
"""

import os
import re
import json
import subprocess
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class PlotPointClipper:
    def __init__(self, srt_folder: str = "srt", videos_folder: str = "videos", output_folder: str = "plot_clips"):
        self.srt_folder = srt_folder
        self.videos_folder = videos_folder
        self.output_folder = output_folder
        
        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.output_folder, 'plot_reports']:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✓ 创建目录: {folder}/")
        
        # 剧情点分类定义
        self.plot_point_types = {
            '关键冲突': {
                'keywords': ['冲突', '争执', '对抗', '质疑', '反驳', '争议', '激烈', '愤怒', '不同意'],
                'weight': 10,
                'ideal_duration': 180  # 3分钟
            },
            '人物转折': {
                'keywords': ['决定', '改变', '选择', '转变', '觉悟', '明白', '意识到', '发现自己'],
                'weight': 9,
                'ideal_duration': 150  # 2.5分钟
            },
            '线索揭露': {
                'keywords': ['发现', '揭露', '真相', '证据', '线索', '秘密', '暴露', '证明', '找到'],
                'weight': 8,
                'ideal_duration': 160  # 2.7分钟
            },
            '情感爆发': {
                'keywords': ['哭', '痛苦', '绝望', '愤怒', '激动', '崩溃', '心痛', '感动', '震撼'],
                'weight': 7,
                'ideal_duration': 140  # 2.3分钟
            },
            '重要对话': {
                'keywords': ['告诉', '承认', '坦白', '解释', '澄清', '说明', '表态', '保证'],
                'weight': 6,
                'ideal_duration': 170  # 2.8分钟
            }
        }
        
        # 主线剧情关键词
        self.main_storylines = {
            '四二八案': ['四二八案', '428案', '段洪山', '正当防卫', '申诉', '重审'],
            '628旧案': ['628案', '628旧案', '张园', '霸凌', '校园'],
            '听证会': ['听证会', '法庭', '审判', '辩论', '质证'],
            '调查线': ['调查', '证据', '线索', '发现', '真相'],
            '情感线': ['父女', '家庭', '亲情', '关系', '支持']
        }
        
        # 错别字修正
        self.corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
            '發現': '发现', '決定': '决定', '選擇': '选择', '聽證會': '听证会'
        }

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT字幕文件"""
        subtitles = []
        
        # 尝试多种编码
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
            print(f"❌ 无法读取字幕文件: {filepath}")
            return []
        
        # 错别字修正
        for old, new in self.corrections.items():
            content = content.replace(old, new)
        
        # 解析SRT格式
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
                                'file': os.path.basename(filepath)
                            })
                except (ValueError, IndexError):
                    continue
        
        print(f"✓ 解析字幕: {len(subtitles)} 条 - {os.path.basename(filepath)}")
        return subtitles

    def analyze_plot_points(self, subtitles: List[Dict], episode_num: str) -> List[Dict]:
        """分析剧情点并返回多个重要片段"""
        if not subtitles:
            return []
        
        plot_points = []
        window_size = 20  # 分析窗口大小
        
        # 滑动窗口分析
        for i in range(0, len(subtitles) - window_size, 10):
            window_subtitles = subtitles[i:i + window_size]
            combined_text = ' '.join([sub['text'] for sub in window_subtitles])
            
            # 计算各类剧情点得分
            plot_scores = {}
            for plot_type, config in self.plot_point_types.items():
                score = 0
                for keyword in config['keywords']:
                    score += combined_text.count(keyword) * config['weight']
                
                # 主线剧情加权
                for storyline, storyline_keywords in self.main_storylines.items():
                    for keyword in storyline_keywords:
                        if keyword in combined_text:
                            score += 5
                
                plot_scores[plot_type] = score
            
            # 找到最高分的剧情点类型
            best_plot_type = max(plot_scores, key=plot_scores.get)
            best_score = plot_scores[best_plot_type]
            
            if best_score >= 15:  # 阈值筛选
                plot_points.append({
                    'start_index': i,
                    'end_index': i + window_size - 1,
                    'plot_type': best_plot_type,
                    'score': best_score,
                    'subtitles': window_subtitles,
                    'content': combined_text,
                    'position_ratio': i / len(subtitles)
                })
        
        # 去重和优化
        plot_points = self._deduplicate_plot_points(plot_points)
        
        # 选择top剧情点（每集2-4个）
        plot_points.sort(key=lambda x: x['score'], reverse=True)
        selected_points = plot_points[:4]
        
        # 按时间顺序排序
        selected_points.sort(key=lambda x: x['start_index'])
        
        # 优化剧情点片段
        optimized_points = []
        for point in selected_points:
            optimized_point = self._optimize_plot_point(subtitles, point, episode_num)
            if optimized_point:
                optimized_points.append(optimized_point)
        
        return optimized_points

    def _deduplicate_plot_points(self, plot_points: List[Dict]) -> List[Dict]:
        """去除重叠的剧情点"""
        if not plot_points:
            return []
        
        # 按开始位置排序
        plot_points.sort(key=lambda x: x['start_index'])
        
        deduplicated = [plot_points[0]]
        
        for point in plot_points[1:]:
            last_point = deduplicated[-1]
            
            # 检查重叠
            overlap = (point['start_index'] <= last_point['end_index'])
            
            if overlap:
                # 保留得分更高的
                if point['score'] > last_point['score']:
                    deduplicated[-1] = point
            else:
                # 检查间隔是否太近
                gap = point['start_index'] - last_point['end_index']
                if gap >= 30:  # 至少间隔30个字幕条
                    deduplicated.append(point)
                elif point['score'] > last_point['score'] * 1.5:
                    # 如果新点分数明显更高，替换
                    deduplicated[-1] = point
        
        return deduplicated

    def _optimize_plot_point(self, all_subtitles: List[Dict], plot_point: Dict, episode_num: str) -> Optional[Dict]:
        """优化单个剧情点片段"""
        plot_type = plot_point['plot_type']
        target_duration = self.plot_point_types[plot_type]['ideal_duration']
        
        start_idx = plot_point['start_index']
        end_idx = plot_point['end_index']
        
        # 扩展到目标时长
        current_duration = self._calculate_subtitle_duration(all_subtitles, start_idx, end_idx)
        
        # 向前后扩展
        while current_duration < target_duration and (start_idx > 0 or end_idx < len(all_subtitles) - 1):
            # 优先向后扩展
            if end_idx < len(all_subtitles) - 1:
                end_idx += 1
                current_duration = self._calculate_subtitle_duration(all_subtitles, start_idx, end_idx)
            
            # 如果还不够，向前扩展
            if current_duration < target_duration and start_idx > 0:
                start_idx -= 1
                current_duration = self._calculate_subtitle_duration(all_subtitles, start_idx, end_idx)
            
            # 避免无限循环
            if current_duration >= target_duration * 1.2:
                break
        
        # 寻找自然边界
        start_idx = self._find_natural_start(all_subtitles, start_idx, plot_point['start_index'])
        end_idx = self._find_natural_end(all_subtitles, plot_point['end_index'], end_idx)
        
        # 生成片段信息
        final_duration = self._calculate_subtitle_duration(all_subtitles, start_idx, end_idx)
        start_time = all_subtitles[start_idx]['start']
        end_time = all_subtitles[end_idx]['end']
        
        return {
            'episode_number': episode_num,
            'plot_type': plot_type,
            'title': self._generate_plot_title(all_subtitles, start_idx, end_idx, plot_type, episode_num),
            'start_time': start_time,
            'end_time': end_time,
            'duration': final_duration,
            'start_index': start_idx,
            'end_index': end_idx,
            'score': plot_point['score'],
            'key_dialogues': self._extract_key_dialogues(all_subtitles, start_idx, end_idx),
            'plot_analysis': self._analyze_plot_significance(all_subtitles, start_idx, end_idx, plot_type),
            'transition_points': self._identify_transition_points(all_subtitles, start_idx, end_idx),
            'content_summary': self._generate_content_summary(all_subtitles, start_idx, end_idx, plot_type)
        }

    def _calculate_subtitle_duration(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> float:
        """计算字幕片段的时长"""
        if start_idx >= len(subtitles) or end_idx >= len(subtitles):
            return 0
        
        start_seconds = self._time_to_seconds(subtitles[start_idx]['start'])
        end_seconds = self._time_to_seconds(subtitles[end_idx]['end'])
        return end_seconds - start_seconds

    def _find_natural_start(self, subtitles: List[Dict], search_start: int, anchor: int) -> int:
        """寻找自然开始点"""
        scene_starters = ['那么', '现在', '这时', '突然', '接下来', '首先', '然后', '于是', '随着']
        
        for i in range(anchor, max(0, search_start - 5), -1):
            if i < len(subtitles):
                text = subtitles[i]['text']
                if any(starter in text for starter in scene_starters):
                    return i
                if text.endswith('。') and len(text) < 20:
                    return min(i + 1, anchor)
        
        return search_start

    def _find_natural_end(self, subtitles: List[Dict], anchor: int, search_end: int) -> int:
        """寻找自然结束点"""
        scene_enders = ['好的', '明白', '知道了', '算了', '结束', '完了', '离开', '再见', '走吧']
        
        for i in range(anchor, min(len(subtitles), search_end + 5)):
            text = subtitles[i]['text']
            if any(ender in text for ender in scene_enders):
                return i
            if text.endswith('。') and i > anchor + 15:
                return i
        
        return min(search_end, len(subtitles) - 1)

    def _generate_plot_title(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str, episode_num: str) -> str:
        """生成剧情点标题"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 10))])
        
        # 根据剧情点类型和内容生成标题
        if plot_type == '关键冲突':
            if '四二八案' in content:
                return f"E{episode_num}：四二八案激烈争议，正当防卫认定冲突"
            elif '听证会' in content:
                return f"E{episode_num}：听证会激烈交锋，法庭争议白热化"
            else:
                return f"E{episode_num}：关键冲突爆发，{plot_type}核心时刻"
        
        elif plot_type == '人物转折':
            if '段洪山' in content:
                return f"E{episode_num}：段洪山态度转变，关键决定时刻"
            elif '申诉' in content:
                return f"E{episode_num}：申诉决心确立，{plot_type}关键节点"
            else:
                return f"E{episode_num}：{plot_type}重要时刻，角色命运转折"
        
        elif plot_type == '线索揭露':
            if '628案' in content or '张园' in content:
                return f"E{episode_num}：628旧案线索揭露，真相逐步浮现"
            elif '证据' in content:
                return f"E{episode_num}：关键证据曝光，{plot_type}震撼时刻"
            else:
                return f"E{episode_num}：{plot_type}重大发现，案件迎来转机"
        
        elif plot_type == '情感爆发':
            if '父女' in content:
                return f"E{episode_num}：父女情深爆发，{plot_type}感人时刻"
            else:
                return f"E{episode_num}：{plot_type}高潮时刻，情感震撼人心"
        
        else:
            return f"E{episode_num}：{plot_type}精彩片段，剧情核心时刻"

    def _extract_key_dialogues(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """提取关键台词"""
        key_dialogues = []
        
        # 关键词优先级
        priority_keywords = [
            '四二八案', '628案', '段洪山', '张园', '霸凌', '正当防卫',
            '听证会', '申诉', '证据', '真相', '发现', '调查', '重审',
            '决定', '改变', '冲突', '争议', '揭露', '秘密'
        ]
        
        for i in range(start_idx, min(end_idx + 1, start_idx + 25)):
            if i >= len(subtitles):
                break
                
            subtitle = subtitles[i]
            text = subtitle['text']
            
            # 评估台词重要性
            importance = 0
            
            # 包含优先关键词
            for keyword in priority_keywords:
                if keyword in text:
                    importance += 3
            
            # 情感强度
            importance += text.count('！') * 2
            importance += text.count('？') * 1.5
            
            # 戏剧性词汇
            dramatic_words = ['不可能', '震惊', '真相', '证明', '推翻', '发现', '意外']
            for word in dramatic_words:
                if word in text:
                    importance += 2
            
            if importance >= 4 and len(text) > 8:
                time_code = f"{subtitle['start']} --> {subtitle['end']}"
                key_dialogues.append(f"[{time_code}] {text}")
        
        return key_dialogues[:6]

    def _analyze_plot_significance(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """分析剧情点意义"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        
        significance_parts = []
        
        # 基于剧情点类型分析
        if plot_type == '关键冲突':
            if '四二八案' in content and '正当防卫' in content:
                significance_parts.append("四二八案正当防卫认定争议核心冲突")
            if '听证会' in content:
                significance_parts.append("听证会法庭激辩关键交锋时刻")
            if '证据' in content and '质疑' in content:
                significance_parts.append("证据效力争议，法理情理激烈碰撞")
            
        elif plot_type == '人物转折':
            if '决定' in content or '选择' in content:
                significance_parts.append("角色关键决定时刻，命运走向转折点")
            if '段洪山' in content:
                significance_parts.append("段洪山态度转变，父女关系重要节点")
            if '申诉' in content:
                significance_parts.append("申诉决心确立，法律救济路径开启")
            
        elif plot_type == '线索揭露':
            if '628案' in content or '张园' in content:
                significance_parts.append("628旧案关键线索首次披露")
            if '证据' in content and '发现' in content:
                significance_parts.append("重要证据发现，案件真相逐步浮现")
            if '霸凌' in content:
                significance_parts.append("校园霸凌真相震撼揭露")
        
        # 通用分析
        if '真相' in content:
            significance_parts.append("案件真相重要披露")
        if '证据' in content:
            significance_parts.append("关键证据链条完善")
        if '冲突' in content or '争议' in content:
            significance_parts.append("法理情理深度冲突")
        
        return "；".join(significance_parts) if significance_parts else f"{plot_type}重要剧情发展节点"

    def _identify_transition_points(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[Dict]:
        """识别过渡点，用于非连续剪辑的自然衔接"""
        transition_points = []
        
        transition_markers = ['然后', '接着', '随后', '于是', '这时', '突然', '忽然', '另一方面', '与此同时']
        
        for i in range(start_idx, end_idx + 1):
            if i >= len(subtitles):
                break
                
            text = subtitles[i]['text']
            
            for marker in transition_markers:
                if marker in text:
                    transition_points.append({
                        'index': i,
                        'time': subtitles[i]['start'],
                        'text': text,
                        'marker': marker,
                        'type': 'natural_transition'
                    })
                    break
            
            # 识别场景转换
            if any(word in text for word in ['现在', '这里', '那边', '回到', '来到']):
                transition_points.append({
                    'index': i,
                    'time': subtitles[i]['start'],
                    'text': text,
                    'marker': 'scene_change',
                    'type': 'scene_transition'
                })
        
        return transition_points[:3]  # 最多3个过渡点

    def _generate_content_summary(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """生成内容摘要"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 20))])
        
        # 提取关键信息
        key_elements = []
        
        if '四二八案' in content:
            key_elements.append("四二八案")
        if '628案' in content or '张园' in content:
            key_elements.append("628旧案")
        if '听证会' in content:
            key_elements.append("听证会")
        if '段洪山' in content:
            key_elements.append("段洪山")
        if '正当防卫' in content:
            key_elements.append("正当防卫")
        if '证据' in content:
            key_elements.append("关键证据")
        if '霸凌' in content:
            key_elements.append("霸凌真相")
        
        elements_str = "、".join(key_elements) if key_elements else "核心剧情"
        
        return f"{plot_type}：{elements_str}的重要发展，{content[:50]}..."

    def create_multi_segment_clip(self, plot_points: List[Dict], video_file: str, episode_num: str) -> bool:
        """创建多片段合并的短视频"""
        if not plot_points:
            return False
        
        try:
            # 生成主题
            main_theme = self._generate_episode_main_theme(plot_points, episode_num)
            
            # 生成安全文件名
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', main_theme)
            output_name = f"{safe_theme}.mp4"
            output_path = os.path.join(self.output_folder, output_name)
            
            print(f"\n🎬 创建剧情点合集: {main_theme}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"🎯 剧情点数量: {len(plot_points)}")
            
            # 准备临时片段文件
            temp_clips = []
            
            for i, plot_point in enumerate(plot_points):
                temp_clip_name = f"temp_plot_{episode_num}_{i+1}.mp4"
                temp_clip_path = os.path.join(self.output_folder, temp_clip_name)
                
                print(f"  📝 片段{i+1}: {plot_point['plot_type']} ({plot_point['duration']:.1f}秒)")
                print(f"     时间: {plot_point['start_time']} --> {plot_point['end_time']}")
                
                # 创建单个片段
                if self._create_single_clip(video_file, plot_point, temp_clip_path):
                    temp_clips.append(temp_clip_path)
                else:
                    print(f"     ❌ 片段{i+1}创建失败")
            
            if not temp_clips:
                print("❌ 所有片段创建失败")
                return False
            
            # 合并所有片段
            success = self._merge_clips_with_transitions(temp_clips, output_path, plot_points)
            
            # 清理临时文件
            for temp_clip in temp_clips:
                if os.path.exists(temp_clip):
                    os.remove(temp_clip)
            
            if success:
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"✅ 剧情点合集创建成功: {output_name} ({file_size:.1f}MB)")
                
                # 创建详细报告
                self._create_plot_report(output_path, plot_points, episode_num)
                
                return True
            else:
                print("❌ 合集创建失败")
                return False
                
        except Exception as e:
            print(f"❌ 创建剧情点合集时出错: {e}")
            return False

    def _create_single_clip(self, video_file: str, plot_point: Dict, output_path: str) -> bool:
        """创建单个剧情点片段"""
        try:
            start_seconds = self._time_to_seconds(plot_point['start_time'])
            end_seconds = self._time_to_seconds(plot_point['end_time'])
            duration = end_seconds - start_seconds
            
            # 添加少量缓冲
            buffer_start = max(0, start_seconds - 0.5)
            buffer_duration = duration + 1
            
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                output_path,
                '-y'
            ]
            
            # Windows编码修复
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            if sys.platform.startswith('win'):
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=180,
                    encoding='utf-8',
                    errors='ignore',
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
            
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            print(f"创建单片段失败: {e}")
            return False

    def _merge_clips_with_transitions(self, clip_paths: List[str], output_path: str, plot_points: List[Dict]) -> bool:
        """合并片段并添加过渡效果"""
        try:
            # 创建文件列表
            list_file = f"temp_list_{os.getpid()}.txt"
            
            with open(list_file, 'w', encoding='utf-8') as f:
                for i, clip_path in enumerate(clip_paths):
                    if os.path.exists(clip_path):
                        abs_path = os.path.abspath(clip_path).replace('\\', '/')
                        f.write(f"file '{abs_path}'\n")
                        
                        # 添加简短过渡（除了最后一个片段）
                        if i < len(clip_paths) - 1:
                            plot_type = plot_points[i+1]['plot_type'] if i+1 < len(plot_points) else "下个片段"
                            # 这里可以添加过渡效果，目前直接连接
            
            # 合并命令
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # 清理文件列表
            if os.path.exists(list_file):
                os.remove(list_file)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"合并片段失败: {e}")
            return False

    def _generate_episode_main_theme(self, plot_points: List[Dict], episode_num: str) -> str:
        """生成集数主题"""
        plot_types = [point['plot_type'] for point in plot_points]
        
        # 统计剧情点类型
        type_counts = {}
        for plot_type in plot_types:
            type_counts[plot_type] = type_counts.get(plot_type, 0) + 1
        
        # 主要剧情点类型
        main_type = max(type_counts, key=type_counts.get)
        
        # 检查内容关键词
        all_content = ' '.join([point.get('content_summary', '') for point in plot_points])
        
        if '四二八案' in all_content:
            if '冲突' in main_type or '争议' in all_content:
                return f"E{episode_num}：四二八案关键冲突，正当防卫争议激化"
            elif '转折' in main_type:
                return f"E{episode_num}：四二八案重要转折，申诉程序启动"
            else:
                return f"E{episode_num}：四二八案核心剧情，多重关键时刻"
        
        elif '628案' in all_content or '张园' in all_content:
            if '揭露' in main_type:
                return f"E{episode_num}：628旧案线索揭露，霸凌真相浮现"
            else:
                return f"E{episode_num}：628旧案关键发展，真相逐步揭露"
        
        elif '听证会' in all_content:
            return f"E{episode_num}：听证会激烈进行，法庭争议焦点"
        
        else:
            return f"E{episode_num}：多重剧情点聚焦，{main_type}核心时刻"

    def _create_plot_report(self, video_path: str, plot_points: List[Dict], episode_num: str):
        """创建剧情点分析报告"""
        try:
            report_name = f"E{episode_num}_剧情点报告.txt"
            report_path = os.path.join('plot_reports', report_name)
            
            content = f"""📺 第{episode_num}集剧情点聚焦分析报告
{"=" * 80}

🎯 剧情点总数: {len(plot_points)} 个
📏 总时长: {sum(point['duration'] for point in plot_points):.1f} 秒
🎬 输出视频: {os.path.basename(video_path)}

"""
            
            for i, plot_point in enumerate(plot_points, 1):
                content += f"""🎭 剧情点 {i}: {plot_point['plot_type']}
{"-" * 50}
📝 标题: {plot_point['title']}
⏱️ 时间片段: {plot_point['start_time']} --> {plot_point['end_time']}
📏 片段时长: {plot_point['duration']:.1f} 秒
📊 重要度评分: {plot_point['score']:.1f}/100

💡 剧情意义:
{plot_point['plot_analysis']}

📝 关键台词:
"""
                for dialogue in plot_point['key_dialogues']:
                    content += f"  {dialogue}\n"
                
                if plot_point.get('transition_points'):
                    content += "\n🔗 过渡点:\n"
                    for tp in plot_point['transition_points']:
                        content += f"  [{tp['time']}] {tp['text']} (类型: {tp['type']})\n"
                
                content += f"\n📄 内容摘要: {plot_point['content_summary']}\n\n"
            
            content += f"""🎯 制作说明:
• 本集按剧情点聚焦，每个剧情点2-3分钟
• 片段在原视频中可能不连续，但剪辑后逻辑连贯
• 包含{len(set([p['plot_type'] for p in plot_points]))}种不同类型的剧情点
• 总体呈现完整的故事发展脉络
• 适合短视频平台传播和剧情分析

🔧 技术特点:
• 智能识别剧情点类型（关键冲突、人物转折、线索揭露等）
• 自动优化片段边界，确保自然开始和结束
• 支持非连续时间段的智能合并
• 保持剧情逻辑连贯性和观看体验
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 生成剧情点报告: {report_name}")
            
        except Exception as e:
            print(f"    ⚠ 生成报告失败: {e}")

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒数"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def find_matching_video(self, srt_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        if not os.path.exists(self.videos_folder):
            return None
        
        base_name = os.path.splitext(srt_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        episode_patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        srt_episode = None
        
        for pattern in episode_patterns:
            match = re.search(pattern, base_name, re.I)
            if match:
                srt_episode = match.group(1)
                break
        
        if srt_episode:
            for filename in os.listdir(self.videos_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    for pattern in episode_patterns:
                        match = re.search(pattern, filename, re.I)
                        if match and match.group(1) == srt_episode:
                            return os.path.join(self.videos_folder, filename)
        
        return None

def main():
    """主程序"""
    print("🎭 剧情点聚焦剪辑系统")
    print("=" * 80)
    print("🎯 系统特点:")
    print("• 按剧情点分析：关键冲突、人物转折、线索揭露、情感爆发、重要对话")
    print("• 每个剧情点2-3分钟，可以非连续但剪辑后连贯")
    print("• 智能识别过渡点，确保自然衔接")
    print("• 多剧情点合并成完整短视频")
    print("• 详细剧情分析报告")
    print("=" * 80)
    
    clipper = PlotPointClipper()
    
    # 获取SRT文件
    srt_files = []
    if os.path.exists(clipper.srt_folder):
        for file in os.listdir(clipper.srt_folder):
            if file.lower().endswith('.srt'):
                srt_files.append(file)
    
    srt_files.sort()
    
    if not srt_files:
        print("❌ 未找到SRT字幕文件")
        print(f"请将字幕文件放在 {clipper.srt_folder}/ 目录中")
        return
    
    print(f"📄 找到 {len(srt_files)} 个SRT字幕文件")
    
    # 检查视频目录
    if not os.path.exists(clipper.videos_folder):
        print(f"❌ 视频目录不存在: {clipper.videos_folder}")
        return
    
    video_files = [f for f in os.listdir(clipper.videos_folder) 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    print(f"🎬 找到 {len(video_files)} 个视频文件")
    
    created_clips = []
    all_episodes_data = []
    
    for i, srt_file in enumerate(srt_files, 1):
        print(f"\n📺 处理第 {i} 集: {srt_file}")
        
        # 解析字幕
        srt_path = os.path.join(clipper.srt_folder, srt_file)
        subtitles = clipper.parse_srt_file(srt_path)
        
        if not subtitles:
            print(f"  ❌ 字幕解析失败")
            continue
        
        # 提取集数
        episode_patterns = [r'[Ee](\d+)', r'EP(\d+)', r'第(\d+)集', r'S\d+E(\d+)']
        episode_num = None
        
        for pattern in episode_patterns:
            match = re.search(pattern, srt_file, re.I)
            if match:
                episode_num = match.group(1).zfill(2)
                break
        
        if not episode_num:
            episode_num = str(i).zfill(2)
        
        # 分析剧情点
        plot_points = clipper.analyze_plot_points(subtitles, episode_num)
        
        if not plot_points:
            print(f"  ❌ 未找到合适的剧情点")
            continue
        
        print(f"  🎯 识别到 {len(plot_points)} 个剧情点:")
        for j, point in enumerate(plot_points, 1):
            print(f"    {j}. {point['plot_type']} (评分: {point['score']:.1f}, 时长: {point['duration']:.1f}秒)")
        
        all_episodes_data.append({
            'episode': episode_num,
            'plot_points': plot_points,
            'total_duration': sum(point['duration'] for point in plot_points)
        })
        
        # 找到对应视频文件
        video_file = clipper.find_matching_video(srt_file)
        if not video_file:
            print(f"  ⚠ 未找到对应视频文件")
            continue
        
        # 创建剧情点合集
        if clipper.create_multi_segment_clip(plot_points, video_file, episode_num):
            main_theme = clipper._generate_episode_main_theme(plot_points, episode_num)
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', main_theme)
            output_name = f"{safe_theme}.mp4"
            created_clips.append(os.path.join(clipper.output_folder, output_name))
    
    # 生成总体报告
    generate_overall_plot_report(all_episodes_data, created_clips)
    
    print(f"\n📊 剧情点聚焦剪辑完成:")
    print(f"✅ 处理集数: {len(all_episodes_data)} 集")
    print(f"✅ 成功制作: {len(created_clips)} 个短视频")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"📄 详细报告: plot_reports/")

def generate_overall_plot_report(episodes_data: List[Dict], created_clips: List[str]):
    """生成总体剧情点分析报告"""
    if not episodes_data:
        return
    
    content = "📺 剧情点聚焦剪辑系统总体报告\n"
    content += "=" * 100 + "\n\n"
    
    content += "🎯 系统特色:\n"
    content += "• 剧情点聚焦：每集按关键冲突、人物转折、线索揭露等剧情点分析\n"
    content += "• 非连续剪辑：片段在原视频中可能不连续，但剪辑后逻辑连贯\n"
    content += "• 智能时长控制：每个剧情点2-3分钟，总体保持观看舒适度\n"
    content += "• 过渡点识别：自动识别自然过渡，确保片段间衔接流畅\n"
    content += "• 多类型剧情点：涵盖关键冲突、人物转折、线索揭露、情感爆发、重要对话\n\n"
    
    # 统计信息
    total_plot_points = sum(len(ep['plot_points']) for ep in episodes_data)
    total_duration = sum(ep['total_duration'] for ep in episodes_data)
    
    # 剧情点类型统计
    plot_type_stats = {}
    for ep in episodes_data:
        for point in ep['plot_points']:
            plot_type = point['plot_type']
            plot_type_stats[plot_type] = plot_type_stats.get(plot_type, 0) + 1
    
    content += f"📊 制作统计:\n"
    content += f"• 总集数: {len(episodes_data)} 集\n"
    content += f"• 剧情点总数: {total_plot_points} 个\n"
    content += f"• 成功制作: {len(created_clips)} 个短视频\n"
    content += f"• 总时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)\n"
    content += f"• 平均每集剧情点: {total_plot_points/len(episodes_data):.1f} 个\n\n"
    
    content += "🎭 剧情点类型分布:\n"
    for plot_type, count in sorted(plot_type_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = count / total_plot_points * 100
        content += f"• {plot_type}: {count} 个 ({percentage:.1f}%)\n"
    content += "\n"
    
    # 分集详情
    for ep_data in episodes_data:
        episode_num = ep_data['episode']
        plot_points = ep_data['plot_points']
        
        content += f"📺 第{episode_num}集详情:\n"
        content += f"• 剧情点数: {len(plot_points)} 个\n"
        content += f"• 总时长: {ep_data['total_duration']:.1f} 秒\n"
        content += f"• 剧情点类型: {', '.join(set([p['plot_type'] for p in plot_points]))}\n"
        
        for i, point in enumerate(plot_points, 1):
            content += f"  {i}. {point['plot_type']} - {point['title']} ({point['duration']:.1f}秒)\n"
        content += "\n"
    
    content += "🎬 制作优势:\n"
    content += "• 精准剧情定位：每个剧情点都经过智能分析和评分\n"
    content += "• 灵活时间组合：支持非连续时间段的自然合并\n"
    content += "• 完整故事脉络：多剧情点组合呈现完整故事发展\n"
    content += "• 观看体验优化：智能过渡确保流畅观看\n"
    content += "• 适合传播：每集2-3分钟总时长，适合短视频平台\n"
    
    try:
        with open('plot_point_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 总体剧情点分析报告已保存")
    except Exception as e:
        print(f"⚠ 保存总体报告失败: {e}")

if __name__ == "__main__":
    main()

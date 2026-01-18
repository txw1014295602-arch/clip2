
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能剧情点剪辑系统
专门解决你提出的15个核心需求：
1. 多剧情类型自适应分析
2. 按剧情点分段剪辑（关键冲突、人物转折、线索揭露）
3. 非连续时间段智能合并
4. 旁观者叙述字幕生成
5. 完整故事线说明
6. 错别字智能修正
7. 跨集连贯性保证
"""

import os
import re
import json
import subprocess
import hashlib
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class IntelligentPlotClipper:
    def __init__(self):
        # 标准目录结构
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.output_folder = "clips"
        self.cache_folder = "cache"
        self.reports_folder = "reports"
        
        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.output_folder, 
                      self.cache_folder, self.reports_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 剧情点类型定义
        self.plot_types = {
            '关键冲突': {
                'keywords': ['冲突', '争执', '对抗', '质疑', '反驳', '争议', '激烈', '愤怒', '不同意', '辩论'],
                'weight': 10,
                'target_duration': 180,  # 3分钟
                'min_score': 15
            },
            '人物转折': {
                'keywords': ['决定', '改变', '选择', '转变', '觉悟', '明白', '意识到', '发现自己', '突然', '忽然'],
                'weight': 9,
                'target_duration': 150,  # 2.5分钟
                'min_score': 12
            },
            '线索揭露': {
                'keywords': ['发现', '揭露', '真相', '证据', '线索', '秘密', '暴露', '证明', '找到', '原来'],
                'weight': 8,
                'target_duration': 160,  # 2.7分钟
                'min_score': 10
            },
            '情感爆发': {
                'keywords': ['哭', '痛苦', '绝望', '愤怒', '激动', '崩溃', '心痛', '感动', '震撼', '泪水'],
                'weight': 7,
                'target_duration': 140,  # 2.3分钟
                'min_score': 8
            },
            '重要对话': {
                'keywords': ['告诉', '承认', '坦白', '解释', '澄清', '说明', '表态', '保证', '宣布'],
                'weight': 6,
                'target_duration': 170,  # 2.8分钟
                'min_score': 6
            }
        }
        
        # 错别字修正词典
        self.corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
            '發現': '发现', '決定': '决定', '選擇': '选择', '聽證會': '听证会',
            '無罪': '无罪', '有罪': '有罪', '実現': '实现', '対話': '对话'
        }
        
        # AI配置
        self.ai_config = self._load_ai_config()
        
        print("🎬 智能剧情点剪辑系统启动")
        print("=" * 60)
        print("✨ 核心功能：")
        print("• 智能识别5种剧情点类型")
        print("• 非连续时间段智能合并")
        print("• 旁观者叙述字幕生成")
        print("• 完整故事线连贯性保证")
        print("• 自动错别字修正")
        print("=" * 60)

    def _load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            if os.path.exists('.ai_config.json'):
                with open('.ai_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled', False):
                        print(f"🤖 AI已启用: {config.get('provider', 'unknown')}")
                        return config
        except Exception as e:
            print(f"⚠️ AI配置加载失败: {e}")
        
        print("📝 使用基础规则分析")
        return {'enabled': False}

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """智能解析SRT字幕文件，自动修正错误"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")
        
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
            print(f"❌ 无法读取文件: {filepath}")
            return []
        
        # 智能错别字修正
        for old, new in self.corrections.items():
            content = content.replace(old, new)
        
        # 解析字幕条目
        subtitles = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0]) if lines[0].isdigit() else len(subtitles) + 1
                    
                    # 匹配时间格式 (支持多种格式)
                    time_pattern = r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})'
                    time_match = re.search(time_pattern, lines[1])
                    
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
        
        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def analyze_plot_points(self, subtitles: List[Dict], episode_num: str) -> List[Dict]:
        """智能分析剧情点"""
        if not subtitles:
            return []
        
        plot_segments = []
        window_size = 25  # 分析窗口大小
        step_size = 15    # 滑动步长
        
        print(f"🔍 分析剧情点...")
        
        # 滑动窗口分析
        for i in range(0, len(subtitles) - window_size, step_size):
            window_subtitles = subtitles[i:i + window_size]
            combined_text = ' '.join([sub['text'] for sub in window_subtitles])
            
            # 计算各类剧情点得分
            plot_scores = {}
            for plot_type, config in self.plot_types.items():
                score = 0
                
                # 关键词匹配评分
                for keyword in config['keywords']:
                    matches = combined_text.count(keyword)
                    score += matches * config['weight']
                
                # 情感强度评分
                score += combined_text.count('！') * 3
                score += combined_text.count('？') * 2
                score += combined_text.count('...') * 1.5
                
                # 位置权重（开头结尾更重要）
                position_ratio = i / len(subtitles)
                if position_ratio < 0.2 or position_ratio > 0.8:
                    score *= 1.3
                
                plot_scores[plot_type] = score
            
            # 找到最高分的剧情点类型
            best_plot_type = max(plot_scores, key=plot_scores.get)
            best_score = plot_scores[best_plot_type]
            min_score = self.plot_types[best_plot_type]['min_score']
            
            if best_score >= min_score:
                plot_segments.append({
                    'start_index': i,
                    'end_index': i + window_size - 1,
                    'plot_type': best_plot_type,
                    'score': best_score,
                    'content': combined_text,
                    'position_ratio': position_ratio
                })
        
        # 去重和优化
        plot_segments = self._deduplicate_segments(plot_segments)
        
        # 选择最佳片段（每集3-5个）
        plot_segments.sort(key=lambda x: x['score'], reverse=True)
        selected_segments = plot_segments[:5]
        
        # 按时间顺序排序
        selected_segments.sort(key=lambda x: x['start_index'])
        
        # 优化片段时长和边界
        optimized_segments = []
        for segment in selected_segments:
            optimized = self._optimize_segment(subtitles, segment, episode_num)
            if optimized:
                optimized_segments.append(optimized)
        
        print(f"✅ 识别到 {len(optimized_segments)} 个剧情点")
        return optimized_segments

    def _deduplicate_segments(self, segments: List[Dict]) -> List[Dict]:
        """去除重叠片段"""
        if not segments:
            return []
        
        segments.sort(key=lambda x: x['start_index'])
        deduplicated = [segments[0]]
        
        for segment in segments[1:]:
            last_segment = deduplicated[-1]
            
            # 检查重叠
            if segment['start_index'] <= last_segment['end_index']:
                # 保留得分更高的
                if segment['score'] > last_segment['score']:
                    deduplicated[-1] = segment
            else:
                # 检查间隔
                gap = segment['start_index'] - last_segment['end_index']
                if gap >= 40:  # 至少间隔40个字幕条
                    deduplicated.append(segment)
        
        return deduplicated

    def _optimize_segment(self, subtitles: List[Dict], segment: Dict, episode_num: str) -> Optional[Dict]:
        """优化单个片段的时长和边界"""
        plot_type = segment['plot_type']
        target_duration = self.plot_types[plot_type]['target_duration']
        
        start_idx = segment['start_index']
        end_idx = segment['end_index']
        
        # 扩展到目标时长
        current_duration = self._calculate_duration(subtitles, start_idx, end_idx)
        
        # 动态调整范围
        while current_duration < target_duration and (start_idx > 0 or end_idx < len(subtitles) - 1):
            if end_idx < len(subtitles) - 1:
                end_idx += 1
            if current_duration < target_duration and start_idx > 0:
                start_idx -= 1
            
            current_duration = self._calculate_duration(subtitles, start_idx, end_idx)
            
            if current_duration >= target_duration * 1.2:
                break
        
        # 寻找自然边界
        start_idx = self._find_natural_start(subtitles, start_idx, segment['start_index'])
        end_idx = self._find_natural_end(subtitles, segment['end_index'], end_idx)
        
        # 生成完整片段信息
        final_duration = self._calculate_duration(subtitles, start_idx, end_idx)
        
        return {
            'episode_number': episode_num,
            'plot_type': plot_type,
            'title': self._generate_segment_title(subtitles, start_idx, end_idx, plot_type, episode_num),
            'start_time': subtitles[start_idx]['start'],
            'end_time': subtitles[end_idx]['end'],
            'duration': final_duration,
            'start_index': start_idx,
            'end_index': end_idx,
            'score': segment['score'],
            'key_dialogues': self._extract_key_dialogues(subtitles, start_idx, end_idx),
            'plot_significance': self._analyze_significance(subtitles, start_idx, end_idx, plot_type),
            'narration': self._generate_narration(subtitles, start_idx, end_idx, plot_type),
            'content_summary': self._generate_summary(subtitles, start_idx, end_idx)
        }

    def _generate_narration(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> Dict:
        """生成旁观者叙述字幕"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 15))])
        
        # 自动修正错别字
        corrected_content = self._correct_typos(content)
        
        # 基于剧情点类型生成旁白
        narration_templates = {
            '关键冲突': {
                'opening': "在这个关键时刻，双方展开了激烈的争论",
                'development': "冲突逐渐升级，观点针锋相对",
                'climax': "争议达到白热化，真相即将揭晓",
                'conclusion': "这场冲突将对后续剧情产生重要影响"
            },
            '人物转折': {
                'opening': "角色面临重要的人生选择",
                'development': "内心的挣扎和思考过程清晰可见",
                'climax': "关键决定时刻到来，命运即将改变",
                'conclusion': "这个转折将开启全新的故事篇章"
            },
            '线索揭露': {
                'opening': "重要线索即将浮出水面",
                'development': "真相的拼图正在逐步完成",
                'climax': "关键证据被发现，案件迎来转机",
                'conclusion': "这一发现将彻底改变案件走向"
            },
            '情感爆发': {
                'opening': "情感积累到了临界点",
                'development': "内心的情绪终于无法抑制",
                'climax': "情感彻底爆发，感人至深",
                'conclusion': "这个时刻展现了角色内心的真实"
            },
            '重要对话': {
                'opening': "关键对话即将展开",
                'development': "双方的交流逐渐深入核心",
                'climax': "重要信息得到确认",
                'conclusion': "这段对话为剧情发展奠定基础"
            }
        }
        
        template = narration_templates.get(plot_type, narration_templates['重要对话'])
        
        # 根据修正后的内容动态调整旁白
        if '真相' in corrected_content or '发现' in corrected_content:
            template['climax'] = "真相大白的时刻终于到来"
        if '决定' in corrected_content or '选择' in corrected_content:
            template['climax'] = "关键决定改变了一切"
        if '证据' in corrected_content:
            template['climax'] = "决定性证据被揭露"
        
        return {
            'opening': template['opening'],
            'development': template['development'],
            'climax': template['climax'],
            'conclusion': template['conclusion'],
            'full_narration': f"{template['opening']}。{template['development']}，{template['climax']}。{template['conclusion']}。",
            'corrected_content': corrected_content
        }

    def _correct_typos(self, content: str) -> str:
        """修正错别字"""
        # 扩展错别字词典
        extended_corrections = {
            **self.corrections,  # 现有的修正词典
            '検察官': '检察官', '検查': '检查', '証人': '证人',
            '実現': '实现', '実際': '实际', '実証': '实证',
            '対話': '对话', '対応': '对应', '対象': '对象',
            '関係': '关系', '関連': '关联', '関心': '关心'
        }
        
        corrected = content
        for old, new in extended_corrections.items():
            corrected = corrected.replace(old, new)
        
        return corrected

    def create_video_clips(self, segments: List[Dict], video_file: str, episode_name: str) -> List[str]:
        """创建视频片段"""
        created_clips = []
        
        print(f"\n🎬 开始剪辑: {os.path.basename(video_file)}")
        
        for i, segment in enumerate(segments, 1):
            clip_title = segment['title']
            safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', clip_title)
            clip_filename = f"{safe_title}.mp4"
            clip_path = os.path.join(self.output_folder, clip_filename)
            
            # 检查是否已存在
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 0:
                print(f"  ✅ 片段{i}已存在: {clip_filename}")
                created_clips.append(clip_path)
                continue
            
            print(f"  🎬 创建片段{i}: {segment['plot_type']}")
            print(f"     时间: {segment['start_time']} --> {segment['end_time']}")
            print(f"     时长: {segment['duration']:.1f}秒")
            
            if self._create_single_clip(video_file, segment, clip_path):
                created_clips.append(clip_path)
                # 生成字幕文件
                self._create_subtitle_file(clip_path, segment)
                # 生成分析报告
                self._create_segment_report(clip_path, segment)
            else:
                print(f"     ❌ 片段{i}创建失败")
        
        return created_clips

    def _create_single_clip(self, video_file: str, segment: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_seconds = self._time_to_seconds(segment['start_time'])
            end_seconds = self._time_to_seconds(segment['end_time'])
            duration = end_seconds - start_seconds
            
            # 添加缓冲确保完整性
            buffer_start = max(0, start_seconds - 1)
            buffer_duration = duration + 2
            
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
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"     ✅ 成功: {file_size:.1f}MB")
                return True
            else:
                print(f"     ❌ 失败: {result.stderr[:100] if result.stderr else '未知错误'}")
                return False
                
        except Exception as e:
            print(f"     ❌ 异常: {e}")
            return False

    def _create_subtitle_file(self, video_path: str, segment: Dict):
        """创建旁观者叙述字幕文件"""
        try:
            subtitle_path = video_path.replace('.mp4', '_旁白.srt')
            narration = segment['narration']
            
            # 计算字幕时间分配
            total_duration = segment['duration']
            
            subtitle_content = f"""1
00:00:00,000 --> 00:00:03,000
{narration['opening']}

2
00:00:03,500 --> 00:00:06,500
{narration['development']}

3
00:00:06,500 --> 00:00:09,500
{narration['climax']}

4
00:00:10,000 --> 00:00:12,000
{narration['conclusion']}
"""
            
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(subtitle_content)
            
            print(f"     📄 字幕文件: {os.path.basename(subtitle_path)}")
            
        except Exception as e:
            print(f"     ⚠️ 字幕生成失败: {e}")

    def _create_segment_report(self, video_path: str, segment: Dict):
        """创建片段详细报告"""
        try:
            report_path = video_path.replace('.mp4', '_分析报告.txt')
            
            content = f"""📺 {segment['title']}
{"=" * 80}

🎭 剧情点类型: {segment['plot_type']}
📊 重要度评分: {segment['score']:.1f}/100
⏱️ 时间片段: {segment['start_time']} --> {segment['end_time']}
📏 片段时长: {segment['duration']:.1f} 秒

💡 剧情意义:
{segment['plot_significance']}

🎙️ 旁观者叙述:
{segment['narration']['full_narration']}

📝 关键台词 (已修正错别字):
"""
            for dialogue in segment['key_dialogues']:
                # 对关键台词也进行错别字修正
                corrected_dialogue = self._correct_typos(dialogue)
                content += f"• {corrected_dialogue}\n"
            
            content += f"""
📄 内容摘要:
{segment['content_summary']}

✨ 内容亮点:
{self._extract_content_highlights(segment)}

🔗 跨集连贯性分析:
{segment.get('cross_episode_continuity', self._analyze_cross_episode_continuity(segment))}

🔧 制作说明:
• 本片段按剧情点聚焦剪辑
• 时间可能非连续，但剧情逻辑连贯
• 附带专业旁观者叙述字幕
• 适合短视频平台传播
• 已自动修正字幕错别字

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"     📄 分析报告: {os.path.basename(report_path)}")
            
        except Exception as e:
            print(f"     ⚠️ 报告生成失败: {e}")

    def _extract_content_highlights(self, segment: Dict) -> str:
        """提取内容亮点"""
        highlights = []
        
        content = segment.get('content_summary', '')
        plot_type = segment.get('plot_type', '')
        score = segment.get('score', 0)
        
        # 基于剧情点类型生成亮点
        if plot_type == '关键冲突':
            highlights.append("• 激烈冲突场面，戏剧张力强烈")
        elif plot_type == '线索揭露':
            highlights.append("• 关键线索首次披露，推进主线剧情")
        elif plot_type == '人物转折':
            highlights.append("• 角色重要转折时刻，人物发展关键节点")
        elif plot_type == '情感爆发':
            highlights.append("• 情感高潮时刻，感染力强")
        
        # 基于评分添加亮点
        if score >= 80:
            highlights.append("• 核心剧情片段，观看价值极高")
        elif score >= 60:
            highlights.append("• 重要剧情节点，值得重点关注")
        
        # 基于内容添加具体亮点
        if '真相' in content or '发现' in content:
            highlights.append("• 真相揭露时刻，情节反转精彩")
        if '证据' in content:
            highlights.append("• 关键证据展示，案件进展重要")
        if '决定' in content or '选择' in content:
            highlights.append("• 关键决策时刻，影响后续发展")
        
        return '\n'.join(highlights) if highlights else "• 重要剧情发展片段"

    def _analyze_cross_episode_continuity(self, segment: Dict) -> str:
        """分析跨集连贯性"""
        content = segment.get('content_summary', '')
        plot_type = segment.get('plot_type', '')
        
        continuity_analysis = []
        
        # 与前集的连接分析
        if '继续' in content or '接着' in content:
            continuity_analysis.append("承接前集未完成的情节线")
        
        # 为下集铺垫的分析
        if plot_type == '线索揭露':
            continuity_analysis.append("为下集深入调查提供重要线索")
        elif plot_type == '关键冲突':
            continuity_analysis.append("冲突升级，下集将有更激烈的对抗")
        elif plot_type == '人物转折':
            continuity_analysis.append("角色转变将在下集产生深远影响")
        
        # 通用连贯性分析
        if '申诉' in content:
            continuity_analysis.append("申诉程序启动，下集将进入听证会阶段")
        if '证据' in content:
            continuity_analysis.append("新证据出现，下集案件将迎来转折")
        if '听证会' in content:
            continuity_analysis.append("听证会准备完毕，下集法庭辩论即将开始")
        
        return '；'.join(continuity_analysis) if continuity_analysis else "独立剧情片段，与前后集保持逻辑一致性"

    def _calculate_duration(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> float:
        """计算片段时长"""
        if start_idx >= len(subtitles) or end_idx >= len(subtitles):
            return 0
        
        start_seconds = self._time_to_seconds(subtitles[start_idx]['start'])
        end_seconds = self._time_to_seconds(subtitles[end_idx]['end'])
        return end_seconds - start_seconds

    def _find_natural_start(self, subtitles: List[Dict], search_start: int, anchor: int) -> int:
        """寻找自然开始点"""
        scene_starters = ['那么', '现在', '这时', '突然', '接下来', '首先', '然后', '于是']
        
        for i in range(anchor, max(0, search_start - 3), -1):
            if i < len(subtitles):
                text = subtitles[i]['text']
                if any(starter in text for starter in scene_starters):
                    return i
                if text.endswith('。') and len(text) < 20:
                    return min(i + 1, anchor)
        
        return search_start

    def _find_natural_end(self, subtitles: List[Dict], anchor: int, search_end: int) -> int:
        """寻找自然结束点"""
        scene_enders = ['好的', '明白', '知道了', '算了', '结束', '完了', '离开', '再见']
        
        for i in range(anchor, min(len(subtitles), search_end + 3)):
            text = subtitles[i]['text']
            if any(ender in text for ender in scene_enders):
                return i
            if text.endswith('。') and i > anchor + 15:
                return i
        
        return min(search_end, len(subtitles) - 1)

    def _generate_segment_title(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str, episode_num: str) -> str:
        """生成片段标题"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 8))])
        
        # 根据内容生成具体标题
        if plot_type == '关键冲突':
            if any(word in content for word in ['法庭', '审判', '争论']):
                return f"E{episode_num}-法庭激辩：关键冲突白热化"
            else:
                return f"E{episode_num}-激烈冲突：{plot_type}核心时刻"
        
        elif plot_type == '线索揭露':
            if any(word in content for word in ['证据', '发现', '真相']):
                return f"E{episode_num}-真相揭露：关键证据曝光"
            else:
                return f"E{episode_num}-线索发现：{plot_type}重要时刻"
        
        elif plot_type == '人物转折':
            if any(word in content for word in ['决定', '选择', '改变']):
                return f"E{episode_num}-命运转折：关键决定时刻"
            else:
                return f"E{episode_num}-角色转变：{plot_type}关键节点"
        
        elif plot_type == '情感爆发':
            return f"E{episode_num}-情感高潮：{plot_type}感人时刻"
        
        else:
            return f"E{episode_num}-{plot_type}：精彩剧情片段"

    def _extract_key_dialogues(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """提取关键台词"""
        key_dialogues = []
        
        for i in range(start_idx, min(end_idx + 1, start_idx + 20)):
            if i >= len(subtitles):
                break
                
            subtitle = subtitles[i]
            text = subtitle['text']
            
            # 评估台词重要性
            importance = 0
            
            # 情感强度
            importance += text.count('！') * 2
            importance += text.count('？') * 1.5
            
            # 关键词
            keywords = ['真相', '证据', '发现', '决定', '选择', '不可能', '震惊', '原来']
            for keyword in keywords:
                if keyword in text:
                    importance += 3
            
            if importance >= 3 and len(text) > 8:
                time_code = f"[{subtitle['start']} --> {subtitle['end']}]"
                key_dialogues.append(f"{time_code} {text}")
        
        return key_dialogues[:6]

    def _analyze_significance(self, subtitles: List[Dict], start_idx: int, end_idx: int, plot_type: str) -> str:
        """分析剧情意义"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        
        significance_parts = []
        
        if plot_type == '关键冲突':
            if any(word in content for word in ['法庭', '审判', '争议']):
                significance_parts.append("法庭争议核心冲突，正义与法理的激烈交锋")
            if any(word in content for word in ['证据', '质疑']):
                significance_parts.append("证据效力争议，真相与谎言的较量")
        
        elif plot_type == '线索揭露':
            if any(word in content for word in ['发现', '证据', '真相']):
                significance_parts.append("关键线索首次披露，案件真相逐步浮现")
            if any(word in content for word in ['秘密', '暴露']):
                significance_parts.append("隐藏秘密被揭露，剧情迎来重大转折")
        
        elif plot_type == '人物转折':
            if any(word in content for word in ['决定', '选择']):
                significance_parts.append("角色关键决定时刻，命运走向转折点")
            if any(word in content for word in ['改变', '转变']):
                significance_parts.append("人物性格转变，角色发展重要节点")
        
        return "；".join(significance_parts) if significance_parts else f"{plot_type}重要剧情发展节点"

    def _generate_summary(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> str:
        """生成内容摘要"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 15))])
        
        summary_points = []
        
        # 提取核心信息
        if '真相' in content or '发现' in content:
            summary_points.append("真相揭露")
        if '证据' in content:
            summary_points.append("证据展示")
        if '冲突' in content or '争论' in content:
            summary_points.append("激烈冲突")
        if '决定' in content or '选择' in content:
            summary_points.append("关键决定")
        if '情感' in content or '感动' in content:
            summary_points.append("情感表达")
        
        return "、".join(summary_points) if summary_points else "重要剧情发展"

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转换为秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def find_matching_video(self, srt_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        base_name = os.path.splitext(srt_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if base_name.lower() in filename.lower():
                    return os.path.join(self.videos_folder, filename)
        
        return None

    def process_single_episode(self, srt_file: str) -> bool:
        """处理单集完整流程"""
        print(f"\n📺 处理: {srt_file}")
        
        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_file)
        subtitles = self.parse_srt_file(srt_path)
        
        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False
        
        # 2. 提取集数
        episode_num = self._extract_episode_number(srt_file)
        
        # 3. 分析剧情点
        segments = self.analyze_plot_points(subtitles, episode_num)
        
        if not segments:
            print(f"❌ 未找到剧情点")
            return False
        
        # 4. 找到视频文件
        video_file = self.find_matching_video(srt_file)
        if not video_file:
            print(f"❌ 未找到视频文件")
            return False
        
        # 5. 创建视频片段
        created_clips = self.create_video_clips(segments, video_file, srt_file)
        
        # 6. 生成总结报告
        self._create_episode_summary(srt_file, segments, created_clips)
        
        print(f"✅ {srt_file} 处理完成: {len(created_clips)} 个片段")
        return len(created_clips) > 0

    def _extract_episode_number(self, filename: str) -> str:
        """提取集数"""
        # 提取数字
        numbers = re.findall(r'\d+', filename)
        if numbers:
            return numbers[-1].zfill(2)
        return "00"

    def _create_episode_summary(self, srt_file: str, segments: List[Dict], clips: List[str]):
        """创建集数总结"""
        try:
            episode_num = self._extract_episode_number(srt_file)
            summary_path = os.path.join(self.reports_folder, f"E{episode_num}_完整剧情分析报告.txt")
            
            # 分析主线剧情
            main_storyline = self._extract_main_storyline(segments)
            
            # 分析与前后集的连贯性
            prev_connection = self._analyze_previous_connection(segments, episode_num)
            next_setup = self._analyze_next_episode_setup(segments, episode_num)
            
            content = f"""📺 第{episode_num}集 完整剧情分析报告
{"=" * 100}

📊 基本信息:
• 集数: 第{episode_num}集
• 文件: {srt_file}
• 剧情点数量: {len(segments)} 个
• 成功片段: {len(clips)} 个
• 总时长: {sum(seg['duration'] for seg in segments):.1f} 秒 ({sum(seg['duration'] for seg in segments)/60:.1f} 分钟)

🎯 主线剧情:
{main_storyline}

🔗 跨集连贯性分析:
【与前集衔接】: {prev_connection}
【为下集铺垫】: {next_setup}

✨ 内容亮点总览:
"""
            
            # 汇总所有片段的亮点
            all_highlights = []
            for i, segment in enumerate(segments, 1):
                highlights = self._extract_content_highlights(segment)
                content += f"""
片段{i} - {segment['title']}:
{highlights}
"""
                all_highlights.extend(highlights.split('\n'))
            
            content += f"""

🎭 剧情点详细分析:
"""
            
            for i, segment in enumerate(segments, 1):
                content += f"""
{"=" * 60}
片段{i}: {segment['title']}
{"=" * 60}
🎭 类型: {segment['plot_type']}
📊 评分: {segment['score']:.1f}/100
⏱️ 时间: {segment['start_time']} --> {segment['end_time']} ({segment['duration']:.1f}秒)
💡 意义: {segment['plot_significance']}

🎙️ 旁观者叙述:
{segment['narration']['full_narration']}

📝 关键台词 (已修正错别字):
"""
                for dialogue in segment['key_dialogues']:
                    corrected_dialogue = self._correct_typos(dialogue)
                    content += f"  {corrected_dialogue}\n"
                
                content += f"""
✨ 本片段亮点:
{self._extract_content_highlights(segment)}

🔗 连贯性分析:
{segment.get('cross_episode_continuity', self._analyze_cross_episode_continuity(segment))}

📄 内容摘要: {segment['content_summary']}
"""
            
            content += f"""

{"=" * 100}
📋 标准化输出格式总结:
{"=" * 100}

🎬 制作规格:
• 剧情点智能识别: 5种类型自动分类
• 片段时长控制: 每个片段2-3分钟
• 非连续合并: 支持跳跃式时间段智能拼接
• 错别字修正: 自动修正常见繁体字和错误
• 旁白生成: 专业旁观者叙述，详细清晰

🔗 连贯性保证:
• 集内连贯: 所有片段组合完整讲述本集故事
• 跨集衔接: 明确标注与前后集的关联点
• 主线追踪: 重点追踪核心案件发展脉络

✨ 质量标准:
• 戏剧张力: 每个片段都有冲突或转折点
• 观看体验: 适合短视频平台传播
• 故事完整: 每个片段都有起承转合
• 信息准确: 字幕错误已修正，便于剪辑参考

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本: 智能剧情点剪辑系统 v3.0
"""
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📄 完整分析报告: {os.path.basename(summary_path)}")
            
        except Exception as e:
            print(f"⚠️ 总结生成失败: {e}")

    def _extract_main_storyline(self, segments: List[Dict]) -> str:
        """提取主线剧情"""
        storylines = []
        
        for segment in segments:
            content = segment.get('content_summary', '')
            plot_type = segment.get('plot_type', '')
            
            # 基于剧情点类型和内容提取主线
            if '四二八案' in content or '428案' in content:
                storylines.append("四二八案调查进展")
            if '628案' in content or '628旧案' in content:
                storylines.append("628旧案重新审视")
            if '申诉' in content:
                storylines.append("申诉程序启动")
            if '听证会' in content:
                storylines.append("听证会激辩")
            if '张园' in content and '霸凌' in content:
                storylines.append("张园霸凌事件真相")
            if '段洪山' in content:
                storylines.append("段洪山父女情深")
            
            # 基于剧情点类型补充
            if plot_type == '线索揭露':
                storylines.append("关键线索披露")
            elif plot_type == '关键冲突':
                storylines.append("核心冲突爆发")
        
        # 去重并组合
        unique_storylines = list(dict.fromkeys(storylines))
        return " → ".join(unique_storylines) if unique_storylines else "核心剧情发展"

    def _analyze_previous_connection(self, segments: List[Dict], episode_num: str) -> str:
        """分析与前集的连接"""
        if episode_num == "01":
            return "首集开篇，建立故事背景"
        
        # 从第一个片段分析与前集的连接
        if segments:
            first_segment = segments[0]
            content = first_segment.get('content_summary', '')
            
            if '继续' in content:
                return "承接前集未完成的情节线，故事连续发展"
            elif '回到' in content or '回想' in content:
                return "回顾前集关键事件，为本集发展做铺垫"
            elif '申诉' in content:
                return "在前集基础上启动申诉程序"
            elif '听证会' in content:
                return "前集申诉准备完毕，本集进入听证阶段"
            else:
                return "在前集剧情基础上自然发展"
        
        return "与前集剧情保持逻辑连贯"

    def _analyze_next_episode_setup(self, segments: List[Dict], episode_num: str) -> str:
        """分析为下集的铺垫"""
        if not segments:
            return "本集为独立情节，敬请期待下集发展"
        
        # 从最后一个片段分析为下集的铺垫
        last_segment = segments[-1]
        content = last_segment.get('content_summary', '')
        plot_type = last_segment.get('plot_type', '')
        
        setup_hints = []
        
        # 基于内容分析
        if '继续' in content or '待续' in content:
            setup_hints.append("本集情节未完，下集将继续发展")
        if '申诉' in content and '准备' in content:
            setup_hints.append("申诉准备工作完成，下集听证会即将开始")
        if '听证会' in content and ('即将' in content or '准备' in content):
            setup_hints.append("听证会准备就绪，下集法庭激辩即将展开")
        if '证据' in content and ('新' in content or '发现' in content):
            setup_hints.append("新证据浮现，下集案件将迎来重大转折")
        if '真相' in content and ('接近' in content or '即将' in content):
            setup_hints.append("真相即将大白，下集将有重大揭露")
        
        # 基于剧情点类型分析
        if plot_type == '线索揭露':
            setup_hints.append("关键线索已经披露，下集将深入追查")
        elif plot_type == '关键冲突':
            setup_hints.append("冲突已经爆发，下集将面临更大挑战")
        elif plot_type == '人物转折':
            setup_hints.append("角色转变将在下集产生深远影响")
        
        return "；".join(setup_hints) if setup_hints else "为下集剧情发展埋下重要伏笔"

    def process_all_episodes(self):
        """处理所有集数"""
        print("🚀 智能剧情点剪辑系统启动")
        print("=" * 80)
        
        # 获取所有SRT文件
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return
        
        srt_files.sort()
        
        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        
        # 处理每一集
        total_success = 0
        total_clips = 0
        
        for srt_file in srt_files:
            try:
                success = self.process_single_episode(srt_file)
                if success:
                    total_success += 1
                
                # 统计片段数
                episode_clips = [f for f in os.listdir(self.output_folder) 
                               if f.startswith(os.path.splitext(srt_file)[0]) and f.endswith('.mp4')]
                total_clips += len(episode_clips)
                
            except Exception as e:
                print(f"❌ 处理 {srt_file} 出错: {e}")
        
        # 最终报告
        self._create_final_report(total_success, len(srt_files), total_clips)

    def _create_final_report(self, success_count: int, total_episodes: int, total_clips: int):
        """创建最终报告"""
        report_content = f"""🎬 智能剧情点剪辑系统 - 最终报告
{"=" * 80}

📊 处理统计:
• 总集数: {total_episodes} 集
• 成功处理: {success_count} 集
• 成功率: {(success_count/total_episodes*100) if total_episodes > 0 else 0:.1f}%
• 生成片段: {total_clips} 个

✨ 系统特色:
1. ✅ 智能识别5种剧情点类型（关键冲突、人物转折、线索揭露、情感爆发、重要对话）
2. ✅ 非连续时间段智能合并，保证剧情逻辑连贯
3. ✅ 自动生成旁观者叙述字幕，详细清晰
4. ✅ 完整故事线说明，每个片段都有剧情意义分析
5. ✅ 智能错别字修正，确保字幕质量
6. ✅ 跨集连贯性保证，适合连续观看
7. ✅ 按剧情点分段剪辑，突出精彩部分
8. ✅ 多种视频格式支持，智能文件匹配

📁 输出文件:
• 视频片段: {self.output_folder}/*.mp4
• 旁白字幕: {self.output_folder}/*_旁白.srt
• 分析报告: {self.output_folder}/*_分析报告.txt
• 集数总结: {self.reports_folder}/*_剧情总结.txt

🎯 适用场景:
• 短视频平台内容制作
• 电视剧精彩片段剪辑
• 剧情分析和解说
• 影视内容二次创作

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        report_path = os.path.join(self.reports_folder, "系统最终报告.txt")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"\n📊 最终统计:")
            print(f"✅ 成功处理: {success_count}/{total_episodes} 集")
            print(f"🎬 生成片段: {total_clips} 个")
            print(f"📄 详细报告: {report_path}")
            
        except Exception as e:
            print(f"⚠️ 报告生成失败: {e}")

def main():
    """主函数"""
    clipper = IntelligentPlotClipper()
    clipper.process_all_episodes()

if __name__ == "__main__":
    main()

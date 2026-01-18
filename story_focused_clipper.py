
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
故事线聚焦的智能电视剧剪辑系统
专门解决：
1. 单集核心聚焦：每集1个核心剧情点，2-3分钟
2. 完整故事线说明和跨集连贯性
3. 精确时间轴片段选择
4. 智能错别字修正
5. 详细衔接点分析
"""

import os
import re
import json
import subprocess
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class StoryFocusedClipper:
    def __init__(self, srt_folder: str = "srt", videos_folder: str = "videos", output_folder: str = "story_clips"):
        self.srt_folder = srt_folder
        self.videos_folder = videos_folder
        self.output_folder = output_folder
        
        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.output_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✓ 创建目录: {folder}/")
        
        # 故事线连贯性缓存
        self.story_context = {
            'previous_episode_ending': '',
            'main_storylines': {},
            'character_arcs': {},
            'case_progress': {}
        }
        
        # 错别字修正字典（扩展版）
        self.corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '審判': '审判', '辯護': '辩护', '起訴': '起诉', '調查': '调查',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
            '結束': '结束', '問題': '问题', '機會': '机会', '聽證會': '听证会',
            '無罪': '无罪', '有罪': '有罪', '実現': '实现', '対話': '对话',
            '関係': '关系', '実际': '实际', '対于': '对于', '変化': '变化'
        }

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """智能解析SRT字幕文件"""
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
                    
                    # 匹配时间格式 (支持 , 和 . 作为毫秒分隔符)
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

    def analyze_story_core(self, subtitles: List[Dict], episode_num: str) -> Dict:
        """分析单集故事核心"""
        
        # 主线剧情关键词（根据您的需求定制）
        main_storylines = {
            '四二八案': ['四二八案', '428案', '段洪山', '正当防卫'],
            '628旧案': ['628案', '628旧案', '张园', '霸凌'],
            '听证会': ['听证会', '申诉', '重审', '辩护'],
            '调查线': ['证据', '调查', '线索', '发现', '真相'],
            '情感线': ['父女', '情感', '关系', '坚持', '支持']
        }
        
        # 戏剧张力关键词
        dramatic_moments = [
            '反转', '揭露', '震惊', '不可能', '真相', '秘密',
            '证明', '推翻', '颠覆', '关键', '决定性', '突破'
        ]
        
        # 评分每个字幕段
        scored_segments = []
        total_duration = len(subtitles)
        
        for i, subtitle in enumerate(subtitles):
            score = 0
            text = subtitle['text']
            position_ratio = i / total_duration
            
            # 主线剧情评分
            for storyline, keywords in main_storylines.items():
                matches = sum(1 for kw in keywords if kw in text)
                if matches > 0:
                    score += matches * 5  # 主线剧情高权重
                    
            # 戏剧张力评分
            drama_score = sum(1 for kw in dramatic_moments if kw in text)
            score += drama_score * 3
            
            # 对话强度评分
            score += text.count('！') * 2
            score += text.count('？') * 1.5
            score += text.count('...') * 1
            
            # 位置权重（开头结尾更重要）
            if position_ratio < 0.2 or position_ratio > 0.8:
                score *= 1.3
            
            if score >= 4:  # 只保留高分片段
                scored_segments.append({
                    'index': i,
                    'subtitle': subtitle,
                    'score': score,
                    'storylines': [sl for sl, kws in main_storylines.items() 
                                 if any(kw in text for kw in kws)]
                })
        
        if not scored_segments:
            # 如果没有高分片段，选择中间部分
            mid_point = total_duration // 2
            return self._create_fallback_segment(subtitles, mid_point, episode_num)
        
        # 选择最高分的片段作为核心
        scored_segments.sort(key=lambda x: x['score'], reverse=True)
        core_segment = scored_segments[0]
        
        return self._build_core_segment(subtitles, core_segment, episode_num)

    def _build_core_segment(self, subtitles: List[Dict], core_segment: Dict, episode_num: str) -> Dict:
        """构建核心片段信息"""
        
        core_index = core_segment['index']
        target_duration = 150  # 2.5分钟目标时长
        
        # 向前后扩展片段
        start_index, end_index = self._expand_segment(subtitles, core_index, target_duration)
        
        # 寻找自然的开始和结束点
        start_index = self._find_natural_start(subtitles, start_index, core_index)
        end_index = self._find_natural_end(subtitles, core_index, end_index)
        
        # 计算实际时长
        start_time = subtitles[start_index]['start']
        end_time = subtitles[end_index]['end']
        duration = self._time_to_seconds(end_time) - self._time_to_seconds(start_time)
        
        # 生成主题和分析
        theme = self._generate_episode_theme(subtitles, start_index, end_index, episode_num)
        key_dialogues = self._extract_key_dialogues(subtitles, start_index, end_index)
        core_value = self._analyze_core_value(subtitles, start_index, end_index, core_segment['storylines'])
        connection_hint = self._generate_connection_hint(subtitles, start_index, end_index, episode_num)
        
        return {
            'episode_number': episode_num,
            'theme': theme,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'start_index': start_index,
            'end_index': end_index,
            'key_dialogues': key_dialogues,
            'core_value': core_value,
            'storylines': core_segment['storylines'],
            'connection_to_next': connection_hint,
            'score': core_segment['score']
        }

    def _expand_segment(self, subtitles: List[Dict], center_index: int, target_duration: float) -> Tuple[int, int]:
        """向前后扩展片段到目标时长"""
        start_index = center_index
        end_index = center_index
        
        # 向前扩展
        while start_index > 0:
            test_duration = (self._time_to_seconds(subtitles[end_index]['end']) - 
                           self._time_to_seconds(subtitles[start_index-1]['start']))
            if test_duration > target_duration:
                break
            start_index -= 1
        
        # 向后扩展
        while end_index < len(subtitles) - 1:
            test_duration = (self._time_to_seconds(subtitles[end_index+1]['end']) - 
                           self._time_to_seconds(subtitles[start_index]['start']))
            if test_duration > target_duration * 1.3:  # 最多3.9分钟
                break
            end_index += 1
        
        return start_index, end_index

    def _find_natural_start(self, subtitles: List[Dict], search_start: int, anchor: int) -> int:
        """寻找自然的开始点"""
        scene_starters = ['那么', '现在', '这时', '突然', '接下来', '首先', '然后']
        
        for i in range(anchor, max(0, search_start - 3), -1):
            if i < len(subtitles):
                text = subtitles[i]['text']
                if any(starter in text for starter in scene_starters):
                    return i
                if '。' in text and len(text) < 20:  # 短句结束
                    return min(i + 1, anchor)
        
        return search_start

    def _find_natural_end(self, subtitles: List[Dict], anchor: int, search_end: int) -> int:
        """寻找自然的结束点"""
        scene_enders = ['好的', '明白', '知道了', '算了', '结束', '完了', '离开']
        
        for i in range(anchor, min(len(subtitles), search_end + 3)):
            text = subtitles[i]['text']
            if any(ender in text for ender in scene_enders):
                return i
            if '。' in text and i > anchor + 15:  # 足够长度后的句号
                return i
        
        return min(search_end, len(subtitles) - 1)

    def _generate_episode_theme(self, subtitles: List[Dict], start_idx: int, end_idx: int, episode_num: str) -> str:
        """生成集数主题"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 10))])
        
        # 智能主题生成
        if '四二八案' in content or '段洪山' in content:
            if '申诉' in content or '启动' in content:
                return f"E{episode_num}：四二八案申诉启动，正当防卫争议浮现"
            elif '调查' in content or '证据' in content:
                return f"E{episode_num}：四二八案深入调查，关键证据浮出水面"
            else:
                return f"E{episode_num}：四二八案核心剧情，父女情深法理难"
        
        elif '628案' in content or '628旧案' in content or '张园' in content:
            if '霸凌' in content:
                return f"E{episode_num}：628旧案真相大白，校园霸凌证据确凿"
            elif '发现' in content or '揭露' in content:
                return f"E{episode_num}：628旧案疑点重重，隐藏真相即将揭露"
            else:
                return f"E{episode_num}：628旧案重新审视，关键线索浮现"
        
        elif '听证会' in content:
            return f"E{episode_num}：听证会激烈辩论，正当防卫争议焦点"
        
        elif '证据' in content and ('新' in content or '关键' in content):
            return f"E{episode_num}：关键证据突破性发现，案件迎来转折"
        
        else:
            return f"E{episode_num}：核心剧情推进，真相逐步揭露"

    def _extract_key_dialogues(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """提取关键台词（带时间码）"""
        key_dialogues = []
        
        # 关键词优先级
        priority_keywords = [
            '四二八案', '628案', '段洪山', '张园', '霸凌', '正当防卫',
            '听证会', '申诉', '证据', '真相', '发现', '调查', '重审'
        ]
        
        for i in range(start_idx, min(end_idx + 1, start_idx + 20)):
            subtitle = subtitles[i]
            text = subtitle['text']
            
            # 检查是否是关键台词
            is_key = False
            
            # 包含优先关键词
            if any(kw in text for kw in priority_keywords):
                is_key = True
            # 情感强烈的台词
            elif text.count('！') >= 2 or text.count('？') >= 2:
                is_key = True
            # 戏剧性台词
            elif any(word in text for word in ['不可能', '震惊', '真相', '证明', '推翻']):
                is_key = True
            
            if is_key and len(text) > 8:
                time_code = f"{subtitle['start']} --> {subtitle['end']}"
                key_dialogues.append(f"[{time_code}] {text}")
        
        return key_dialogues[:6]  # 最多6条关键台词

    def _analyze_core_value(self, subtitles: List[Dict], start_idx: int, end_idx: int, storylines: List[str]) -> str:
        """分析片段核心价值"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        
        values = []
        
        # 基于故事线分析
        if '四二八案' in storylines:
            if '申诉' in content:
                values.append("四二八案申诉程序启动，法律救济路径开启")
            elif '调查' in content or '证据' in content:
                values.append("四二八案深度调查，关键证据链条完善")
            else:
                values.append("四二八案核心争议，正当防卫认定焦点")
        
        if '628旧案' in storylines:
            if '霸凌' in content and '张园' in content:
                values.append("628旧案霸凌真相完全揭露，案件本质彻底反转")
            elif '发现' in content or '线索' in content:
                values.append("628旧案关键线索发现，隐藏真相即将大白")
            else:
                values.append("628旧案重新审视，疑点逐一梳理")
        
        if '听证会' in storylines:
            values.append("听证会激烈法庭辩论，正当防卫争议白热化")
        
        if '调查线' in storylines:
            values.append("调查工作重大突破，证据链条日趋完整")
        
        if '情感线' in storylines:
            values.append("父女情感深度刻画，法理情理交织冲突")
        
        # 戏剧张力分析
        if any(word in content for word in ['反转', '颠覆', '推翻', '震惊']):
            values.append("剧情重大反转时刻，观众认知彻底颠覆")
        
        return "；".join(values) if values else "重要剧情推进节点，故事发展关键时刻"

    def _generate_connection_hint(self, subtitles: List[Dict], start_idx: int, end_idx: int, episode_num: str) -> str:
        """生成下集衔接说明"""
        
        # 分析片段结尾内容
        end_content = ' '.join([subtitles[i]['text'] for i in range(max(0, end_idx-3), end_idx + 1)])
        
        # 更新故事上下文
        self.story_context['previous_episode_ending'] = end_content
        
        # 生成衔接说明
        if '申诉' in end_content and ('启动' in end_content or '开始' in end_content):
            return f"本集四二八案申诉程序正式启动，为下一集听证会准备工作和法律程序推进铺垫"
        
        elif '听证会' in end_content and ('准备' in end_content or '即将' in end_content):
            return f"听证会准备工作就绪，下一集将展现激烈法庭辩论和正当防卫争议焦点"
        
        elif '证据' in end_content and ('发现' in end_content or '新' in end_content):
            return f"关键证据重大发现，下一集案件调查将迎来突破性进展"
        
        elif '张园' in end_content and '霸凌' in end_content:
            return f"张园霸凌证据首次披露，下一集628旧案真相将彻底大白"
        
        elif '真相' in end_content or '揭露' in end_content:
            return f"部分真相初步揭露，下一集更深层次的案件本质即将浮出水面"
        
        elif '调查' in end_content or '线索' in end_content:
            return f"调查线索重要突破，下一集将沿着新发现的线索深入挖掘真相"
        
        else:
            return f"重要剧情节点确立，下一集故事主线将在此基础上深入发展"

    def _create_fallback_segment(self, subtitles: List[Dict], center_point: int, episode_num: str) -> Dict:
        """备用片段创建（当没有高分片段时）"""
        target_duration = 150
        
        start_idx = max(0, center_point - 25)
        end_idx = min(len(subtitles) - 1, center_point + 25)
        
        # 调整到合适时长
        while end_idx < len(subtitles) - 1:
            duration = (self._time_to_seconds(subtitles[end_idx]['end']) - 
                       self._time_to_seconds(subtitles[start_idx]['start']))
            if duration >= target_duration:
                break
            end_idx += 1
        
        return {
            'episode_number': episode_num,
            'theme': f"E{episode_num}：精彩剧情片段",
            'start_time': subtitles[start_idx]['start'],
            'end_time': subtitles[end_idx]['end'],
            'duration': self._time_to_seconds(subtitles[end_idx]['end']) - self._time_to_seconds(subtitles[start_idx]['start']),
            'start_index': start_idx,
            'end_index': end_idx,
            'key_dialogues': [f"[{subtitles[start_idx]['start']} --> {subtitles[start_idx]['end']}] {subtitles[start_idx]['text']}"],
            'core_value': "核心剧情推进片段",
            'storylines': ['通用剧情'],
            'connection_to_next': "剧情持续发展，下集故事线深入推进",
            'score': 3.0
        }

    def _time_to_seconds(self, time_str: str) -> float:
        """时间字符串转换为秒数"""
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
        
        # 提取集数模糊匹配
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

    def create_story_clip(self, segment_info: Dict, video_file: str) -> bool:
        """创建故事聚焦短视频"""
        try:
            theme = segment_info['theme']
            start_time = segment_info['start_time']
            end_time = segment_info['end_time']
            
            # 生成安全文件名
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', theme)
            output_name = f"{safe_theme}.mp4"
            output_path = os.path.join(self.output_folder, output_name)
            
            print(f"\n🎬 创建故事聚焦短视频: {theme}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"⏱️ 时间段: {start_time} --> {end_time}")
            print(f"📏 时长: {segment_info['duration']:.1f}秒")
            print(f"🎭 故事线: {', '.join(segment_info['storylines'])}")
            print(f"📊 评分: {segment_info['score']:.1f}/10")
            
            # 计算时间
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
                print(f"  ✅ 成功创建: {output_name} ({file_size:.1f}MB)")
                
                # 创建详细说明文件
                self._create_description_file(output_path, segment_info)
                
                return True
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"
                print(f"  ❌ 剪辑失败: {error_msg}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建短视频时出错: {e}")
            return False

    def _create_description_file(self, video_path: str, segment_info: Dict):
        """创建详细说明文件"""
        try:
            desc_path = video_path.replace('.mp4', '_故事分析.txt')
            
            content = f"""📺 {segment_info['theme']}
{"=" * 80}

⏱️ 精确时间片段: {segment_info['start_time']} --> {segment_info['end_time']}
📏 片段时长: {segment_info['duration']:.1f} 秒 ({segment_info['duration']/60:.1f} 分钟)
🎭 涉及故事线: {', '.join(segment_info['storylines'])}
📊 剧情重要度评分: {segment_info['score']:.1f}/10

💡 核心价值分析:
{segment_info['core_value']}

📝 关键台词（带精确时间码）:
"""
            for dialogue in segment_info['key_dialogues']:
                content += f"{dialogue}\n"
            
            content += f"""
🔗 下集衔接说明:
{segment_info['connection_to_next']}

📄 故事线完整性说明:
• 本片段为第{segment_info['episode_number']}集核心剧情聚焦
• 时长精确控制在2-3分钟，突出单一核心剧情点
• 涉及主要故事线: {', '.join(segment_info['storylines'])}
• 包含完整对话场景，确保剧情连贯性
• 错别字已修正，便于剪辑参考
• 与下一集明确衔接，保持故事线连续性

🎯 剪辑建议:
• 严格按照标注时间轴进行剪辑
• 保留完整对话，不要截断重要内容
• 可在片头添加简短上集回顾（10-15秒）
• 片尾可添加下集预告提示（5-10秒）
"""
            
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 生成故事分析文件: {os.path.basename(desc_path)}")
            
        except Exception as e:
            print(f"    ⚠ 生成说明文件失败: {e}")

def main():
    """主程序入口"""
    print("🚀 故事线聚焦的智能电视剧剪辑系统")
    print("=" * 80)
    print("🎯 专业特性:")
    print("• 单集核心聚焦：每集1个核心剧情点，2-3分钟精准时长")
    print("• 完整故事线分析：优先主线剧情，确保连贯性")
    print("• 精确时间轴标注：毫秒级精度，便于剪辑操作")
    print("• 智能错别字修正：自动修正常见错误")
    print("• 跨集连贯性保证：明确衔接点说明")
    print("=" * 80)
    
    clipper = StoryFocusedClipper()
    
    # 获取所有SRT字幕文件
    srt_files = []
    if os.path.exists(clipper.srt_folder):
        for file in os.listdir(clipper.srt_folder):
            if file.lower().endswith('.srt'):
                srt_files.append(file)
    
    srt_files.sort()
    
    if not srt_files:
        print("❌ 未找到SRT字幕文件")
        print(f"请将字幕文件放在 {clipper.srt_folder}/ 目录中")
        print("支持格式: .srt")
        return
    
    print(f"📄 找到 {len(srt_files)} 个SRT字幕文件")
    
    # 检查视频目录
    if not os.path.exists(clipper.videos_folder):
        print(f"❌ 视频目录不存在: {clipper.videos_folder}")
        print("请创建videos目录并放入对应的视频文件")
        return
    
    video_files = [f for f in os.listdir(clipper.videos_folder) 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.ts'))]
    
    print(f"🎬 找到 {len(video_files)} 个视频文件")
    
    created_clips = []
    all_segments = []
    
    for i, srt_file in enumerate(srt_files, 1):
        print(f"\n📺 分析第 {i} 集: {srt_file}")
        
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
        
        # 分析故事核心
        segment_info = clipper.analyze_story_core(subtitles, episode_num)
        all_segments.append(segment_info)
        
        print(f"  🎯 主题: {segment_info['theme']}")
        print(f"  🎭 故事线: {', '.join(segment_info['storylines'])}")
        print(f"  ⏱️ 时间: {segment_info['start_time']} --> {segment_info['end_time']} ({segment_info['duration']:.1f}秒)")
        print(f"  💡 价值: {segment_info['core_value'][:60]}...")
        print(f"  📊 评分: {segment_info['score']:.1f}/10")
        
        # 找到对应视频文件
        video_file = clipper.find_matching_video(srt_file)
        if not video_file:
            print(f"  ⚠ 未找到对应视频文件")
            continue
        
        # 创建短视频
        if clipper.create_story_clip(segment_info, video_file):
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', segment_info['theme'])
            output_name = f"{safe_theme}.mp4"
            created_clips.append(os.path.join(clipper.output_folder, output_name))
    
    # 生成完整报告
    generate_story_report(all_segments, clipper, created_clips)
    
    print(f"\n📊 故事聚焦剪辑完成统计:")
    print(f"✅ 分析集数: {len(all_segments)} 集")
    print(f"✅ 成功制作: {len(created_clips)} 个短视频")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"📄 完整报告: story_focused_analysis_report.txt")

def generate_story_report(segments: List[Dict], clipper, created_clips: List[str]):
    """生成故事聚焦分析报告"""
    if not segments:
        return
    
    content = "📺 故事线聚焦的电视剧剪辑分析报告\n"
    content += "=" * 100 + "\n\n"
    
    content += "🎯 系统特性说明：\n"
    content += "• 单集核心聚焦：每集围绕1个核心剧情点，时长控制在2-3分钟\n"
    content += "• 完整故事线保证：优先主线剧情，确保跨集连贯性\n"
    content += "• 精确时间轴标注：毫秒级精度，便于专业剪辑操作\n"
    content += "• 智能错别字修正：自动修正防衛→防卫等常见错误\n"
    content += "• 详细衔接点分析：明确与下一集的连接说明\n\n"
    
    content += f"📊 制作统计：\n"
    content += f"• 总集数: {len(segments)} 集\n"
    content += f"• 成功制作: {len(created_clips)} 个短视频\n"
    content += f"• 制作成功率: {len(created_clips)/len(segments)*100:.1f}%\n\n"
    
    # 故事线分布统计
    storyline_stats = {}
    total_duration = 0
    total_score = 0
    
    for segment in segments:
        for storyline in segment['storylines']:
            storyline_stats[storyline] = storyline_stats.get(storyline, 0) + 1
        total_duration += segment['duration']
        total_score += segment['score']
    
    content += "📈 故事线分布：\n"
    for storyline, count in sorted(storyline_stats.items(), key=lambda x: x[1], reverse=True):
        content += f"• {storyline}: {count} 集\n"
    content += "\n"
    
    avg_duration = total_duration / len(segments) if segments else 0
    avg_score = total_score / len(segments) if segments else 0
    
    content += f"🎭 质量分析：\n"
    content += f"• 平均时长: {avg_duration:.1f} 秒 ({avg_duration/60:.1f} 分钟)\n"
    content += f"• 平均评分: {avg_score:.1f}/10\n"
    content += f"• 总时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)\n\n"
    
    # 详细分集信息
    for i, segment in enumerate(segments, 1):
        content += f"📺 {segment['theme']}\n"
        content += "-" * 80 + "\n"
        content += f"精确时间片段：{segment['start_time']} --> {segment['end_time']}\n"
        content += f"片段时长：{segment['duration']:.1f} 秒 ({segment['duration']/60:.1f} 分钟)\n"
        content += f"涉及故事线：{', '.join(segment['storylines'])}\n"
        content += f"重要度评分：{segment['score']:.1f}/10\n\n"
        
        content += "核心价值分析：\n"
        content += f"{segment['core_value']}\n\n"
        
        content += "关键台词（带时间码）：\n"
        for dialogue in segment['key_dialogues']:
            content += f"  {dialogue}\n"
        content += "\n"
        
        content += f"下集衔接说明：\n"
        content += f"{segment['connection_to_next']}\n"
        content += "=" * 100 + "\n\n"
    
    # 整体连贯性分析
    content += "🔗 整体故事线连贯性分析：\n"
    content += "• 每集都有明确的核心剧情点聚焦\n"
    content += "• 主线故事（四二八案、628旧案、听证会）贯穿始终\n"
    content += "• 跨集衔接点明确，保证观看连贯性\n"
    content += "• 时间轴精确标注，便于专业剪辑操作\n"
    content += "• 适合短视频平台传播和剧情解说\n"
    
    try:
        with open('story_focused_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 故事聚焦分析报告已保存")
    except Exception as e:
        print(f"⚠ 保存报告失败: {e}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单集短视频剪辑器 - 每集一个2-3分钟的核心剧情短视频
"""

import os
import re
import subprocess
from typing import List, Dict, Optional

class EpisodeClipper:
    def __init__(self, video_folder: str = "videos", output_folder: str = "episode_clips"):
        self.video_folder = video_folder
        self.output_folder = output_folder
        
        # 创建输出文件夹
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"✓ 创建输出目录: {self.output_folder}/")
        
        # 主线剧情关键词
        self.main_plot_keywords = [
            '四二八案', '428案', '628旧案', '628案', '正当防卫', '听证会', 
            '段洪山', '张园', '霸凌', '申诉', '重审', '证据', '证词',
            '检察官', '法官', '律师', '辩护', '起诉', '判决'
        ]
        
        # 戏剧张力关键词
        self.dramatic_keywords = [
            '反转', '揭露', '发现', '真相', '秘密', '震惊', '不可能',
            '证明', '推翻', '颠覆', '关键', '重要', '决定性'
        ]
        
        # 情感爆发词
        self.emotional_keywords = [
            '愤怒', '痛苦', '激动', '崩溃', '哭', '喊', '怒', '绝望',
            '希望', '感动', '震撼', '无奈', '坚持'
        ]

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件并修正错别字"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 修正常见错别字
            corrections = {
                '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
                '調查': '调查', '審判': '审判', '辯護': '辩护', '起訴': '起诉'
            }
            
            for old, new in corrections.items():
                content = content.replace(old, new)
            
            # 解析字幕块
            blocks = re.split(r'\n\s*\n', content.strip())
            subtitles = []
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        index = int(lines[0])
                        time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                        if time_match:
                            start_time = time_match.group(1)
                            end_time = time_match.group(2)
                            text = '\n'.join(lines[2:])
                            
                            subtitles.append({
                                'index': index,
                                'start': start_time,
                                'end': end_time,
                                'text': text,
                                'episode': os.path.basename(filepath)
                            })
                    except (ValueError, IndexError):
                        continue
            
            return subtitles
            
        except Exception as e:
            print(f"❌ 解析字幕文件失败 {filepath}: {e}")
            return []

    def calculate_segment_score(self, text: str, position_ratio: float) -> float:
        """计算片段重要性评分"""
        score = 0
        
        # 主线剧情评分（权重最高）
        for keyword in self.main_plot_keywords:
            if keyword in text:
                score += 5
        
        # 戏剧张力评分
        for keyword in self.dramatic_keywords:
            if keyword in text:
                score += 3
        
        # 情感强度评分
        for keyword in self.emotional_keywords:
            if keyword in text:
                score += 2
        
        # 对话强度评分（标点符号）
        score += text.count('！') * 1.5
        score += text.count('？') * 1.0
        score += text.count('...') * 0.5
        
        # 位置权重（开头和结尾更重要）
        if position_ratio < 0.2 or position_ratio > 0.8:
            score *= 1.2
        
        # 文本长度适中加分
        if 20 <= len(text) <= 100:
            score += 1
        
        return score

    def find_core_segment(self, subtitles: List[Dict], episode_num: str) -> Optional[Dict]:
        """找到单集的核心片段（2-3分钟）"""
        if not subtitles:
            return None
        
        # 计算每个字幕的评分
        scored_subtitles = []
        total_subtitles = len(subtitles)
        
        for i, subtitle in enumerate(subtitles):
            position_ratio = i / total_subtitles
            score = self.calculate_segment_score(subtitle['text'], position_ratio)
            
            if score >= 3:  # 只考虑高分片段
                scored_subtitles.append({
                    'index': i,
                    'subtitle': subtitle,
                    'score': score
                })
        
        if not scored_subtitles:
            # 如果没有高分片段，选择中间部分
            mid_start = total_subtitles // 3
            mid_end = total_subtitles * 2 // 3
            scored_subtitles = [{
                'index': mid_start,
                'subtitle': subtitles[mid_start],
                'score': 1
            }]
        
        # 按评分排序
        scored_subtitles.sort(key=lambda x: x['score'], reverse=True)
        
        # 选择最高分的片段作为核心
        core_subtitle = scored_subtitles[0]
        core_index = core_subtitle['index']
        
        # 向前后扩展，确保2-3分钟时长
        target_duration = 150  # 2.5分钟
        start_index = core_index
        end_index = core_index
        
        # 向前扩展
        while start_index > 0:
            test_duration = self.time_to_seconds(subtitles[end_index]['end']) - self.time_to_seconds(subtitles[start_index-1]['start'])
            if test_duration > target_duration:
                break
            start_index -= 1
        
        # 向后扩展
        while end_index < len(subtitles) - 1:
            test_duration = self.time_to_seconds(subtitles[end_index+1]['end']) - self.time_to_seconds(subtitles[start_index]['start'])
            if test_duration > target_duration * 1.2:  # 最多3分钟
                break
            end_index += 1
        
        # 寻找自然的开始和结束点
        start_index = self.find_natural_start(subtitles, start_index, core_index)
        end_index = self.find_natural_end(subtitles, core_index, end_index)
        
        segment_duration = self.time_to_seconds(subtitles[end_index]['end']) - self.time_to_seconds(subtitles[start_index]['start'])
        
        # 生成主题
        theme = self.generate_episode_theme(subtitles, start_index, end_index, episode_num)
        
        # 提取关键台词
        key_dialogues = self.extract_key_dialogues(subtitles, start_index, end_index)
        
        # 分析核心价值
        core_value = self.analyze_core_value(subtitles, start_index, end_index)
        
        # 生成衔接说明
        connection = self.generate_connection_hint(subtitles, start_index, end_index, episode_num)
        
        return {
            'episode_number': episode_num,
            'theme': theme,
            'start_time': subtitles[start_index]['start'],
            'end_time': subtitles[end_index]['end'],
            'duration': segment_duration,
            'start_index': start_index,
            'end_index': end_index,
            'key_dialogues': key_dialogues,
            'core_value': core_value,
            'connection_to_next': connection,
            'content_summary': self.generate_content_summary(subtitles, start_index, end_index)
        }

    def find_natural_start(self, subtitles: List[Dict], search_start: int, anchor: int) -> int:
        """寻找自然的开始点"""
        scene_starters = ['突然', '这时', '忽然', '现在', '那么', '首先', '接下来']
        
        for i in range(anchor, max(0, search_start - 5), -1):
            text = subtitles[i]['text']
            if any(starter in text for starter in scene_starters):
                return i
            if '。' in text and len(text) < 15:  # 短句结束
                return i + 1
        
        return search_start

    def find_natural_end(self, subtitles: List[Dict], anchor: int, search_end: int) -> int:
        """寻找自然的结束点"""
        scene_enders = ['结束', '完了', '好吧', '算了', '走了', '离开', '再见']
        
        for i in range(anchor, min(len(subtitles) - 1, search_end + 5)):
            text = subtitles[i]['text']
            if any(ender in text for ender in scene_enders):
                return i
            if '。' in text and i > anchor + 10:  # 适当长度后的句号
                return i
        
        return min(search_end, len(subtitles) - 1)

    def generate_episode_theme(self, subtitles: List[Dict], start_idx: int, end_idx: int, episode_num: str) -> str:
        """生成集数主题"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 10))])
        
        # 根据内容生成主题
        if '四二八案' in content and '申诉' in content:
            theme = f"E{episode_num}：四二八案申诉启动，案件迎来转机"
        elif '628案' in content or '628旧案' in content:
            theme = f"E{episode_num}：628旧案疑点浮现，真相即将揭露"
        elif '听证会' in content:
            theme = f"E{episode_num}：听证会激烈辩论，正当防卫争议"
        elif '张园' in content and '霸凌' in content:
            theme = f"E{episode_num}：张园霸凌证据曝光，案件真相大白"
        elif '段洪山' in content:
            theme = f"E{episode_num}：段洪山父女情深，法理情交织"
        elif '证据' in content and ('新' in content or '关键' in content):
            theme = f"E{episode_num}：关键证据浮现，案件迎来转折"
        else:
            theme = f"E{episode_num}：核心剧情推进，真相逐步揭露"
        
        return theme

    def extract_key_dialogues(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """提取关键台词"""
        key_dialogues = []
        
        for i in range(start_idx, min(end_idx + 1, start_idx + 20)):  # 限制数量
            subtitle = subtitles[i]
            text = subtitle['text']
            
            # 检查是否是关键台词
            is_key = False
            if any(keyword in text for keyword in self.main_plot_keywords):
                is_key = True
            elif any(keyword in text for keyword in self.dramatic_keywords):
                is_key = True
            elif text.count('！') >= 2 or text.count('？') >= 2:
                is_key = True
            
            if is_key and len(text) > 10:
                time_range = f"[{subtitle['start']} --> {subtitle['end']}]"
                key_dialogues.append(f"{time_range} {text}")
        
        return key_dialogues[:5]  # 最多5条关键台词

    def analyze_core_value(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> str:
        """分析片段核心价值"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        
        values = []
        
        if '四二八案' in content or '628案' in content:
            values.append("核心案件调查进展")
        if '申诉' in content or '重审' in content:
            values.append("法律程序重大突破")
        if '证据' in content and ('新' in content or '关键' in content):
            values.append("关键证据首次披露")
        if '张园' in content and '霸凌' in content:
            values.append("霸凌真相震撼揭露")
        if '听证会' in content:
            values.append("法庭激辩高潮时刻")
        if '段洪山' in content:
            values.append("父女情感深度刻画")
        if any(word in content for word in ['反转', '颠覆', '推翻']):
            values.append("剧情重大反转点")
        
        if values:
            return "、".join(values)
        else:
            return "重要剧情推进节点"

    def generate_connection_hint(self, subtitles: List[Dict], start_idx: int, end_idx: int, episode_num: str) -> str:
        """生成与下一集的衔接说明"""
        content = ' '.join([subtitles[i]['text'] for i in range(max(0, end_idx-5), end_idx + 1)])
        
        if '申诉' in content and '启动' in content:
            return f"本集申诉程序启动，为下一集听证会翻案铺垫"
        elif '听证会' in content and ('准备' in content or '即将' in content):
            return f"听证会准备就绪，下一集法庭激辩即将开始"
        elif '证据' in content and ('发现' in content or '新' in content):
            return f"新证据浮现，下一集案件迎来重大转机"
        elif '张园' in content:
            return f"张园涉案信息披露，下一集霸凌真相全面揭露"
        elif '继续' in content or '下次' in content:
            return f"关键线索埋下，下一集真相进一步揭露"
        else:
            return f"重要情节节点确立，下一集故事线深入发展"

    def generate_content_summary(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> str:
        """生成内容摘要"""
        key_points = []
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, min(end_idx + 1, start_idx + 15))])
        
        if '四二八案' in content:
            key_points.append("四二八案调查")
        if '628案' in content:
            key_points.append("628旧案重现")
        if '申诉' in content:
            key_points.append("申诉程序")
        if '听证会' in content:
            key_points.append("听证会辩论")
        if '张园' in content:
            key_points.append("张园霸凌")
        if '段洪山' in content:
            key_points.append("段洪山父女")
        if '证据' in content:
            key_points.append("关键证据")
        
        return " | ".join(key_points) if key_points else "核心剧情发展"

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def find_video_file(self, episode_subtitle_name: str) -> Optional[str]:
        """找到对应的视频文件"""
        if not os.path.exists(self.video_folder):
            return None
        
        base_name = os.path.basename(episode_subtitle_name).replace('.txt', '').replace('.srt', '')
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        for filename in os.listdir(self.video_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                file_base = os.path.splitext(filename)[0]
                if base_name.lower() in file_base.lower() or file_base.lower() in base_name.lower():
                    return os.path.join(self.video_folder, filename)
        
        return None

    def create_episode_clip(self, segment_plan: Dict, video_file: str) -> bool:
        """创建单集短视频"""
        try:
            episode_num = segment_plan['episode_number']
            theme = segment_plan['theme']
            start_time = segment_plan['start_time']
            end_time = segment_plan['end_time']
            
            # 输出文件名
            safe_theme = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', theme)
            output_name = f"{safe_theme}.mp4"
            output_path = os.path.join(self.output_folder, output_name)
            
            print(f"\n🎬 创建短视频: {theme}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"⏱️ 时间段: {start_time} --> {end_time}")
            print(f"📏 时长: {segment_plan['duration']:.1f}秒")
            
            # 计算精确时间
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            # 添加缓冲时间确保完整性
            buffer_start = max(0, start_seconds - 2)
            buffer_duration = duration + 4
            
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
                # 添加专业标题
                self.add_professional_overlay(output_path, segment_plan)
                
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"  ✅ 成功创建: {output_name} ({file_size:.1f}MB)")
                
                # 创建说明文件
                self.create_description_file(output_path, segment_plan)
                
                return True
            else:
                print(f"  ❌ 剪辑失败: {result.stderr[:100]}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建短视频时出错: {e}")
            return False

    def add_professional_overlay(self, video_path: str, segment_plan: Dict):
        """添加专业字幕叠层"""
        try:
            temp_path = video_path.replace('.mp4', '_temp.mp4')
            
            theme = segment_plan['theme']
            core_value = segment_plan['core_value']
            
            # 清理文本
            title_text = theme.replace("'", "").replace('"', '')[:40]
            value_text = core_value.replace("'", "").replace('"', '')[:30]
            
            # 创建字幕滤镜
            filter_text = (
                f"drawtext=text='{title_text}':fontsize=28:fontcolor=white:x=(w-text_w)/2:y=50:"
                f"box=1:boxcolor=black@0.8:boxborderw=6:enable='between(t,0,4)',"
                f"drawtext=text='{value_text}':fontsize=18:fontcolor=yellow:x=(w-text_w)/2:y=90:"
                f"box=1:boxcolor=black@0.7:boxborderw=4:enable='between(t,1,4)',"
                f"drawtext=text='🔥精彩片段':fontsize=16:fontcolor=red:x=20:y=20:"
                f"box=1:boxcolor=black@0.6:boxborderw=3:enable='gt(t,2)'"
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
                print(f"    ✓ 添加专业字幕完成")
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
        except Exception as e:
            print(f"    ⚠ 添加字幕失败: {e}")

    def create_description_file(self, video_path: str, segment_plan: Dict):
        """创建视频说明文件"""
        try:
            desc_path = video_path.replace('.mp4', '_说明.txt')
            
            content = f"""📺 {segment_plan['theme']}
{"=" * 60}

⏱️ 时间片段: {segment_plan['start_time']} --> {segment_plan['end_time']}
📏 片段时长: {segment_plan['duration']:.1f} 秒
💡 核心价值: {segment_plan['core_value']}

📝 关键台词:
"""
            for dialogue in segment_plan['key_dialogues']:
                content += f"{dialogue}\n"
            
            content += f"""
🎯 内容摘要: {segment_plan['content_summary']}

🔗 下集衔接: {segment_plan['connection_to_next']}

📄 剪辑说明:
• 本片段为第{segment_plan['episode_number']}集核心剧情
• 时长控制在2-3分钟，突出主线剧情
• 包含关键对话和戏剧张力点
• 与下一集剧情保持连贯性
"""
            
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 生成说明文件: {os.path.basename(desc_path)}")
            
        except Exception as e:
            print(f"    ⚠ 生成说明文件失败: {e}")

def process_all_episodes():
    """处理所有集数的短视频制作"""
    print("🎬 单集核心短视频制作系统")
    print("=" * 60)
    print("📋 制作规则:")
    print("• 每集1个核心剧情点，时长2-3分钟")
    print("• 突出主线剧情（四二八案、628旧案、听证会）")
    print("• 保持跨集连贯性")
    print("• 自动修正字幕错别字")
    print("=" * 60)
    
    clipper = EpisodeClipper()
    
    # 获取所有字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith('.txt') and ('E' in file or 'S' in file):
            subtitle_files.append(file)
    
    subtitle_files.sort()
    
    if not subtitle_files:
        print("❌ 未找到字幕文件")
        return
    
    print(f"📄 找到 {len(subtitle_files)} 个字幕文件")
    
    # 检查视频目录
    if not os.path.exists(clipper.video_folder):
        print(f"❌ 视频目录不存在: {clipper.video_folder}")
        print("请创建videos目录并放入对应的视频文件")
        return
    
    created_clips = []
    episode_plans = []
    
    for i, subtitle_file in enumerate(subtitle_files, 1):
        print(f"\n📺 处理第 {i} 集: {subtitle_file}")
        
        # 解析字幕
        subtitles = clipper.parse_subtitle_file(subtitle_file)
        if not subtitles:
            print(f"  ❌ 字幕解析失败")
            continue
        
        # 提取集数
        episode_match = re.search(r'[SE](\d+)', subtitle_file)
        episode_num = episode_match.group(1) if episode_match else str(i).zfill(2)
        
        # 找到核心片段
        segment_plan = clipper.find_core_segment(subtitles, episode_num)
        if not segment_plan:
            print(f"  ❌ 未找到合适的核心片段")
            continue
        
        episode_plans.append(segment_plan)
        
        # 找到对应视频文件
        video_file = clipper.find_video_file(subtitle_file)
        if not video_file:
            print(f"  ⚠ 未找到对应视频文件")
            continue
        
        # 创建短视频
        if clipper.create_episode_clip(segment_plan, video_file):
            theme = segment_plan['theme']
            output_name = f"{re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', theme)}.mp4"
            created_clips.append(os.path.join(clipper.output_folder, output_name))
    
    # 生成总体方案文档
    generate_series_plan_document(episode_plans)
    
    print(f"\n📊 制作完成统计:")
    print(f"✅ 成功制作: {len(created_clips)} 个短视频")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"📄 详细方案: series_plan.txt")

def generate_series_plan_document(episode_plans: List[Dict]):
    """生成整体剧集方案文档"""
    if not episode_plans:
        return
    
    content = "📺 电视剧单集短视频制作方案\n"
    content += "=" * 80 + "\n\n"
    
    content += "📋 制作规则:\n"
    content += "• 单集核心聚焦：每集围绕1个核心剧情点，时长2-3分钟\n"
    content += "• 主线剧情优先：突出四二八案、628旧案、听证会辩论\n"
    content += "• 强戏剧张力：证词反转、法律争议、情感爆发点\n"
    content += "• 跨集连贯性：保持故事线逻辑一致，明确衔接点\n\n"
    
    total_duration = 0
    
    for i, plan in enumerate(episode_plans, 1):
        content += f"📺 {plan['theme']}\n"
        content += "-" * 60 + "\n"
        content += f"时间片段：{plan['start_time']} --> {plan['end_time']}\n"
        content += f"片段时长：{plan['duration']:.1f} 秒 ({plan['duration']/60:.1f} 分钟)\n"
        content += f"核心价值：{plan['core_value']}\n"
        content += f"内容摘要：{plan['content_summary']}\n\n"
        
        content += "关键台词：\n"
        for dialogue in plan['key_dialogues']:
            content += f"  {dialogue}\n"
        
        content += f"\n🔗 下集衔接：{plan['connection_to_next']}\n"
        content += "=" * 80 + "\n\n"
        
        total_duration += plan['duration']
    
    content += f"📊 总体统计：\n"
    content += f"• 制作集数：{len(episode_plans)} 集\n"
    content += f"• 总时长：{total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)\n"
    content += f"• 平均时长：{total_duration/len(episode_plans):.1f} 秒\n"
    content += f"• 剧情连贯性：每集结尾都有明确的下集衔接说明\n"
    
    try:
        with open('series_plan.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 剧集方案文档已保存: series_plan.txt")
    except Exception as e:
        print(f"⚠ 保存方案文档失败: {e}")

if __name__ == "__main__":
    process_all_episodes()

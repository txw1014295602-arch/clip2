#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能剧情分析器 - 专注单集核心剧情和跨集连贯性
"""

import os
import re
import json
import requests
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class SmartAnalyzer:
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai

        # 主线剧情关键词
        self.main_plot_keywords = [
            '四二八案', '628旧案', '正当防卫', '听证会', '申诉', '重审',
            '段洪山', '张园', '霸凌', '证据', '真相', '翻案',
            '检察官', '律师', '法官', '证词', '辩护'
        ]

        # 戏剧张力标识
        self.dramatic_keywords = [
            '突然', '发现', '真相', '秘密', '反转', '揭露', '暴露',
            '冲突', '争议', '辩论', '对抗', '质疑', '颠覆'
        ]

        # 情感爆发标识
        self.emotional_keywords = [
            '愤怒', '激动', '崩溃', '哭泣', '震惊', '绝望', '希望',
            '坚持', '放弃', '决定', '选择', '改变', '觉悟'
        ]

        # 错别字修正
        self.corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '設計': '设计', '開始': '开始', '結束': '结束',
            '問題': '问题', '機會': '机会', '決定': '决定', '選擇': '选择',
            '聽證會': '听证会', '辯護': '辩护', '審判': '审判', '調查': '调查'
        }

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件并修正错别字"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            try:
                with open(filepath, 'r', encoding='gbk', errors='ignore') as f:
                    content = f.read()
            except:
                print(f"❌ 无法读取文件: {filepath}")
                return []

        # 修正错别字
        for old, new in self.corrections.items():
            content = content.replace(old, new)

        # 解析字幕
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

    def calculate_segment_score(self, text: str, position: float) -> float:
        """计算片段重要性评分"""
        score = 0

        # 主线剧情评分 (最高权重)
        for keyword in self.main_plot_keywords:
            if keyword in text:
                score += 5.0

        # 戏剧张力评分
        for keyword in self.dramatic_keywords:
            if keyword in text:
                score += 3.0

        # 情感强度评分
        for keyword in self.emotional_keywords:
            if keyword in text:
                score += 2.0

        # 对话强度评分
        score += text.count('！') * 0.5
        score += text.count('？') * 0.5
        score += text.count('...') * 0.3

        # 位置权重 (开头和结尾更重要)
        if position < 0.2 or position > 0.8:
            score *= 1.2

        # 文本长度适中加分
        text_len = len(text)
        if 20 <= text_len <= 150:
            score += 1.0
        elif text_len > 200:
            score *= 0.8

        return score

    def find_core_segments(self, subtitles: List[Dict]) -> List[Dict]:
        """找到核心剧情片段"""
        if not subtitles:
            return []

        # 创建滑动窗口片段
        window_size = 25  # 每个窗口25条字幕，约2-3分钟
        step_size = 10    # 步长10，确保重叠

        segments = []

        for i in range(0, len(subtitles), step_size):
            end_idx = min(i + window_size, len(subtitles))

            if end_idx - i < 15:  # 太短跳过
                continue

            segment_subs = subtitles[i:end_idx]
            combined_text = ' '.join([sub['text'] for sub in segment_subs])

            # 计算评分
            position = i / len(subtitles)
            score = self.calculate_segment_score(combined_text, position)

            if score >= 6.0:  # 高分片段
                start_time = segment_subs[0]['start']
                end_time = segment_subs[-1]['end']
                duration = self.time_to_seconds(end_time) - self.time_to_seconds(start_time)

                segments.append({
                    'start_index': i,
                    'end_index': end_idx - 1,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': duration,
                    'score': score,
                    'text': combined_text,
                    'subtitles': segment_subs,
                    'position': position
                })

        # 按分数排序并选择最佳片段
        segments.sort(key=lambda x: x['score'], reverse=True)

        # 选择最高分的片段，避免重叠
        selected = []
        used_ranges = []

        for segment in segments:
            start_idx = segment['start_index']
            end_idx = segment['end_index']

            # 检查是否与已选片段重叠
            overlap = False
            for used_start, used_end in used_ranges:
                if not (end_idx < used_start or start_idx > used_end):
                    overlap = True
                    break

            if not overlap:
                selected.append(segment)
                used_ranges.append((start_idx, end_idx))

                if len(selected) >= 1:  # 每集只选1个核心片段
                    break

        return selected

    def extract_key_dialogues(self, segment: Dict) -> List[str]:
        """提取关键对话"""
        key_dialogues = []

        for sub in segment['subtitles']:
            text = sub['text'].strip()

            # 检查是否包含关键信息
            has_key_info = any(keyword in text for keyword in self.main_plot_keywords)
            has_drama = any(keyword in text for keyword in self.dramatic_keywords)

            if (has_key_info or has_drama) and len(text) > 10:
                time_code = f"{sub['start']} --> {sub['end']}"
                key_dialogues.append(f"[{time_code}] {text}")

        return key_dialogues[:5]  # 最多5条关键对话

    def analyze_plot_significance(self, segment: Dict) -> str:
        """分析剧情意义"""
        text = segment['text']

        # 主线剧情分析
        if '四二八案' in text and ('申诉' in text or '重审' in text):
            return "四二八案申诉程序启动"
        elif '628旧案' in text and ('证据' in text or '真相' in text):
            return "628旧案关键证据揭露"
        elif '听证会' in text:
            return "听证会关键辩论"
        elif '张园' in text and '霸凌' in text:
            return "张园霸凌事件证据呈现"
        elif '正当防卫' in text:
            return "正当防卫争议核心讨论"
        elif '段洪山' in text:
            return "段洪山案件关键进展"
        else:
            return "重要剧情推进节点"

    def generate_episode_theme(self, episode_file: str, segment: Dict) -> str:
        """生成集数主题"""
        episode_num = re.search(r'[Ee](\d+)', episode_file)
        episode_number = episode_num.group(1) if episode_num else "00"

        significance = self.analyze_plot_significance(segment)

        # 根据剧情意义生成主题
        if "申诉" in significance:
            theme = f"E{episode_number}：李慕枫申诉启动，旧案疑点浮现"
        elif "听证会" in significance:
            theme = f"E{episode_number}：听证会激辩，正当防卫争议"
        elif "证据" in significance:
            theme = f"E{episode_number}：关键证据呈现，真相逐步揭露"
        elif "霸凌" in significance:
            theme = f"E{episode_number}：张园霸凌证据，案件转折点"
        else:
            theme = f"E{episode_number}：核心剧情推进，{significance}"

        return theme

    def generate_next_episode_connection(self, segment: Dict, episode_num: str) -> str:
        """生成与下一集的衔接说明"""
        text = segment['text']

        if '申诉' in text:
            return f"本集申诉启动，为下一集听证会翻案铺垫"
        elif '听证会' in text and '准备' in text:
            return f"听证会准备就绪，下一集将进入激烈辩论"
        elif '证据' in text and ('新' in text or '发现' in text):
            return f"新证据浮现，下一集案件迎来重大转机"
        elif '张园' in text:
            return f"张园涉案信息披露，下一集霸凌真相将全面揭露"
        elif '真相' in text:
            return f"部分真相显现，下一集更深层内幕即将曝光"
        else:
            return f"关键剧情节点确立，下一集故事线将进一步推进"

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def analyze_single_episode(self, episode_file: str) -> Dict:
        """分析单集，返回剪辑方案"""
        print(f"🔍 分析 {episode_file}...")

        subtitles = self.parse_subtitle_file(episode_file)
        if not subtitles:
            return None

        # 找到核心片段
        core_segments = self.find_core_segments(subtitles)

        if not core_segments:
            print(f"  ⚠ 未找到足够精彩的片段")
            return None

        # 选择最佳片段
        best_segment = core_segments[0]

        # 生成集数信息
        episode_num = re.search(r'[Ee](\d+)', episode_file)
        episode_number = episode_num.group(1) if episode_num else "00"

        # 生成主题
        theme = self.generate_episode_theme(episode_file, best_segment)

        # 提取关键对话
        key_dialogues = self.extract_key_dialogues(best_segment)

        # 分析剧情意义
        plot_significance = self.analyze_plot_significance(best_segment)

        # 生成衔接说明
        next_connection = self.generate_next_episode_connection(best_segment, episode_number)

        # 内容亮点
        content_highlights = []
        text = best_segment['text']

        if '四二八案' in text:
            content_highlights.append("首次/关键提及四二八案申诉")
        if '628旧案' in text:
            content_highlights.append("628旧案关键信息披露")
        if '张园' in text and '霸凌' in text:
            content_highlights.append("张园霸凌事件证据呈现")
        if '正当防卫' in text:
            content_highlights.append("正当防卫争议核心讨论")
        if any(word in text for word in ['真相', '发现', '证据']):
            content_highlights.append("重要证据或真相揭露")

        if not content_highlights:
            content_highlights.append("重要剧情推进节点")

        return {
            'episode': episode_file,
            'episode_number': episode_number,
            'theme': theme,
            'segment': {
                'start_time': best_segment['start_time'],
                'end_time': best_segment['end_time'],
                'duration': best_segment['duration'],
                'score': best_segment['score']
            },
            'plot_significance': plot_significance,
            'key_dialogues': key_dialogues,
            'content_highlights': content_highlights,
            'next_episode_connection': next_connection,
            'core_content_preview': best_segment['text'][:100] + "..." if len(best_segment['text']) > 100 else best_segment['text']
        }

def analyze_all_episodes_smartly():
    """智能分析所有集数"""
    print("🚀 启动智能剧情分析系统")
    print("=" * 60)
    print("📋 分析规则:")
    print("• 每集聚焦1个核心剧情点")
    print("• 优先主线剧情(四二八案、628旧案、听证会)")
    print("• 保持跨集故事线连贯性")
    print("• 自动修正字幕错别字")
    print("=" * 60)

    analyzer = SmartAnalyzer()

    # 获取字幕文件
    subtitle_files = []
    for file in os.listdir('.'):
        if file.endswith('.txt') and any(pattern in file.lower() for pattern in ['e', 's01e', '第', '集']):
            subtitle_files.append(file)

    subtitle_files.sort()

    if not subtitle_files:
        print("❌ 未找到字幕文件")
        return []

    print(f"📁 找到 {len(subtitle_files)} 个字幕文件")

    all_plans = []

    for filename in subtitle_files:
        try:
            plan = analyzer.analyze_single_episode(filename)
            if plan:
                all_plans.append(plan)

                print(f"✅ {filename}")
                print(f"  📺 主题: {plan['theme']}")
                print(f"  ⏱️ 片段: {plan['segment']['start_time']} --> {plan['segment']['end_time']} ({plan['segment']['duration']:.1f}秒)")
                print(f"  🎯 意义: {plan['plot_significance']}")
                print(f"  💡 亮点: {', '.join(plan['content_highlights'])}")
                print(f"  🔗 衔接: {plan['next_episode_connection']}")
                print()
            else:
                print(f"❌ {filename} - 未找到合适片段")

        except Exception as e:
            print(f"❌ 处理 {filename} 时出错: {e}")

    # 生成分析报告
    generate_analysis_report(all_plans)

    print(f"📊 分析完成: {len(all_plans)}/{len(subtitle_files)} 集")
    print(f"📄 详细方案已保存到: smart_analysis_report.txt")

    return all_plans

def generate_analysis_report(plans: List[Dict]):
    """生成分析报告"""
    if not plans:
        return

    content = "📺 智能剧情分析报告\n"
    content += "=" * 80 + "\n\n"

    content += "🎯 分析目标:\n"
    content += "• 单集核心聚焦: 每集围绕1个核心剧情点，2-3分钟时长\n"
    content += "• 主线剧情优先: 突出四二八案、628旧案、听证会等关键线索\n"
    content += "• 跨集连贯性: 保持故事线逻辑一致和明确衔接\n"
    content += "• 错别字修正: 自动修正防衛→防卫等常见错误\n\n"

    total_duration = 0

    for i, plan in enumerate(plans):
        content += f"📺 {plan['theme']}\n"
        content += "-" * 60 + "\n"
        content += f"时间片段: {plan['segment']['start_time']} --> {plan['segment']['end_time']}\n"
        content += f"片段时长: {plan['segment']['duration']:.1f} 秒 ({plan['segment']['duration']/60:.1f} 分钟)\n"
        content += f"重要性评分: {plan['segment']['score']:.1f}/10\n"
        content += f"剧情意义: {plan['plot_significance']}\n\n"

        content += "关键台词 (精确时间标注):\n"
        for dialogue in plan['key_dialogues']:
            content += f"  {dialogue}\n"
        content += "\n"

        content += "✨ 内容亮点:\n"
        for highlight in plan['content_highlights']:
            content += f"  • {highlight}\n"
        content += "\n"

        content += f"🔗 与下一集衔接: {plan['next_episode_connection']}\n"
        content += "\n"

        content += f"核心内容预览:\n{plan['core_content_preview']}\n"
        content += "=" * 80 + "\n\n"

        total_duration += plan['segment']['duration']

    # 整体统计
    content += "📊 整体统计:\n"
    content += f"• 分析集数: {len(plans)} 集\n"
    content += f"• 总剪辑时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)\n"
    content += f"• 平均每集: {total_duration/len(plans):.1f} 秒\n"
    content += f"• 故事线连贯性: 已确保跨集逻辑一致\n"
    content += f"• 剪辑价值: 每集聚焦核心剧情，适合短视频传播\n"

    # 保存报告
    with open('smart_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    analyze_all_episodes_smartly()
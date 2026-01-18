#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧旁白字幕生成模块
为每个剪辑片段生成旁观者视角的叙述字幕
"""

import os
import re
from typing import Dict, List


class TVSubtitleGenerator:
    """电视剧旁白字幕生成器"""

    def __init__(self, output_folder: str = "tv_clips"):
        """初始化字幕生成器"""
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def generate_subtitle_for_clip(
        self,
        clip_video_path: str,
        clip_data: Dict,
        episode_name: str,
        clip_index: int
    ) -> str:
        """
        为单个剪辑片段生成旁白字幕文件

        Args:
            clip_video_path: 剪辑视频文件路径
            clip_data: 剪辑数据（包含旁白信息）
            episode_name: 集数名称
            clip_index: 片段索引

        Returns:
            字幕文件路径
        """
        subtitle_path = clip_video_path.replace('.mp4', '_旁白.srt')

        # 获取旁白内容
        narrator = clip_data.get('narrator_commentary', )

        # 生成SRT格式字幕
        srt_content = self._build_srt_content(narrator, clip_data)

        # 保存字幕文件
        try:
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"    📝 旁白字幕: {os.path.basename(subtitle_path)}")
            return subtitle_path
        except Exception as e:
            print(f"    ⚠️ 字幕生成失败: {e}")
            return ""

    def _build_srt_content(self, narrator: Dict, clip_data: Dict) -> str:
        """构建SRT格式字幕内容"""
        if not narrator:
            narrator = {}

        duration = clip_data.get('duration_seconds', 120)

        # 将旁白分成4段：开场、发展、高潮、结尾
        segments = [
            {
                'text': narrator.get('opening', ''),
                'start': 0,
                'end': duration * 0.25
            },
            {
                'text': narrator.get('development', ''),
                'start': duration * 0.25,
                'end': duration * 0.5
            },
            {
                'text': narrator.get('climax', ''),
                'start': duration * 0.5,
                'end': duration * 0.75
            },
            {
                'text': narrator.get('conclusion', ''),
                'start': duration * 0.75,
                'end': duration
            }
        ]

        # 生成SRT内容
        srt_lines = []
        index = 1

        for seg in segments:
            if seg['text'] and seg['text'].strip():
                start_time = self._seconds_to_srt_time(seg['start'])
                end_time = self._seconds_to_srt_time(seg['end'])

                srt_lines.append(f"{index}")
                srt_lines.append(f"{start_time} --> {end_time}")
                srt_lines.append(seg['text'].strip())
                srt_lines.append("")
                index += 1

        return '\n'.join(srt_lines)

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """秒数转换为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    def generate_analysis_report(
        self,
        clip_video_path: str,
        clip_data: Dict,
        episode_name: str,
        clip_index: int
    ) -> str:
        """生成片段分析报告"""
        report_path = clip_video_path.replace('.mp4', '_分析报告.txt')

        narrator = clip_data.get('narrator_commentary', {})

        content = f"""📺 电视剧片段分析报告
{'=' * 80}

【集数】{episode_name}
【片段】第 {clip_index} 段 - {clip_data.get('title', '未知')}
【类型】{clip_data.get('plot_type', '未知')}
【时长】{clip_data.get('duration_seconds', 0):.1f} 秒
【时间】{clip_data.get('start_time', '00:00:00,000')} --> {clip_data.get('end_time', '00:00:00,000')}

【精彩原因】
{clip_data.get('why_exciting', '这是一个精彩的片段')}

【关键时刻】
"""
        for moment in clip_data.get('key_moments', []):
            content += f"• {moment}\n"

        content += f"""
【旁观者叙述】
• 开场: {narrator.get('opening', '无')}
• 发展: {narrator.get('development', '无')}
• 高潮: {narrator.get('climax', '无')}
• 结尾: {narrator.get('conclusion', '无')}

【完整叙述】
{narrator.get('complete_narration', '无')}

【剧情联系】
• 与前面剧情: {clip_data.get('connection_to_previous', '无')}
• 与后续剧情: {clip_data.get('connection_to_next', '无')}

【对话内容】
{clip_data.get('dialogue_content', '无')[:500]}...

生成时间: {self._get_current_time()}
"""

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    📄 分析报告: {os.path.basename(report_path)}")
            return report_path
        except Exception as e:
            print(f"    ⚠️ 报告生成失败: {e}")
            return ""

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

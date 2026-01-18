#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI分析器模块 - 专门处理AI相关分析功能
"""

import json
from typing import Dict, Optional

class AIAnalyzer:
    """AI分析器类"""

    def __init__(self):
        pass

    def generate_srt_narration(self, narration_data: Dict, duration: int) -> str:
        """生成SRT格式的旁白字幕"""
        try:
            # 安全获取旁白内容
            if isinstance(narration_data, dict):
                narration_text = narration_data.get('full_narration', 
                                                  narration_data.get('full_script', '专业旁白解说'))
            else:
                narration_text = str(narration_data) if narration_data else '专业旁白解说'

            # 限制时长在合理范围内
            duration = min(max(duration, 10), 300)  # 10秒到5分钟

            # 将旁白分段
            sentences = self._split_narration(narration_text)

            srt_content = ""
            current_time = 0
            segment_duration = max(duration // len(sentences), 3) if sentences else duration

            for i, sentence in enumerate(sentences, 1):
                start_time = current_time
                end_time = min(current_time + segment_duration, duration)

                srt_content += f"""{i}
{self._seconds_to_srt_time(start_time)} --> {self._seconds_to_srt_time(end_time)}
{sentence.strip()}

"""
                current_time = end_time

                if current_time >= duration:
                    break

            return srt_content

        except Exception as e:
            # 返回基础SRT内容
            return f"""1
00:00:00,000 --> 00:00:05,000
精彩片段开始

2
00:00:05,000 --> 00:{min(duration//60, 99):02d}:{duration%60:02d},000
精彩内容正在播放
"""

    def _split_narration(self, text: str) -> list:
        """将旁白文本分割成合适的段落"""
        if not text or len(text.strip()) < 10:
            return ["精彩内容正在播放"]

        # 按句号、感叹号、问号分割
        import re
        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 如果句子太少，按逗号进一步分割
        if len(sentences) < 3:
            all_parts = []
            for sentence in sentences:
                parts = re.split(r'[，,]', sentence)
                all_parts.extend([p.strip() for p in parts if p.strip()])
            sentences = all_parts

        # 限制最大句子数量
        return sentences[:8] if sentences else ["精彩内容正在播放"]

    def _seconds_to_srt_time(self, seconds: int) -> str:
        """将秒数转换为SRT时间格式"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d},000"
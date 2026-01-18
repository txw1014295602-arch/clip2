#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
旁白生成器 - 为短视频生成专业旁白内容
"""

import os
import re
from typing import Dict, List, Optional
from api_config_helper import config_helper

class NarrationGenerator:
    def __init__(self):
        self.config = config_helper.load_config()
        self.enabled = self.config.get('enabled', False)

        # 旁白模板
        self.templates = {
            'legal': {
                'intro': "在这个法律剧情中，",
                'tension': "法庭上的激烈辩论",
                'climax': "真相即将大白",
                'outro': "正义与法律的较量令人深思"
            },
            'romance': {
                'intro': "在这个感人的情感片段中，",
                'tension': "两人之间的情感纠葛",
                'climax': "情感达到高潮",
                'outro': "爱情的力量让人动容"
            },
            'crime': {
                'intro': "在这个紧张的犯罪片段中，",
                'tension': "案件调查的关键时刻",
                'climax': "线索逐渐浮现",
                'outro': "真相背后的故事引人深思"
            },
            'family': {
                'intro': "在这个温馨的家庭片段中，",
                'tension': "家庭关系的微妙变化",
                'climax': "亲情的力量显现",
                'outro': "家庭的温暖让人感动"
            },
            'general': {
                'intro': "在这个精彩的片段中，",
                'tension': "剧情的紧张发展",
                'climax': "情节达到高潮",
                'outro': "精彩的表演令人印象深刻"
            }
        }

    def generate_professional_narration(self, clip_analysis: Dict, episode_context: str = "") -> Dict:
        """生成专业旁白"""
        title = clip_analysis.get('video_title', '精彩片段')
        segment_type = clip_analysis.get('segment_type', 'general')
        highlights = clip_analysis.get('highlights', [])
        hook_reason = clip_analysis.get('hook_reason', '')

        # 获取对应模板
        template = self.templates.get(segment_type, self.templates['general'])

        # 如果启用AI，使用AI生成更精准的旁白
        if self.enabled:
            ai_narration = self._generate_ai_narration(clip_analysis, episode_context)
            if ai_narration:
                return ai_narration

        # 使用模板生成旁白
        return self._generate_template_narration(clip_analysis, template)

    def _generate_ai_narration(self, clip_analysis: Dict, episode_context: str) -> Optional[Dict]:
        """使用AI生成旁白"""
        try:
            segment = clip_analysis['original_segment']
            title = clip_analysis.get('video_title', '精彩片段')
            highlights = clip_analysis.get('highlights', [])
            hook_reason = clip_analysis.get('hook_reason', '')

            # 截取部分原始内容
            original_content = segment['full_text'][:200]

            prompt = f"""你是专业的短视频旁白解说员，需要为这个电视剧精彩片段生成旁白。

片段信息：
- 标题：{title}
- 吸引点：{hook_reason}
- 精彩亮点：{', '.join(highlights[:3])}
- 剧集背景：{episode_context}
- 部分内容：{original_content}

请生成专业的旁白解说，包含：
1. 开场白（2-3秒）：简要介绍片段
2. 过程解说（3-5秒）：解释正在发生的事情
3. 亮点强调（2-3秒）：强调最精彩的部分
4. 结尾（1-2秒）：总结或展望

要求：
- 语言生动有趣，吸引观众
- 总时长控制在8-12秒内
- 避免剧透，保持悬念
- 语言通俗易懂

请以JSON格式返回：
{{
    "opening": "开场白文本",
    "process": "过程解说文本", 
    "highlight": "亮点强调文本",
    "ending": "结尾文本",
    "full_narration": "完整旁白文本",
    "timing": {{
        "opening": [0, 3],
        "process": [3, 8],
        "highlight": [8, 11],
        "ending": [11, 12]
    }}
}}"""

            response = self._call_ai_api(prompt)
            if response:
                return self._parse_narration_response(response)

        except Exception as e:
            print(f"AI旁白生成失败: {e}")

        return None

    def _generate_template_narration(self, clip_analysis: Dict, template: Dict) -> Dict:
        """使用模板生成旁白"""
        title = clip_analysis.get('video_title', '精彩片段')
        highlights = clip_analysis.get('highlights', [])
        hook_reason = clip_analysis.get('hook_reason', '')

        # 构建旁白内容
        opening = f"{template['intro']}{title}正在上演。"

        process = f"我们看到{template['tension']}，"
        if highlights:
            process += f"特别是{highlights[0]}的部分。"
        else:
            process += "剧情紧张刺激。"

        highlight = f"最精彩的是{template['climax']}，"
        if hook_reason:
            highlight += f"{hook_reason}。"
        else:
            highlight += "让人印象深刻。"

        ending = f"{template['outro']}。"

        full_narration = f"{opening} {process} {highlight} {ending}"

        return {
            "opening": opening,
            "process": process,
            "highlight": highlight,
            "ending": ending,
            "full_narration": full_narration,
            "timing": {
                "opening": [0, 3],
                "process": [3, 8],
                "highlight": [8, 11],
                "ending": [11, 12]
            }
        }

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        try:
            import requests

            if self.config['provider'] == 'gemini':
                return self._call_gemini_api(prompt)
            elif self.config['provider'] == 'qwen':
                return self._call_qwen_api(prompt)
            elif self.config['provider'] == 'doubao':
                return self._call_doubao_api(prompt)
            else:
                return self._call_standard_api(prompt)

        except Exception as e:
            print(f"API调用失败: {e}")
            return None

    def _call_standard_api(self, prompt: str) -> Optional[str]:
        """调用标准API（支持OpenRouter等新服务商）"""
        try:
            return config_helper.call_ai_api(prompt, self.config)
        except Exception as e:
            print(f"旁白生成API调用失败: {e}")
            return None

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """调用Gemini API"""
        try:
            import requests

            url = f"https://generativelanguage.googleapis.com/v1/models/{self.config['model']}:generateContent?key={self.config['api_key']}"

            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 500,
                    "temperature": 0.7
                }
            }

            response = requests.post(url, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            else:
                return None

        except Exception as e:
            return None

    def _call_qwen_api(self, prompt: str) -> Optional[str]:
        """调用通义千问API"""
        try:
            import requests

            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': self.config['model'],
                'input': {'prompt': prompt},
                'parameters': {
                    'max_tokens': 500,
                    'temperature': 0.7
                }
            }

            response = requests.post(self.config['url'], headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('output', {}).get('text', '')
            else:
                return None

        except Exception as e:
            return None

    def _call_doubao_api(self, prompt: str) -> Optional[str]:
        """调用豆包API"""
        try:
            import requests

            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': self.config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是专业的短视频旁白解说员。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 500,
                'temperature': 0.7
            }

            response = requests.post(self.config['url'], headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                return None

        except Exception as e:
            return None

    def _parse_narration_response(self, response_text: str) -> Dict:
        """解析旁白响应"""
        try:
            import json

            # 提取JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]

            response = json.loads(response_text)

            opening = response.get('opening', '')
            process = response.get('process', '')
            highlight = response.get('highlight', '')
            ending = response.get('ending', '')
            full_narration = response.get('full_narration', '')
            timing = response.get('timing', {})

            return {
                "opening": opening,
                "process": process,
                "highlight": highlight,
                "ending": ending,
                "full_narration": full_narration,
                "timing": timing
            }

        except Exception as e:
            print(f"旁白解析失败: {e}")
            return {}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧AI分析模块
支持完整剧情分析、缓存机制、跨集连贯性
"""

import os
import json
import hashlib
from typing import Dict, List, Optional


class TVAIAnalyzer:
    """电视剧AI分析器 - 支持缓存和跨集连贯"""

    def __init__(self, ai_config: Dict, cache_folder: str = "tv_cache"):
        """初始化AI分析器"""
        self.ai_config = ai_config
        self.cache_folder = cache_folder
        os.makedirs(cache_folder, exist_ok=True)

    def analyze_episode(
        self,
        episode_name: str,
        subtitles: List[Dict],
        previous_context: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        分析单集电视剧

        Args:
            episode_name: 集数名称
            subtitles: 字幕列表
            previous_context: 上一集的衔接信息

        Returns:
            分析结果（包含剪辑点、旁白、衔接信息）
        """
        # 检查缓存
        cache_path = self._get_cache_path(episode_name, subtitles)
        cached_analysis = self._load_cache(cache_path)

        if cached_analysis:
            print(f"💾 使用缓存的AI分析结果")
            return cached_analysis

        # 调用AI分析
        print(f"🤖 AI分析中: {episode_name}")
        analysis = self._call_ai_for_analysis(episode_name, subtitles, previous_context)

        if not analysis:
            print(f"❌ AI分析失败，直接返回")
            return None

        # 保存缓存
        self._save_cache(cache_path, analysis)
        return analysis

    def _get_cache_path(self, episode_name: str, subtitles: List[Dict]) -> str:
        """生成缓存路径（确保一致性）"""
        # 使用字幕内容哈希确保相同字幕得到相同结果
        content_for_hash = json.dumps(
            [s['text'] for s in subtitles[:100]],  # 使用前100条字幕生成哈希
            ensure_ascii=False,
            sort_keys=True
        )
        content_hash = hashlib.md5(content_for_hash.encode()).hexdigest()[:16]

        safe_name = episode_name.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_folder, f"analysis_{safe_name}_{content_hash}.json")

    def _load_cache(self, cache_path: str) -> Optional[Dict]:
        """加载缓存"""
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 缓存加载失败: {e}")
        return None

    def _save_cache(self, cache_path: str, analysis: Dict) -> bool:
        """保存缓存"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"💾 AI分析结果已缓存")
            return True
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")
            return False

    def _call_ai_for_analysis(
        self,
        episode_name: str,
        subtitles: List[Dict],
        previous_context: Optional[Dict]
    ) -> Optional[Dict]:
        """调用AI进行完整剧情分析"""
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置")
            return None

        # 构建完整对话内容
        full_dialogue = self._build_full_dialogue(subtitles)

        # 构建AI提示词
        prompt = self._build_analysis_prompt(episode_name, full_dialogue, previous_context)

        # 调用AI API
        try:
            response = self._call_ai_api(prompt)
            if not response:
                return None

            # 解析AI响应
            analysis = self._parse_ai_response(response)
            return analysis

        except Exception as e:
            print(f"❌ AI调用异常: {e}")
            return None

    def _build_full_dialogue(self, subtitles: List[Dict]) -> str:
        """构建完整对话内容"""
        dialogue_lines = []
        for sub in subtitles:
            time_str = sub['start_time']
            text = sub['text']
            dialogue_lines.append(f"[{time_str}] {text}")

        return '\n'.join(dialogue_lines)

    def _build_analysis_prompt(
        self,
        episode_name: str,
        full_dialogue: str,
        previous_context: Optional[Dict]
    ) -> str:
        """构建AI分析提示词"""

        # 上一集衔接信息
        context_section = ""
        if previous_context:
            context_section = f"""
【上一集衔接信息】
主线剧情: {previous_context.get('main_storyline', '无')}
关键人物: {', '.join(previous_context.get('key_characters', []))}
未解决线索: {', '.join(previous_context.get('unresolved_clues', []))}
下集预告: {previous_context.get('next_episode_hint', '无')}
"""

        prompt = f"""你是世界顶级的电视剧分析大师。请对这集电视剧进行100% AI驱动的深度分析。

【集数】{episode_name}
{context_section}

【完整对话内容】
{full_dialogue[:15000]}

请完成以下任务：

1. **剧情理解** - 深度理解本集完整剧情，识别关键剧情点
2. **精彩片段识别** - 找出3-8个最精彩的片段（关键冲突、人物转折、线索揭露等）
3. **剪辑点规划** - 每个片段必须保证对话完整，不能在句子中间截断
4. **旁观者叙述** - 为每个片段生成详细的旁观者视角叙述（第三人称）
5. **跨集连贯** - 分析本集与下一集的衔接点

返回JSON格式：
{{
    "episode_name": "{episode_name}",
    "analysis_status": "success",
    "main_storyline": "本集主线剧情概述",
    "key_characters": ["角色1", "角色2", "角色3"],
    "story_summary": "本集完整故事总结",

    "highlight_clips": [
        {{
            "clip_id": 1,
            "title": "片段标题",
            "plot_type": "剧情点类型（冲突/转折/揭露/高潮等）",
            "start_time": "开始时间(HH:MM:SS,mmm)",
            "end_time": "结束时间(HH:MM:SS,mmm)",
            "duration_seconds": 实际秒数,
            "dialogue_content": "这段时间内的完整对话内容",
            "narrator_commentary": {{
                "opening": "开场旁白（介绍背景）",
                "development": "发展旁白（解释过程）",
                "climax": "高潮旁白（强调重点）",
                "conclusion": "结尾旁白（总结意义）",
                "complete_narration": "完整连贯的旁观者叙述"
            }},
            "why_exciting": "为什么这段精彩",
            "key_moments": ["关键时刻1", "关键时刻2"],
            "connection_to_previous": "与前面剧情的联系",
            "connection_to_next": "与后续剧情的联系"
        }}
    ],

    "next_episode_connection": {{
        "main_storyline": "主线剧情进展",
        "unresolved_clues": ["未解决的线索1", "未解决的线索2"],
        "character_status": "主要角色当前状态",
        "next_episode_hint": "下一集衔接点说明"
    }},

    "content_highlights": "本集内容亮点总结",
    "editing_notes": "剪辑注意事项"
}}

分析要求：
1. 必须100% AI判断，不使用任何预设规则
2. 剪辑点必须保证对话完整，不能在句子中间截断
3. 旁观者叙述要详细清晰，帮助观众理解剧情
4. 所有短视频合起来能完整叙述本集剧情
5. 如果有反转等特殊情况，需要在旁白中联系前面的剧情
6. 如果无法充分分析，请返回分析失败状态"""

        return prompt

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        config = self.ai_config

        try:
            if config.get('api_type') == 'official':
                return self._call_gemini_official(prompt, config)
            else:
                return self._call_proxy_api(prompt, config)
        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            return None

    def _call_gemini_official(self, prompt: str, config: Dict) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai

            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'],
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return None

    def _call_proxy_api(self, prompt: str, config: Dict) -> Optional[str]:
        """调用中转API（OpenAI兼容）"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )

            response = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {'role': 'system', 'content': '你是专业的电视剧分析师，必须进行100% AI驱动的深度分析。严格按照JSON格式返回。'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=8000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"中转API调用失败: {e}")
            return None

    def _parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON内容
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                else:
                    return None

            analysis = json.loads(json_str)

            # 验证必要字段
            if analysis.get('analysis_status') != 'success':
                print("❌ AI分析状态不是success")
                return None

            if not analysis.get('highlight_clips'):
                print("❌ 没有找到精彩片段")
                return None

            print(f"✅ AI分析成功，找到 {len(analysis['highlight_clips'])} 个精彩片段")
            return analysis

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析错误: {e}")
            return None


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能字幕分析器 - 多剧情类型自适应分析
"""

import os
import re
import json
import requests
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from clip_rules import ClipRules

# 平台兼容性修复
try:
    from platform_fix import fix_encoding, safe_file_read, safe_file_write
    fix_encoding()
except ImportError:
    def safe_file_read(filepath, encoding='utf-8'):
        with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
            return f.read()

    def safe_file_write(filepath, content, encoding='utf-8'):
        with open(filepath, 'w', encoding=encoding, errors='ignore') as f:
            f.write(content)

class IntelligentSubtitleAnalyzer:
    def __init__(self, use_ai_analysis: bool = True, api_key: Optional[str] = None):
        self.use_ai_analysis = use_ai_analysis
        self.api_key = api_key

        # 智能剧情类型识别
        self.genre_patterns = {
            'legal': {
                'keywords': ['法官', '检察官', '律师', '法庭', '审判', '证据', '案件', '起诉', '辩护', '判决', '申诉', '听证会'],
                'weight': 1.0
            },
            'crime': {
                'keywords': ['警察', '犯罪', '嫌疑人', '调查', '破案', '线索', '凶手', '案发', '侦探', '刑侦', '追踪', '逮捕'],
                'weight': 1.0
            },
            'medical': {
                'keywords': ['医生', '护士', '医院', '手术', '病人', '诊断', '治疗', '病情', '急诊', '救护车', '药物', '病房'],
                'weight': 1.0
            },
            'romance': {
                'keywords': ['爱情', '喜欢', '心动', '表白', '约会', '分手', '复合', '结婚', '情侣', '恋人', '暗恋', '初恋'],
                'weight': 1.0
            },
            'family': {
                'keywords': ['家庭', '父母', '孩子', '兄弟', '姐妹', '亲情', '家人', '团聚', '离别', '成长', '教育', '代沟'],
                'weight': 1.0
            },
            'business': {
                'keywords': ['公司', '老板', '员工', '合作', '竞争', '项目', '会议', '谈判', '投资', '创业', '职场', '晋升'],
                'weight': 1.0
            },
            'historical': {
                'keywords': ['皇帝', '大臣', '朝廷', '战争', '将军', '士兵', '王朝', '宫廷', '政治', '权力', '叛乱', '起义'],
                'weight': 1.0
            },
            'fantasy': {
                'keywords': ['魔法', '武功', '修炼', '仙人', '妖怪', '神话', '传说', '法术', '灵力', '异能', '穿越', '重生'],
                'weight': 1.0
            }
        }

        # 通用戏剧张力标识词
        self.universal_dramatic_keywords = [
            '突然', '忽然', '没想到', '原来', '居然', '竟然', '震惊', '惊讶', '意外', '发现',
            '真相', '秘密', '隐瞒', '揭露', '暴露', '爆发', '冲突', '对抗', '争吵', '反转',
            '危险', '紧急', '救命', '帮助', '拯救', '逃跑', '追逐', '打斗', '生死', '关键'
        ]

        # 通用情感爆发点标识
        self.universal_emotional_markers = [
            '哭', '笑', '喊', '叫', '怒', '气', '激动', '兴奋', '紧张', '害怕', '担心', '焦虑',
            '开心', '高兴', '悲伤', '难过', '痛苦', '绝望', '希望', '感动', '温暖', '失望',
            '愤怒', '生气', '暴怒', '崩溃', '颤抖', '心跳', '呼吸', '眼泪', '微笑', '拥抱'
        ]

        # 对话强度标识
        self.dialogue_intensity_markers = [
            '！', '？', '...', '啊', '呀', '哦', '唉', '哎', '嗯', '呢', '吧', '吗', '咦', '哇'
        ]

        # 动态调整权重
        self.adaptive_weights = {
            'genre_match': 5.0,
            'dramatic_tension': 3.0,
            'emotional_intensity': 2.0,
            'dialogue_richness': 1.5,
            'character_development': 2.5,
            'plot_advancement': 4.0
        }

        # 自动识别的剧情类型
        self.detected_genre = None
        self.genre_confidence = 0.0

    def detect_genre(self, all_subtitles: List[Dict]) -> str:
        """智能识别剧情类型"""
        genre_scores = {}
        total_text = " ".join([sub['text'] for sub in all_subtitles[:200]])  # 分析前200条字幕

        for genre, pattern in self.genre_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                score += total_text.count(keyword) * pattern['weight']
            genre_scores[genre] = score

        # 找出最匹配的类型
        if genre_scores:
            best_genre = max(genre_scores, key=genre_scores.get)
            max_score = genre_scores[best_genre]

            if max_score > 5:  # 足够的匹配度
                self.detected_genre = best_genre
                self.genre_confidence = min(max_score / 50, 1.0)  # 归一化信心度
                return best_genre

        return 'general'  # 通用类型

    def get_genre_specific_keywords(self, genre: str) -> List[str]:
        """获取特定类型的关键词"""
        if genre in self.genre_patterns:
            return self.genre_patterns[genre]['keywords']
        return []

    def parse_subtitle_file(self, filepath: str) -> List[Dict]:
        """解析字幕文件，自动修正常见错别字"""
        content = safe_file_read(filepath)

        # 通用错别字修正
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '設計': '设计', '開始': '开始', '結束': '结束',
            '問題': '问题', '機會': '机会', '決定': '决定', '選擇': '选择'
        }

        for old, new in corrections.items():
            content = content.replace(old, new)

        # 分割字幕块
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

    def calculate_intelligent_score(self, text: str, context: Dict = None) -> float:
        """智能评分算法 - 自适应不同剧情类型"""

        # 基础规则评分
        rule_score = self._calculate_adaptive_rule_score(text, context)

        # 如果启用AI分析，获取AI评分
        if self.use_ai_analysis:
            ai_score = self._calculate_ai_score(text, context)
            if ai_score > 0:
                # 动态混合评分
                rule_weight = 0.4 if self.genre_confidence > 0.7 else 0.6
                ai_weight = 1 - rule_weight
                final_score = rule_score * rule_weight + ai_score * ai_weight
                return final_score

        return rule_score

    def _calculate_adaptive_rule_score(self, text: str, context: Dict = None) -> float:
        """自适应规则评分"""
        score = 0

        # 类型匹配评分
        if self.detected_genre:
            genre_keywords = self.get_genre_specific_keywords(self.detected_genre)
            for keyword in genre_keywords:
                if keyword in text:
                    score += self.adaptive_weights['genre_match'] * self.genre_confidence

        # 通用戏剧张力评分
        for keyword in self.universal_dramatic_keywords:
            if keyword in text:
                score += self.adaptive_weights['dramatic_tension']

        # 情感强度评分
        for emotion in self.universal_emotional_markers:
            if emotion in text:
                score += self.adaptive_weights['emotional_intensity']

        # 对话丰富度
        for marker in self.dialogue_intensity_markers:
            score += text.count(marker) * self.adaptive_weights['dialogue_richness']

        # 文本长度和质量
        text_length = len(text)
        if 15 <= text_length <= 200:
            score += 2
        elif text_length > 200:
            score += 1

        # 角色发展标识
        character_indicators = ['决定', '选择', '改变', '成长', '领悟', '明白', '坚持', '放弃']
        for indicator in character_indicators:
            if indicator in text:
                score += self.adaptive_weights['character_development']

        # 剧情推进标识
        plot_indicators = ['然后', '接着', '随后', '突然', '这时', '结果', '最终', '终于']
        for indicator in plot_indicators:
            if indicator in text:
                score += self.adaptive_weights['plot_advancement']

        return score

    def _calculate_ai_score(self, text: str, context: Dict = None) -> float:
        """使用AI模型评估剧情重要性 - 支持多种模型"""
        try:
            from api_config_helper import config_helper
            
            config = config_helper.load_config()
            if not config.get('enabled') or not config.get('api_key'):
                return 0.0

            if len(text) < 10:
                return 0.0
            if len(text) > 500:
                text = text[:500] + "..."

            # 动态生成提示词
            genre_context = f"这是一部{self.detected_genre}类型的电视剧" if self.detected_genre else "这是一部电视剧"

            prompt = f"""你是专业的电视剧剪辑师，专注于识别精彩片段。

{genre_context}，请评估以下对话片段的剪辑价值：
"{text}"

评估标准：
1. 剧情重要性(0-2分)：是否推进主要故事线，包含关键信息
2. 戏剧张力(0-2分)：是否包含冲突、转折、意外发现
3. 情感共鸣(0-2分)：是否引发观众情感反应，有感人或震撼时刻
4. 角色发展(0-2分)：是否展现角色成长、关系变化、重要决定
5. 观众吸引力(0-2分)：是否制造悬念、幽默、紧张感

请根据以上标准给出0-10分的综合评分。
只需要输出数字，例如：8.5"""

            # 根据不同API提供商构建请求
            provider = config.get('provider', 'openai')
            
            if provider == 'gemini':
                return self._call_gemini_api(config, prompt)
            elif provider == 'qwen':
                return self._call_qwen_api(config, prompt)
            elif provider == 'doubao':
                return self._call_doubao_api(config, prompt)
            else:
                return self._call_standard_api(config, prompt)

        except Exception as e:
            return 0.0

    def _call_gemini_api(self, config: Dict, prompt: str) -> float:
        """调用Gemini API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/{config['model']}:generateContent?key={config['api_key']}"
            
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 20,
                    "temperature": 0.2
                }
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                score_match = re.search(r'(\d+\.?\d*)', text.strip())
                if score_match:
                    return min(max(float(score_match.group(1)), 0), 10)
            
            return 0.0
            
        except Exception:
            return 0.0

    def _call_qwen_api(self, config: Dict, prompt: str) -> float:
        """调用通义千问API"""
        try:
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'input': {'prompt': prompt},
                'parameters': {
                    'max_tokens': 20,
                    'temperature': 0.2
                }
            }
            
            response = requests.post(config['url'], headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('output', {}).get('text', '').strip()
                score_match = re.search(r'(\d+\.?\d*)', text)
                if score_match:
                    return min(max(float(score_match.group(1)), 0), 10)
            
            return 0.0
            
        except Exception:
            return 0.0

    def _call_doubao_api(self, config: Dict, prompt: str) -> float:
        """调用豆包API"""
        try:
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是专业的电视剧剪辑师，专注于评估片段的剪辑价值。请严格按照评分标准给出0-10分的数字评分。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 20,
                'temperature': 0.2
            }
            
            response = requests.post(config['url'], headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                score_match = re.search(r'(\d+\.?\d*)', text)
                if score_match:
                    return min(max(float(score_match.group(1)), 0), 10)
            
            return 0.0
            
        except Exception:
            return 0.0

    def _call_standard_api(self, config: Dict, prompt: str) -> float:
        """调用标准OpenAI格式API"""
        try:
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是专业的电视剧剪辑师，专注于评估片段的剪辑价值。请严格按照评分标准给出0-10分的数字评分。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 20,
                'temperature': 0.2
            }
            
            response = requests.post(config['url'], headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                score_match = re.search(r'(\d+\.?\d*)', text)
                if score_match:
                    return min(max(float(score_match.group(1)), 0), 10)
            else:
                print(f"⚠ API调用失败: {response.status_code} - {response.text}")
            
            return 0.0
            
        except requests.exceptions.RequestException as e:
            print(f"⚠ 网络请求错误: {e}")
            return 0.0
        except Exception as e:
            print(f"⚠ API调用异常: {e}")
            return 0.0

    def identify_smart_segments(self, subtitles: List[Dict]) -> List[Dict]:
        """智能识别精彩片段"""
        high_relevance_segments = []

        # 智能阈值调整 - 针对短视频优化
        base_threshold = 5.0  # 降低基础阈值，获取更多精彩片段
        if self.detected_genre in ['crime', 'legal']:
            threshold = base_threshold - 1.5  # 法律剧精彩片段较多
        elif self.detected_genre in ['romance', 'family']:
            threshold = base_threshold - 1.0  # 情感剧也需要更多片段
        else:
            threshold = base_threshold

        for i, subtitle in enumerate(subtitles):
            # 构建上下文
            context = {
                'position': i / len(subtitles),  # 在剧集中的位置
                'prev_text': subtitles[i-1]['text'] if i > 0 else '',
                'next_text': subtitles[i+1]['text'] if i < len(subtitles)-1 else '',
                'genre': self.detected_genre
            }

            score = self.calculate_intelligent_score(subtitle['text'], context)
            if score >= threshold:
                high_relevance_segments.append({
                    'index': i,
                    'subtitle': subtitle,
                    'score': score,
                    'context': context
                })

        # 按分数排序
        high_relevance_segments.sort(key=lambda x: x['score'], reverse=True)

        # 智能片段合并
        coherent_segments = self._merge_coherent_segments(subtitles, high_relevance_segments)

        return coherent_segments

    def _merge_coherent_segments(self, subtitles: List[Dict], high_segments: List[Dict]) -> List[Dict]:
        """智能合并连贯片段"""
        coherent_segments = []
        used_indices = set()

        for segment_data in high_segments:
            start_idx = segment_data['index']
            if start_idx in used_indices:
                continue

            # 动态扩展范围
            expand_range = 12 if self.detected_genre in ['romance', 'family'] else 10

            segment_start = max(0, start_idx - expand_range)
            segment_end = min(len(subtitles) - 1, start_idx + expand_range)

            # 寻找自然边界
            segment_start = self._find_natural_start(subtitles, segment_start, start_idx)
            segment_end = self._find_natural_end(subtitles, start_idx, segment_end)

            # 计算时长
            start_time = self.time_to_seconds(subtitles[segment_start]['start'])
            end_time = self.time_to_seconds(subtitles[segment_end]['end'])
            duration = end_time - start_time

            # 动态时长控制
            min_duration = 90 if self.detected_genre in ['romance', 'family'] else 120
            max_duration = 200 if self.detected_genre in ['crime', 'legal'] else 180

            if min_duration <= duration <= max_duration:
                coherent_segments.append({
                    'start_index': segment_start,
                    'end_index': segment_end,
                    'start_time': subtitles[segment_start]['start'],
                    'end_time': subtitles[segment_end]['end'],
                    'duration': duration,
                    'core_content': self._extract_smart_content(subtitles, segment_start, segment_end),
                    'key_dialogue': self._extract_key_dialogue(subtitles, segment_start, segment_end),
                    'significance': self._analyze_smart_significance(subtitles, segment_start, segment_end),
                    'emotional_tone': self._analyze_emotional_tone(subtitles, segment_start, segment_end),
                    'genre': self.detected_genre,
                    'confidence': segment_data['score']
                })

                # 标记已使用的索引
                for idx in range(segment_start, segment_end + 1):
                    used_indices.add(idx)

        return coherent_segments[:3]  # 每集最多3个核心片段

    def _find_natural_start(self, subtitles: List[Dict], search_start: int, anchor: int) -> int:
        """寻找自然开始点"""
        scene_starters = ['突然', '这时', '忽然', '刚才', '现在', '那天', '当时', '随即', '后来', '接着']

        for i in range(anchor, search_start - 1, -1):
            text = subtitles[i]['text']
            if any(starter in text for starter in scene_starters):
                return i
            if len(text) < 8 and '...' in text:
                return i + 1

        return search_start

    def _find_natural_end(self, subtitles: List[Dict], anchor: int, search_end: int) -> int:
        """寻找自然结束点"""
        scene_enders = ['走了', '离开', '结束', '算了', '好吧', '再见', '拜拜', '完了', '行了']

        for i in range(anchor, search_end + 1):
            text = subtitles[i]['text']
            if any(ender in text for ender in scene_enders):
                return i
            if '...' in text and i > anchor + 8:
                return i

        return search_end

    def _extract_smart_content(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> str:
        """智能提取核心内容"""
        key_texts = []
        genre_keywords = self.get_genre_specific_keywords(self.detected_genre) if self.detected_genre else []

        for i in range(start_idx, min(end_idx + 1, start_idx + 6)):
            text = subtitles[i]['text']

            # 检查是否包含关键信息
            has_key_info = False
            if genre_keywords:
                has_key_info = any(keyword in text for keyword in genre_keywords)

            if has_key_info or any(keyword in text for keyword in self.universal_dramatic_keywords):
                key_texts.append(text.strip())

        return ' | '.join(key_texts) if key_texts else subtitles[start_idx]['text']

    def _extract_key_dialogue(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> List[str]:
        """提取关键对话"""
        key_dialogues = []

        for i in range(start_idx, end_idx + 1):
            text = subtitles[i]['text'].strip()
            score = self.calculate_intelligent_score(text)

            if score >= 4.0:
                time_code = f"{subtitles[i]['start']} --> {subtitles[i]['end']}"
                key_dialogues.append(f"[{time_code}] {text}")

        return key_dialogues[:5]

    def _analyze_smart_significance(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> str:
        """智能分析剧情意义"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])
        significance_points = []

        # 根据剧情类型分析
        if self.detected_genre == 'legal':
            if any(word in content for word in ['案件', '证据', '审判']):
                significance_points.append("法律程序推进")
        elif self.detected_genre == 'romance':
            if any(word in content for word in ['表白', '约会', '分手']):
                significance_points.append("情感关系发展")
        elif self.detected_genre == 'crime':
            if any(word in content for word in ['线索', '破案', '真相']):
                significance_points.append("案件调查进展")
        elif self.detected_genre == 'family':
            if any(word in content for word in ['家庭', '亲情', '成长']):
                significance_points.append("家庭关系发展")

        # 通用意义分析
        if any(word in content for word in ['发现', '真相', '秘密']):
            significance_points.append("重要信息揭露")
        if any(word in content for word in ['决定', '选择', '改变']):
            significance_points.append("角色发展转折")
        if any(word in content for word in ['冲突', '争论', '对抗']):
            significance_points.append("戏剧冲突高潮")

        return "、".join(significance_points) if significance_points else "剧情重要节点"

    def _analyze_emotional_tone(self, subtitles: List[Dict], start_idx: int, end_idx: int) -> str:
        """分析情感基调"""
        content = ' '.join([subtitles[i]['text'] for i in range(start_idx, end_idx + 1)])

        emotion_scores = {
            'positive': sum(1 for word in ['开心', '高兴', '快乐', '幸福', '温暖', '感动'] if word in content),
            'negative': sum(1 for word in ['悲伤', '难过', '痛苦', '绝望', '愤怒', '恐惧'] if word in content),
            'tense': sum(1 for word in ['紧张', '危险', '急', '快', '冲突', '争论'] if word in content),
            'romantic': sum(1 for word in ['爱', '喜欢', '心动', '浪漫', '甜蜜'] if word in content)
        }

        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        return dominant_emotion if emotion_scores[dominant_emotion] > 0 else 'neutral'

    def generate_smart_summary(self, episode_file: str, segments: List[Dict]) -> Dict:
        """生成智能剧集摘要"""
        episode_num = re.search(r'(\d+)', episode_file)
        episode_number = episode_num.group(1) if episode_num else "00"

        best_segments = segments[:2] if len(segments) >= 2 else segments
        total_duration = sum(seg['duration'] for seg in best_segments)

        # 智能生成主题
        if self.detected_genre:
            genre_desc = {
                'legal': '法律争议',
                'romance': '情感纠葛',
                'crime': '案件调查',
                'family': '家庭温情',
                'medical': '医疗救治',
                'business': '商战风云',
                'historical': '历史变迁',
                'fantasy': '奇幻冒险'
            }.get(self.detected_genre, '精彩片段')
        else:
            genre_desc = '精彩片段'

        # 从核心内容提取关键信息
        key_elements = []
        for seg in best_segments:
            content = seg['core_content']
            if len(content) > 20:
                key_elements.append(content.split(' | ')[0][:15])

        theme_desc = '、'.join(key_elements[:2]) if key_elements else genre_desc
        theme = f"E{episode_number}：{theme_desc}"

        return {
            'episode': episode_file,
            'episode_number': episode_number,
            'theme': theme,
            'genre': self.detected_genre or 'general',
            'genre_confidence': self.genre_confidence,
            'total_duration': total_duration,
            'segments': best_segments,
            'highlights': self._extract_smart_highlights(best_segments),
            'emotional_journey': self._analyze_emotional_journey(best_segments),
            'content_summary': self._generate_smart_content_summary(best_segments)
        }

    def _extract_smart_highlights(self, segments: List[Dict]) -> List[str]:
        """智能提取亮点"""
        highlights = []

        for seg in segments:
            content_preview = seg['core_content'][:40] + "..." if len(seg['core_content']) > 40 else seg['core_content']

            # 根据剧情类型调整亮点描述
            if self.detected_genre == 'legal':
                value_desc = "法律冲突核心场面"
            elif self.detected_genre == 'romance':
                value_desc = "情感高潮关键时刻"
            elif self.detected_genre == 'crime':
                value_desc = "案件破解重要线索"
            else:
                value_desc = "剧情关键转折点"

            highlights.append(f"• {seg['significance']}：{content_preview} ({value_desc})")

        return highlights

    def _analyze_emotional_journey(self, segments: List[Dict]) -> str:
        """分析情感历程"""
        emotions = [seg.get('emotional_tone', 'neutral') for seg in segments]
        return " → ".join(emotions)

    def _generate_smart_content_summary(self, segments: List[Dict]) -> str:
        """生成智能内容摘要"""
        if not segments:
            return "暂无重点内容"

        significances = [seg['significance'] for seg in segments]
        return "、".join(set(significances))

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换"""
        h, m, s_ms = time_str.split(':')
        s, ms = s_ms.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

    def analyze_single_episode(self, episode_file: str) -> Dict:
        """分析单集"""
        print(f"🔍 智能分析 {episode_file}...")

        subtitles = self.parse_subtitle_file(episode_file)

        # 首次分析时检测剧情类型
        if self.detected_genre is None:
            detected_genre = self.detect_genre(subtitles)
            print(f"🎭 检测到剧情类型: {detected_genre} (置信度: {self.genre_confidence:.2f})")

        core_segments = self.identify_smart_segments(subtitles)
        episode_summary = self.generate_smart_summary(episode_file, core_segments)

        # 添加连贯性分析
        episode_summary['continuity_hints'] = self._analyze_episode_continuity(core_segments)
        episode_summary['next_episode_connection'] = self._generate_next_episode_hint(core_segments)

        return episode_summary

    def _analyze_episode_continuity(self, segments: List[Dict]) -> List[str]:
        """分析集内连贯性提示"""
        hints = []
        for i, segment in enumerate(segments):
            content = segment['core_content']

            # 分析情节推进线索
            if '案件' in content or '证据' in content:
                hints.append(f"片段{i+1}: 案件调查关键进展")
            elif '法庭' in content or '审判' in content:
                hints.append(f"片段{i+1}: 法庭辩论核心场面")
            elif any(word in content for word in ['真相', '发现', '秘密']):
                hints.append(f"片段{i+1}: 重要信息揭露时刻")
            elif any(word in content for word in ['决定', '选择', '改变']):
                hints.append(f"片段{i+1}: 角色发展转折点")

        return hints

    def _generate_next_episode_hint(self, segments: List[Dict]) -> str:
        """生成与下一集的衔接提示"""
        if not segments:
            return "本集为独立情节，敬请期待下集精彩"

        last_segment = segments[-1]
        content = last_segment['core_content']

        # 根据结尾内容预测下集方向
        if '继续' in content or '下次' in content:
            return "本集埋下伏笔，下集将有重大进展"
        elif '听证会' in content:
            return "听证会准备就绪，下集法庭激辩即将开始"
        elif '申诉' in content or '重审' in content:
            return "申诉程序启动，下集案件迎来转机"
        elif '证据' in content:
            return "关键证据浮现，下集真相即将大白"
        elif '危险' in content or '威胁' in content:
            return "危机升级，下集情况更加紧急"
        else:
            return "剧情持续发展，下集更多精彩等您观看"

def analyze_all_episodes_intelligently():
    """智能分析整个剧集"""
    analyzer = IntelligentSubtitleAnalyzer()

    # 获取所有字幕文件
    subtitle_files = [f for f in os.listdir('.') if f.endswith('.txt') and ('E' in f or 'e' in f)]
    subtitle_files.sort()

    if not subtitle_files:
        print("❌ 未找到字幕文件")
        return []

    print(f"📺 智能分析系统启动 - 发现 {len(subtitle_files)} 个字幕文件")
    print("🤖 系统特性：")
    print("• 自动识别剧情类型（法律/爱情/犯罪/家庭/医疗/商战/古装/奇幻）")
    print("• 动态调整评分权重和时长控制")
    print("• AI辅助分析提升准确性")
    print("• 智能错别字修正和片段合并")
    print("=" * 60)

    all_episodes_plans = []

    for filename in subtitle_files:
        try:
            episode_plan = analyzer.analyze_single_episode(filename)
            all_episodes_plans.append(episode_plan)

            print(f"✓ {filename}")
            print(f"  🎭 类型: {episode_plan.get('genre', 'unknown')}")
            print(f"  📝 主题: {episode_plan['theme']}")
            print(f"  ⏱️ 时长: {episode_plan['total_duration']:.1f}秒")
            print(f"  🎯 内容: {episode_plan['content_summary']}")
            print(f"  😊 情感: {episode_plan.get('emotional_journey', 'neutral')}")
            print()

        except Exception as e:
            print(f"✗ 错误处理 {filename}: {e}")

    # 生成智能分析报告
    generate_intelligent_report(all_episodes_plans, analyzer)

    return all_episodes_plans

def generate_intelligent_report(episodes_plans: List[Dict], analyzer):
    """生成智能分析报告"""
    if not episodes_plans:
        return

    content = "📺 智能电视剧剪辑分析报告\n"
    content += "=" * 80 + "\n\n"

    # 系统信息
    content += "🤖 智能分析系统信息：\n"
    content += f"• 检测到的剧情类型: {analyzer.detected_genre or '通用'}\n"
    content += f"• 类型识别置信度: {analyzer.genre_confidence:.2f}\n"
    content += f"• 分析模式: {'AI增强' if analyzer.use_ai_analysis else '规则分析'}\n"
    content += f"• 总集数: {len(episodes_plans)} 集\n\n"

    # 剧情类型统计
    genre_stats = {}
    for plan in episodes_plans:
        genre = plan.get('genre', 'unknown')
        genre_stats[genre] = genre_stats.get(genre, 0) + 1

    content += "📊 剧情类型分布：\n"
    for genre, count in genre_stats.items():
        content += f"• {genre}: {count} 集\n"
    content += "\n"

    # 详细分析
    total_duration = 0
    for i, plan in enumerate(episodes_plans):
        content += f"📺 {plan['theme']}\n"
        content += "-" * 60 + "\n"
        content += f"剧情类型：{plan.get('genre', 'unknown')}\n"
        content += f"总时长：{plan['total_duration']:.1f} 秒 ({plan['total_duration']/60:.1f} 分钟)\n"
        content += f"情感历程：{plan.get('emotional_journey', 'neutral')}\n"
        content += f"片段数：{len(plan['segments'])} 个核心片段\n\n"

        # 片段详情
        for j, segment in enumerate(plan['segments']):
            content += f"🎬 片段 {j+1}：\n"
            content += f"   时间：{segment['start_time']} --> {segment['end_time']}\n"
            content += f"   时长：{segment['duration']:.1f} 秒\n"
            content += f"   意义：{segment['significance']}\n"
            content += f"   情感：{segment.get('emotional_tone', 'neutral')}\n"
            content += f"   置信度：{segment.get('confidence', 0):.1f}\n"
            content += f"   内容：{segment['core_content'][:100]}...\n"

            if segment['key_dialogue']:
                content += "   关键对话：\n"
                for dialogue in segment['key_dialogue'][:3]:
                    content += f"     {dialogue}\n"
            content += "\n"

        # 亮点
        if plan['highlights']:
            content += "✨ 本集亮点：\n"
            for highlight in plan['highlights']:
                content += f"   {highlight}\n"

        total_duration += plan['total_duration']
        content += "=" * 80 + "\n\n"

    # 总结
    content += f"📊 智能分析总结：\n"
    content += f"• 分析集数：{len(episodes_plans)} 集\n"
    content += f"• 总时长：{total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)\n"
    content += f"• 平均每集：{total_duration/len(episodes_plans):.1f} 秒\n"
    content += f"• 主要类型：{analyzer.detected_genre or '通用'}\n"
    content += f"• 分析精度：{'AI增强模式' if analyzer.use_ai_analysis else '规则模式'}\n"
    content += f"• 适用场景：自动化剪辑、精彩片段提取、内容分析\n"

    # 保存报告
    safe_file_write('intelligent_analysis_report.txt', content)

    print(f"✅ 智能分析报告已保存到 intelligent_analysis_report.txt")
    print(f"📄 报告包含{len(episodes_plans)}集的详细分析，总时长{total_duration/60:.1f}分钟")

if __name__ == "__main__":
    analyze_all_episodes_intelligently()

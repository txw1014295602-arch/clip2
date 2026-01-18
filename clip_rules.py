
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
专业剪辑规则配置 - 针对连贯剧情剪辑的规则引擎
"""

class ClipRules:
    """剪辑规则配置类"""
    
    def __init__(self):
        # 单集剪辑规则
        self.single_episode_rules = {
            'target_duration': (120, 180),  # 每集2-3分钟
            'max_segments': 3,  # 每集最多3个核心片段
            'min_segment_duration': 30,  # 单个片段最少30秒
            'max_segment_duration': 90,  # 单个片段最多90秒
            'buffer_time': 3,  # 前后缓冲时间(秒)
        }
        
        # 片段选择标准
        self.selection_criteria = {
            'priority_keywords': {
                'legal': ['法庭', '审判', '证据', '申诉', '听证会', '检察官', '律师', '正当防卫'],
                'plot_advancement': ['发现', '真相', '秘密', '揭露', '调查', '线索'],
                'character_development': ['决定', '选择', '改变', '成长', '坚持', '放弃'],
                'dramatic_tension': ['冲突', '争论', '对抗', '危险', '紧急', '威胁'],
                'emotional_peaks': ['愤怒', '悲伤', '激动', '震惊', '感动', '绝望']
            },
            'story_continuity': {
                'case_keywords': ['四二八案', '628旧案', '段洪山', '张园', '霸凌'],
                'legal_process': ['起诉', '辩护', '判决', '上诉', '重审', '听证'],
                'relationships': ['父女', '师生', '同学', '朋友', '敌对']
            }
        }
        
        # 跨集连贯性规则
        self.series_continuity = {
            'main_storylines': [
                '四二八案调查进展',
                '628旧案真相揭露', 
                '段洪山父女情感线',
                '正当防卫争议',
                '校园霸凌案件'
            ],
            'episode_connections': {
                'setup_keywords': ['开始', '启动', '决定', '准备'],
                'development_keywords': ['进展', '发现', '调查', '收集'],
                'climax_keywords': ['关键', '决定性', '转折', '突破'],
                'resolution_keywords': ['结果', '判决', '真相', '结束']
            }
        }
        
        # 内容质量标准
        self.quality_standards = {
            'dialogue_completeness': True,  # 确保对话完整性
            'scene_coherence': True,  # 确保场景连贯性
            'emotional_arc': True,  # 保持情感弧线
            'narrative_flow': True  # 维持叙事流畅
        }
    
    def evaluate_segment_priority(self, segment_text: str, episode_context: dict) -> float:
        """评估片段优先级"""
        score = 0.0
        
        # 基础关键词匹配
        for category, keywords in self.selection_criteria['priority_keywords'].items():
            matches = sum(1 for kw in keywords if kw in segment_text)
            if category == 'legal':
                score += matches * 3.0  # 法律剧情高权重
            elif category == 'plot_advancement':
                score += matches * 2.5
            elif category == 'dramatic_tension':
                score += matches * 2.0
            else:
                score += matches * 1.5
        
        # 故事连贯性加分
        for keyword in self.selection_criteria['story_continuity']['case_keywords']:
            if keyword in segment_text:
                score += 4.0  # 主线剧情高分
        
        # 情感强度评估
        emotional_markers = ['！', '？', '...', '哭', '喊', '激动', '愤怒']
        emotion_score = sum(segment_text.count(marker) for marker in emotional_markers)
        score += emotion_score * 0.5
        
        return score
    
    def generate_episode_theme(self, segments: list, episode_num: str) -> str:
        """生成集数主题"""
        # 分析主要内容
        all_text = ' '.join([seg.get('core_content', '') for seg in segments])
        
        themes = {
            '案件开始': ['开始', '启动', '申请', '决定'],
            '证据收集': ['证据', '调查', '发现', '收集'],
            '法庭辩论': ['法庭', '审判', '辩论', '听证'],
            '真相揭露': ['真相', '揭露', '秘密', '发现'],
            '情感冲突': ['冲突', '争吵', '对抗', '分歧'],
            '关键转折': ['转折', '改变', '突破', '关键'],
            '最终判决': ['判决', '结果', '结束', '终于']
        }
        
        for theme, keywords in themes.items():
            if any(kw in all_text for kw in keywords):
                return f"E{episode_num}：{theme}"
        
        return f"E{episode_num}：剧情发展"
    
    def check_segment_continuity(self, prev_segment: dict, current_segment: dict) -> dict:
        """检查片段间连贯性"""
        continuity_info = {
            'has_connection': False,
            'connection_type': None,
            'transition_hint': ''
        }
        
        if not prev_segment:
            return continuity_info
        
        prev_text = prev_segment.get('core_content', '')
        curr_text = current_segment.get('core_content', '')
        
        # 检查逻辑连接
        if any(word in prev_text for word in ['然后', '接着', '随后']):
            continuity_info['has_connection'] = True
            continuity_info['connection_type'] = 'sequential'
            
        # 检查因果关系
        if any(word in prev_text for word in ['因为', '所以', '导致', '结果']):
            continuity_info['has_connection'] = True
            continuity_info['connection_type'] = 'causal'
            
        # 检查主题连续性
        common_keywords = set(prev_text.split()) & set(curr_text.split())
        if len(common_keywords) >= 3:
            continuity_info['has_connection'] = True
            continuity_info['connection_type'] = 'thematic'
        
        return continuity_info
    
    def format_episode_output(self, episode_plan: dict) -> dict:
        """格式化集数输出信息"""
        formatted = {
            'episode_number': episode_plan.get('episode_number', '00'),
            'theme': episode_plan.get('theme', '精彩片段'),
            'segments': [],
            'highlights': [],
            'continuity_summary': '',
            'next_episode_connection': episode_plan.get('next_episode_connection', '')
        }
        
        # 格式化片段信息
        for i, segment in enumerate(episode_plan.get('segments', [])):
            formatted_segment = {
                'segment_number': i + 1,
                'time_range': f"{segment.get('start_time', '')} --> {segment.get('end_time', '')}",
                'duration': f"{segment.get('duration', 0):.1f}秒",
                'core_dialogue': segment.get('key_dialogue', [])[:3],  # 取前3条关键对话
                'significance': segment.get('significance', ''),
                'content_preview': segment.get('core_content', '')[:100] + '...'
            }
            formatted['segments'].append(formatted_segment)
        
        # 生成亮点总结
        for segment in formatted['segments']:
            highlight = f"• {segment['significance']}（{segment['duration']}）"
            formatted['highlights'].append(highlight)
        
        return formatted

# 全局规则实例
clip_rules = ClipRules()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版旁白生成器 - 为精彩片段生成解说字幕
"""

import re
from typing import Dict, List, Optional
from narration_config import NARRATION_TEMPLATES, KEYWORD_MAPPING

class EnhancedNarrationGenerator:
    def __init__(self, ai_config: Dict = None):
        self.ai_config = ai_config or {}
        self.ai_enabled = self.ai_config.get('enabled', False)

    def generate_segment_narration(self, segment: Dict) -> Dict:
        """为视频片段生成旁白"""
        try:
            title = segment.get('title', '精彩片段')
            significance = segment.get('plot_significance', '')
            content_summary = segment.get('content_summary', '')
            narration_text = segment.get('professional_narration', '')
            
            # 检测剧情类型
            genre = self.detect_content_genre(title + ' ' + significance + ' ' + content_summary)
            
            # 如果有AI生成的旁白，优先使用
            if self.ai_enabled and narration_text and len(narration_text) > 30:
                return self.parse_ai_narration(narration_text, genre)
            
            # 否则使用模板生成
            return self.generate_template_narration(title, significance, content_summary, genre)
            
        except Exception as e:
            print(f"旁白生成失败: {e}")
            return self.get_fallback_narration()

    def detect_content_genre(self, content: str) -> str:
        """检测内容类型"""
        content_lower = content.lower()
        
        for genre, keywords in KEYWORD_MAPPING.items():
            genre_name = genre.replace('_keywords', '')
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score >= 2:  # 至少匹配2个关键词
                return genre_name
        
        return 'general'

    def parse_ai_narration(self, ai_text: str, genre: str) -> Dict:
        """解析AI生成的旁白"""
        try:
            # 将AI文本分解成不同部分
            sentences = [s.strip() for s in ai_text.split('。') if s.strip()]
            
            if len(sentences) >= 2:
                main_explanation = sentences[0][:40]
                highlight_tip = sentences[1][:35] if len(sentences) > 1 else ""
                
                # 添加emoji和标识符
                highlight_tip = f"💡 {highlight_tip}" if highlight_tip else "💡 精彩内容值得关注"
                
            else:
                main_explanation = ai_text[:40]
                highlight_tip = "💡 精彩对话不容错过"
            
            return {
                'genre': genre,
                'main_explanation': main_explanation,
                'highlight_tip': highlight_tip,
                'full_narration': ai_text,
                'timing': {
                    'explanation_start': 3,
                    'explanation_duration': 5,
                    'highlight_start_from_end': 3
                }
            }
            
        except Exception as e:
            print(f"AI旁白解析失败: {e}")
            return self.generate_template_narration("", "", "", genre)

    def generate_template_narration(self, title: str, significance: str, content: str, genre: str) -> Dict:
        """使用模板生成旁白"""
        template = NARRATION_TEMPLATES.get(genre, NARRATION_TEMPLATES['general'])
        
        # 智能生成解说内容
        if '真相' in significance or '揭露' in significance:
            explanation = "关键真相即将揭晓"
            tip = "💡 重要信息不容错过"
        elif '冲突' in significance or '争论' in significance:
            explanation = template['explanation']
            tip = f"💡 {template['tip']}"
        elif '情感' in significance or '感动' in significance:
            explanation = "感人至深的情感表达"
            tip = "💡 最动人的时刻到了"
        elif '法律' in significance or '案件' in significance:
            explanation = "法律争议焦点分析"
            tip = "💡 关键法理值得深思"
        else:
            explanation = template['explanation']
            tip = f"💡 {template['tip']}"
        
        return {
            'genre': genre,
            'main_explanation': explanation,
            'highlight_tip': tip,
            'full_narration': f"{explanation}，{tip}",
            'timing': {
                'explanation_start': 3,
                'explanation_duration': 5, 
                'highlight_start_from_end': 3
            }
        }

    def get_fallback_narration(self) -> Dict:
        """获取备用旁白"""
        return {
            'genre': 'general',
            'main_explanation': "精彩剧情即将上演",
            'highlight_tip': "💡 不容错过的重要情节",
            'full_narration': "精彩剧情即将上演，不容错过的重要情节",
            'timing': {
                'explanation_start': 3,
                'explanation_duration': 5,
                'highlight_start_from_end': 3
            }
        }

    def create_subtitle_filters(self, narration: Dict, video_duration: float) -> List[str]:
        """创建字幕滤镜"""
        filters = []
        
        try:
            main_text = self.clean_text_for_ffmpeg(narration.get('main_explanation', ''))
            tip_text = self.clean_text_for_ffmpeg(narration.get('highlight_tip', ''))
            
            if main_text:
                # 主要解说（3-8秒）
                filters.append(
                    f"drawtext=text='{main_text}':fontsize=20:fontcolor=yellow:"
                    f"x=(w-text_w)/2:y=h-120:box=1:boxcolor=black@0.7:boxborderw=3:"
                    f"enable='between(t,3,8)'"
                )
            
            if tip_text:
                # 精彩提示（最后3秒）
                highlight_start = max(0, video_duration - 3)
                filters.append(
                    f"drawtext=text='{tip_text}':fontsize=18:fontcolor=lightblue:"
                    f"x=(w-text_w)/2:y=h-80:box=1:boxcolor=black@0.6:boxborderw=3:"
                    f"enable='gte(t,{highlight_start})'"
                )
            
            # 精彩标识
            filters.append(
                f"drawtext=text='🔥 精彩片段':fontsize=16:fontcolor=red:"
                f"x=20:y=20:box=1:boxcolor=black@0.6:boxborderw=2:"
                f"enable='between(t,1,4)'"
            )
            
        except Exception as e:
            print(f"字幕滤镜创建失败: {e}")
        
        return filters

    def clean_text_for_ffmpeg(self, text: str) -> str:
        """清理文本以适配FFmpeg"""
        if not text:
            return ""
        
        # 移除或替换可能导致FFmpeg错误的字符
        text = text.replace("'", "").replace('"', '')
        text = text.replace('\\', '').replace(':', '：')
        text = text.replace('[', '').replace(']', '')
        text = text.replace('(', '').replace(')', '')
        text = re.sub(r'[^\w\u4e00-\u9fff\s\-_！？。，：；💡🔥]', '', text)
        
        return text.strip()[:50]  # 限制长度

    def export_narration_text(self, narration: Dict, output_path: str):
        """导出旁白文本到文件"""
        try:
            narration_file = output_path.replace('.mp4', '_旁白解说.txt')
            
            content = f"""📺 视频旁白解说文案
{'=' * 50}

🎭 剧情类型: {narration.get('genre', 'general')}

🎙️ 主要解说 (3-8秒):
{narration.get('main_explanation', '')}

💡 精彩提示 (最后3秒):
{narration.get('highlight_tip', '')}

📝 完整旁白:
{narration.get('full_narration', '')}

⏰ 时间配置:
- 解说开始: {narration.get('timing', {}).get('explanation_start', 3)} 秒
- 解说时长: {narration.get('timing', {}).get('explanation_duration', 5)} 秒
- 提示位置: 倒数 {narration.get('timing', {}).get('highlight_start_from_end', 3)} 秒

💡 使用说明:
本旁白专门为视频精彩片段设计，通过字幕叠加的方式为观众提供额外的解释和提示，
帮助观众更好地理解剧情要点和精彩之处。
"""
            
            with open(narration_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   📜 旁白说明已保存: {narration_file}")
            
        except Exception as e:
            print(f"   ⚠️ 旁白文件保存失败: {e}")

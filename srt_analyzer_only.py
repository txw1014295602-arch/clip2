
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SRT字幕精准分析解释系统
专门用于分析字幕内容，生成详细且通俗易懂的解释
不涉及视频剪辑功能
"""

import os
import re
import json
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
import platform_fix

class SRTAnalyzerOnly:
    def __init__(self):
        self.srt_folder = "srt"
        self.output_folder = "srt_analysis"
        self.cache_folder = "srt_cache"
        
        # 创建必要目录
        for folder in [self.srt_folder, self.output_folder, self.cache_folder]:
            os.makedirs(folder, exist_ok=True)
        
        # 加载AI配置
        self.ai_config = self.load_ai_config()
        
        print("📝 SRT字幕精准分析解释系统")
        print("=" * 50)
        print("🎯 功能：专门分析SRT字幕内容，生成详细解释")
        print("📁 字幕目录：srt/")
        print("📄 输出目录：srt_analysis/")

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            config_content = platform_fix.safe_file_read('.ai_config.json')
            if config_content:
                return json.loads(config_content)
        except:
            pass
        return {'enabled': False}

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """精准解析SRT字幕文件"""
        print(f"📖 解析字幕文件: {os.path.basename(filepath)}")
        
        try:
            content = platform_fix.safe_file_read(filepath)
            
            # 智能错误修正
            content = self.fix_common_errors(content)
            
            # 解析SRT格式
            subtitles = []
            blocks = re.split(r'\n\s*\n', content.strip())
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        index = int(lines[0])
                        time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                        
                        if time_match:
                            start_time = time_match.group(1)
                            end_time = time_match.group(2)
                            text = '\n'.join(lines[2:]).strip()
                            
                            subtitles.append({
                                'index': index,
                                'start_time': start_time,
                                'end_time': end_time,
                                'text': text,
                                'duration': self.calculate_duration(start_time, end_time),
                                'char_count': len(text),
                                'word_count': len(text.split())
                            })
                    except (ValueError, IndexError):
                        continue
            
            print(f"✅ 成功解析 {len(subtitles)} 条字幕")
            return subtitles
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return []

    def fix_common_errors(self, content: str) -> str:
        """修正常见的字幕错误"""
        corrections = {
            # 繁体字修正
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '設計': '设计', '開始': '开始', '結束': '结束',
            '問題': '问题', '機會': '机会', '決定': '决定', '選擇': '选择',
            '聽証會': '听证会', '調查': '调查', '審理': '审理', '辯護': '辩护',
            
            # 常见错别字
            '四二八案': '428案', '六二八': '628', '正当防衛': '正当防卫',
            '申述': '申诉', '証詞': '证词', '覆審': '复审'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        return content

    def calculate_duration(self, start_time: str, end_time: str) -> float:
        """计算字幕持续时间（秒）"""
        try:
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            return end_seconds - start_seconds
        except:
            return 0.0

    def time_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def analyze_subtitle_content(self, subtitles: List[Dict]) -> Dict:
        """分析字幕内容特征"""
        if not subtitles:
            return {}
        
        total_duration = sum(sub['duration'] for sub in subtitles)
        total_chars = sum(sub['char_count'] for sub in subtitles)
        total_words = sum(sub['word_count'] for sub in subtitles)
        
        # 统计说话速度
        speaking_rates = []
        for sub in subtitles:
            if sub['duration'] > 0:
                chars_per_second = sub['char_count'] / sub['duration']
                speaking_rates.append(chars_per_second)
        
        avg_speaking_rate = sum(speaking_rates) / len(speaking_rates) if speaking_rates else 0
        
        # 识别剧情类型
        content_text = ' '.join([sub['text'] for sub in subtitles])
        genre = self.detect_genre(content_text)
        
        # 提取关键词
        keywords = self.extract_keywords(content_text)
        
        # 识别角色
        characters = self.identify_characters(subtitles)
        
        return {
            'total_subtitles': len(subtitles),
            'total_duration': total_duration,
            'total_characters': total_chars,
            'total_words': total_words,
            'average_speaking_rate': avg_speaking_rate,
            'genre': genre,
            'keywords': keywords,
            'characters': characters,
            'language_complexity': self.analyze_language_complexity(content_text)
        }

    def detect_genre(self, content: str) -> str:
        """检测剧情类型"""
        genre_keywords = {
            '法律剧': ['法官', '检察官', '律师', '法庭', '审判', '证据', '案件', '起诉', '辩护', '判决', '申诉', '听证会'],
            '犯罪剧': ['警察', '犯罪', '嫌疑人', '调查', '破案', '线索', '凶手', '案发', '侦探', '刑侦'],
            '医疗剧': ['医生', '护士', '医院', '手术', '病人', '诊断', '治疗', '病情', '急诊'],
            '爱情剧': ['爱情', '喜欢', '心动', '表白', '约会', '分手', '复合', '结婚', '情侣'],
            '家庭剧': ['家庭', '父母', '孩子', '兄弟', '姐妹', '亲情', '家人', '团聚'],
            '商战剧': ['公司', '老板', '员工', '合作', '竞争', '项目', '会议', '谈判', '投资'],
            '古装剧': ['皇帝', '大臣', '朝廷', '战争', '将军', '士兵', '王朝', '宫廷'],
            '都市剧': ['城市', '职场', '白领', '生活', '工作', '压力', '梦想', '奋斗']
        }
        
        genre_scores = {}
        for genre, keywords in genre_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                genre_scores[genre] = score
        
        if genre_scores:
            return max(genre_scores, key=genre_scores.get)
        return '通用剧情'

    def extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 常见的重要词汇
        important_patterns = [
            r'[四六]二八案', r'\d+案', r'听证会', r'申诉', r'复审', r'证据', r'证词',
            r'正当防卫', r'故意伤害', r'法官', r'检察官', r'律师', r'辩护',
            r'段洪山', r'李慕枫', r'张园', r'霸凌', r'校园暴力'
        ]
        
        keywords = []
        for pattern in important_patterns:
            matches = re.findall(pattern, content)
            keywords.extend(matches)
        
        return list(set(keywords))  # 去重

    def identify_characters(self, subtitles: List[Dict]) -> List[str]:
        """识别剧中角色"""
        # 常见的人名模式
        name_patterns = [
            r'[李王张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段雷钱汤尹黎易常武乔贺赖龚文][一-龯]{1,2}'
        ]
        
        characters = set()
        for sub in subtitles:
            for pattern in name_patterns:
                matches = re.findall(pattern, sub['text'])
                characters.update(matches)
        
        # 过滤掉可能不是人名的词
        filtered_characters = []
        for char in characters:
            if len(char) >= 2 and not any(word in char for word in ['法官', '检察官', '律师', '医生', '护士']):
                filtered_characters.append(char)
        
        return sorted(filtered_characters)

    def analyze_language_complexity(self, content: str) -> Dict:
        """分析语言复杂度"""
        # 计算句子长度分布
        sentences = re.split(r'[。！？]', content)
        sentence_lengths = [len(s.strip()) for s in sentences if s.strip()]
        
        # 计算词汇丰富度
        words = content.split()
        unique_words = set(words)
        vocabulary_richness = len(unique_words) / len(words) if words else 0
        
        # 检测专业术语
        professional_terms = ['正当防卫', '故意伤害', '听证会', '申诉', '复审', '证据', '证词', '辩护', '起诉']
        term_count = sum(1 for term in professional_terms if term in content)
        
        return {
            'avg_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            'vocabulary_richness': vocabulary_richness,
            'professional_terms_count': term_count,
            'complexity_level': '高' if vocabulary_richness > 0.7 and term_count > 5 else ('中' if vocabulary_richness > 0.5 else '低')
        }

    def generate_detailed_explanation(self, subtitles: List[Dict], analysis: Dict, filename: str) -> str:
        """生成详细且通俗易懂的解释"""
        episode_num = self.extract_episode_number(filename)
        
        explanation = f"""📺 第{episode_num}集 字幕内容详细解释
{'=' * 80}

📊 基本信息统计
• 字幕条数：{analysis['total_subtitles']} 条
• 总时长：{analysis['total_duration']:.1f} 秒 ({analysis['total_duration']/60:.1f} 分钟)
• 总字符数：{analysis['total_characters']} 字
• 总词汇量：{analysis['total_words']} 词
• 平均语速：{analysis['average_speaking_rate']:.1f} 字/秒

🎭 剧情类型分析
• 检测类型：{analysis['genre']}
• 语言复杂度：{analysis['language_complexity']['complexity_level']}
• 专业术语：{analysis['language_complexity']['professional_terms_count']} 个
• 词汇丰富度：{analysis['language_complexity']['vocabulary_richness']:.2f}

👥 主要角色识别
"""
        if analysis['characters']:
            for char in analysis['characters'][:10]:  # 显示前10个角色
                explanation += f"• {char}\n"
        else:
            explanation += "• 未识别到明确角色名称\n"

        explanation += f"""
🔑 关键词提取
"""
        if analysis['keywords']:
            for keyword in analysis['keywords'][:15]:  # 显示前15个关键词
                explanation += f"• {keyword}\n"
        else:
            explanation += "• 未提取到特定关键词\n"

        # 分析精彩对话片段
        interesting_segments = self.find_interesting_segments(subtitles)
        
        explanation += f"""
💬 精彩对话片段解析（共{len(interesting_segments)}个）
"""

        for i, segment in enumerate(interesting_segments[:5], 1):  # 显示前5个精彩片段
            explanation += f"""
📍 片段 {i}：{segment['title']}
⏰ 时间：{segment['start_time']} --> {segment['end_time']} (时长: {segment['duration']:.1f}秒)
🎯 重要性：{segment['importance']}
📝 内容摘要：{segment['summary']}

💭 通俗解释：
{segment['explanation']}

🗣️ 关键对话：
"""
            for dialogue in segment['key_dialogues'][:3]:  # 每个片段显示前3句关键对话
                explanation += f"   [{dialogue['time']}] {dialogue['text']}\n"
            
            explanation += "\n"

        # 剧情连贯性分析
        explanation += f"""
🔗 剧情连贯性分析
• 对话节奏：{'快速' if analysis['average_speaking_rate'] > 8 else ('适中' if analysis['average_speaking_rate'] > 5 else '缓慢')}
• 情节密度：{'高密度' if len(interesting_segments) > 8 else ('中密度' if len(interesting_segments) > 4 else '低密度')}
• 主线推进：{self.analyze_plot_progression(subtitles)}

📝 内容总结
{self.generate_content_summary(subtitles, analysis)}

💡 观看建议
{self.generate_viewing_suggestions(analysis)}

📊 技术统计
• 最长字幕：{max([sub['char_count'] for sub in subtitles], default=0)} 字
• 最短字幕：{min([sub['char_count'] for sub in subtitles if sub['char_count'] > 0], default=0)} 字
• 平均字幕长度：{sum([sub['char_count'] for sub in subtitles]) / len(subtitles):.1f} 字
• 最快语速：{max([sub['char_count']/sub['duration'] for sub in subtitles if sub['duration'] > 0], default=0):.1f} 字/秒
• 最慢语速：{min([sub['char_count']/sub['duration'] for sub in subtitles if sub['duration'] > 0], default=0):.1f} 字/秒

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return explanation

    def find_interesting_segments(self, subtitles: List[Dict]) -> List[Dict]:
        """查找精彩对话片段"""
        segments = []
        
        # 关键词权重
        keywords_weights = {
            '高权重': ['真相', '证据', '发现', '秘密', '揭露', '申诉', '听证会', '判决', '复审'],
            '中权重': ['案件', '调查', '法庭', '律师', '证词', '辩护', '起诉', '审理'],
            '低权重': ['问题', '情况', '事情', '可能', '应该', '觉得', '认为', '希望']
        }
        
        # 情感标识词
        emotion_words = ['愤怒', '生气', '激动', '兴奋', '紧张', '害怕', '担心', '开心', '高兴', '悲伤', '难过', '震惊', '惊讶']
        
        # 分析每个字幕的重要性
        for i, subtitle in enumerate(subtitles):
            score = 0
            text = subtitle['text']
            
            # 关键词评分
            for weight_category, keywords in keywords_weights.items():
                for keyword in keywords:
                    if keyword in text:
                        if weight_category == '高权重':
                            score += 3
                        elif weight_category == '中权重':
                            score += 2
                        else:
                            score += 1
            
            # 情感词评分
            for emotion in emotion_words:
                if emotion in text:
                    score += 2
            
            # 对话长度评分
            if subtitle['char_count'] > 30:
                score += 1
            if subtitle['char_count'] > 50:
                score += 1
            
            # 语速评分（快语速通常表示紧张情节）
            if subtitle['duration'] > 0:
                speaking_rate = subtitle['char_count'] / subtitle['duration']
                if speaking_rate > 10:  # 快语速
                    score += 2
            
            if score >= 5:  # 阈值：至少5分才算精彩
                # 构建片段上下文
                context_start = max(0, i - 2)
                context_end = min(len(subtitles), i + 3)
                context_subtitles = subtitles[context_start:context_end]
                
                segment = self.build_segment_info(subtitle, context_subtitles, score, i)
                segments.append(segment)
        
        # 按重要性排序
        segments.sort(key=lambda x: x['score'], reverse=True)
        
        # 合并相邻片段
        merged_segments = self.merge_adjacent_segments(segments, subtitles)
        
        return merged_segments[:10]  # 返回前10个最精彩的片段

    def build_segment_info(self, main_subtitle: Dict, context_subtitles: List[Dict], score: int, index: int) -> Dict:
        """构建片段信息"""
        # 生成标题
        text = main_subtitle['text']
        if '真相' in text or '发现' in text:
            title = "真相揭露时刻"
        elif '证据' in text:
            title = "关键证据呈现"
        elif '申诉' in text or '听证会' in text:
            title = "法律程序关键"
        elif '愤怒' in text or '生气' in text:
            title = "情感爆发时刻"
        elif '调查' in text or '案件' in text:
            title = "案件调查推进"
        else:
            title = "重要对话片段"
        
        # 生成解释
        explanation = self.generate_segment_explanation(main_subtitle, context_subtitles)
        
        # 提取关键对话
        key_dialogues = []
        for sub in context_subtitles:
            if sub['char_count'] > 15:  # 只提取有意义的对话
                key_dialogues.append({
                    'time': sub['start_time'],
                    'text': sub['text']
                })
        
        return {
            'title': title,
            'start_time': context_subtitles[0]['start_time'],
            'end_time': context_subtitles[-1]['end_time'],
            'duration': sum(sub['duration'] for sub in context_subtitles),
            'score': score,
            'importance': self.get_importance_level(score),
            'summary': text[:50] + "..." if len(text) > 50 else text,
            'explanation': explanation,
            'key_dialogues': key_dialogues,
            'index': index
        }

    def generate_segment_explanation(self, main_subtitle: Dict, context_subtitles: List[Dict]) -> str:
        """生成片段的通俗解释"""
        text = main_subtitle['text']
        
        if '428案' in text or '628案' in text:
            return "这里涉及到案件的核心信息。428案和628案是剧中的重要案件线索，关系到整个故事的发展走向。"
        elif '申诉' in text:
            return "申诉是法律程序中的重要环节，意味着当事人对判决结果不满，要求重新审理。这通常是剧情转折的关键时刻。"
        elif '听证会' in text:
            return "听证会是法庭审理的正式程序，各方将在此展示证据、进行辩论。这种场景往往是剧情的高潮部分。"
        elif '证据' in text:
            return "证据是法庭审理的核心，新证据的出现往往会改变案件走向，是推动剧情发展的重要因素。"
        elif '正当防卫' in text:
            return "正当防卫是法律概念，指在受到不法侵害时采取的合理防御行为。这是案件争议的焦点之一。"
        elif '霸凌' in text or '校园暴力' in text:
            return "校园霸凌是社会热点问题，剧中通过这一情节反映现实中的社会问题，引发观众思考。"
        elif '真相' in text or '发现' in text:
            return "真相的揭露是观众最期待的时刻，这里可能会有重要的情节反转或关键信息披露。"
        elif '段洪山' in text:
            return "段洪山是剧中重要角色，他的言行举止往往关系到案件的发展和真相的揭示。"
        else:
            return "这段对话包含了推进剧情的重要信息，值得观众仔细关注其中的细节和含义。"

    def get_importance_level(self, score: int) -> str:
        """获取重要性等级"""
        if score >= 10:
            return "极其重要"
        elif score >= 8:
            return "非常重要"
        elif score >= 6:
            return "比较重要"
        else:
            return "一般重要"

    def merge_adjacent_segments(self, segments: List[Dict], subtitles: List[Dict]) -> List[Dict]:
        """合并相邻的精彩片段"""
        if not segments:
            return []
        
        merged = []
        current_segment = segments[0].copy()
        
        for next_segment in segments[1:]:
            # 检查是否相邻（时间间隔小于30秒）
            current_end = self.time_to_seconds(current_segment['end_time'])
            next_start = self.time_to_seconds(next_segment['start_time'])
            
            if next_start - current_end < 30:  # 30秒内的片段合并
                # 合并片段
                current_segment['end_time'] = next_segment['end_time']
                current_segment['duration'] = self.time_to_seconds(current_segment['end_time']) - self.time_to_seconds(current_segment['start_time'])
                current_segment['score'] = max(current_segment['score'], next_segment['score'])
                current_segment['key_dialogues'].extend(next_segment['key_dialogues'])
                current_segment['title'] = f"{current_segment['title']} & {next_segment['title']}"
            else:
                merged.append(current_segment)
                current_segment = next_segment.copy()
        
        merged.append(current_segment)
        return merged

    def analyze_plot_progression(self, subtitles: List[Dict]) -> str:
        """分析剧情推进情况"""
        content = ' '.join([sub['text'] for sub in subtitles])
        
        if '申诉' in content and '听证会' in content:
            return "法律程序推进，从申诉到听证会的完整流程"
        elif '调查' in content and '证据' in content:
            return "案件调查深入，证据逐步收集和分析"
        elif '真相' in content or '发现' in content:
            return "真相逐步揭露，关键信息披露"
        elif '审理' in content or '法庭' in content:
            return "法庭审理过程，法律争议焦点明确"
        else:
            return "剧情稳步发展，人物关系和故事线索推进"

    def generate_content_summary(self, subtitles: List[Dict], analysis: Dict) -> str:
        """生成内容总结"""
        genre = analysis['genre']
        keywords = analysis['keywords']
        
        summary = f"本集为{genre}，"
        
        if '法律' in genre:
            summary += "主要围绕法律案件展开，涉及法庭审理、证据分析等法律程序。"
        elif '犯罪' in genre:
            summary += "重点描述案件调查过程，包括线索收集、真相追查等内容。"
        elif '爱情' in genre:
            summary += "聚焦人物情感关系发展，展现爱情故事的起伏变化。"
        else:
            summary += "通过丰富的人物对话和情节发展，推进整体故事线索。"
        
        if keywords:
            summary += f" 关键要素包括：{', '.join(keywords[:5])}等。"
        
        summary += f" 语言{analysis['language_complexity']['complexity_level']}，适合对{genre.replace('剧', '')}题材感兴趣的观众观看。"
        
        return summary

    def generate_viewing_suggestions(self, analysis: Dict) -> str:
        """生成观看建议"""
        suggestions = []
        
        # 基于语速的建议
        speaking_rate = analysis['average_speaking_rate']
        if speaking_rate > 8:
            suggestions.append("语速较快，建议专注观看，不要分心")
        elif speaking_rate < 5:
            suggestions.append("语速适中，适合轻松观看")
        
        # 基于复杂度的建议
        complexity = analysis['language_complexity']['complexity_level']
        if complexity == '高':
            suggestions.append("内容较为复杂，建议仔细理解专业术语")
        elif complexity == '中':
            suggestions.append("内容适中，一般观众容易理解")
        else:
            suggestions.append("内容通俗易懂，适合休闲观看")
        
        # 基于类型的建议
        genre = analysis['genre']
        if '法律' in genre:
            suggestions.append("涉及法律专业知识，可关注法律程序和术语解释")
        elif '犯罪' in genre:
            suggestions.append("注意线索收集过程，思考案件逻辑")
        
        return "；".join(suggestions) + "。"

    def extract_episode_number(self, filename: str) -> str:
        """提取集数"""
        match = re.search(r'[Ee](\d+)', filename)
        if match:
            return match.group(1)
        
        match = re.search(r'第(\d+)集', filename)
        if match:
            return match.group(1)
        
        match = re.search(r'(\d+)', filename)
        if match:
            return match.group(1)
        
        return "未知"

    def process_single_srt(self, filepath: str) -> bool:
        """处理单个SRT文件"""
        filename = os.path.basename(filepath)
        print(f"\n📝 分析: {filename}")
        
        # 解析字幕
        subtitles = self.parse_srt_file(filepath)
        if not subtitles:
            print(f"❌ 字幕解析失败")
            return False
        
        # 分析内容
        analysis = self.analyze_subtitle_content(subtitles)
        
        # 生成详细解释
        explanation = self.generate_detailed_explanation(subtitles, analysis, filename)
        
        # 保存结果
        output_filename = f"{os.path.splitext(filename)[0]}_详细解释.txt"
        output_path = os.path.join(self.output_folder, output_filename)
        
        try:
            platform_fix.safe_file_write(output_path, explanation)
            print(f"✅ 解释文件已保存: {output_filename}")
            
            # 生成简要统计
            print(f"📊 统计信息:")
            print(f"   字幕数量: {analysis['total_subtitles']} 条")
            print(f"   总时长: {analysis['total_duration']:.1f} 秒")
            print(f"   剧情类型: {analysis['genre']}")
            print(f"   精彩片段: {len(self.find_interesting_segments(subtitles))} 个")
            
            return True
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False

    def process_all_srt_files(self):
        """处理所有SRT文件"""
        print("\n🚀 开始批量SRT字幕分析")
        print("=" * 50)
        
        # 获取所有SRT文件
        srt_files = []
        for file in os.listdir(self.srt_folder):
            if file.endswith(('.srt', '.txt')) and not file.startswith('.'):
                srt_files.append(os.path.join(self.srt_folder, file))
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到SRT文件")
            return
        
        srt_files.sort()  # 按文件名排序
        print(f"📝 找到 {len(srt_files)} 个字幕文件")
        
        # 处理每个文件
        success_count = 0
        for srt_file in srt_files:
            try:
                if self.process_single_srt(srt_file):
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理 {os.path.basename(srt_file)} 失败: {e}")
        
        # 生成总结报告
        self.generate_summary_report(srt_files, success_count)
        
        print(f"\n📊 处理完成:")
        print(f"✅ 成功分析: {success_count}/{len(srt_files)} 个文件")
        print(f"📁 结果保存在: {self.output_folder}/ 目录")

    def generate_summary_report(self, srt_files: List[str], success_count: int):
        """生成总结报告"""
        report = f"""📺 SRT字幕分析总结报告
{'=' * 80}

📊 处理统计
• 总文件数：{len(srt_files)} 个
• 成功分析：{success_count} 个
• 失败数量：{len(srt_files) - success_count} 个
• 成功率：{success_count/len(srt_files)*100:.1f}%

📁 输出文件
"""
        
        # 列出所有输出文件
        output_files = [f for f in os.listdir(self.output_folder) if f.endswith('.txt')]
        for output_file in sorted(output_files):
            report += f"• {output_file}\n"
        
        report += f"""
🎯 分析特色
• 精准SRT字幕解析，智能错误修正
• 详细剧情类型识别和角色分析
• 通俗易懂的内容解释和观看建议
• 精彩片段自动识别和重点标注
• 语言复杂度和技术统计分析

💡 使用说明
每个解释文件包含：
1. 基本统计信息（时长、字数、语速等）
2. 剧情类型和角色识别
3. 精彩对话片段详细解析
4. 通俗易懂的内容解释
5. 个性化观看建议

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        report_path = os.path.join(self.output_folder, "分析总结报告.txt")
        platform_fix.safe_file_write(report_path, report)
        print(f"📋 总结报告已保存: 分析总结报告.txt")

    def show_main_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "=" * 50)
            print("📝 SRT字幕精准分析解释系统")
            print("=" * 50)
            
            print("\n🎯 主要功能:")
            print("1. 📖 分析单个SRT文件")
            print("2. 📚 批量分析所有SRT文件")
            print("3. 📁 查看文件状态")
            print("4. 🔧 检查系统环境")
            print("0. ❌ 退出系统")
            
            try:
                choice = input("\n请选择操作 (0-4): ").strip()
                
                if choice == '1':
                    self.analyze_single_file()
                elif choice == '2':
                    self.process_all_srt_files()
                elif choice == '3':
                    self.show_file_status()
                elif choice == '4':
                    self.check_system_status()
                elif choice == '0':
                    print("\n👋 感谢使用SRT字幕分析系统！")
                    break
                else:
                    print("❌ 无效选择，请输入0-4")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break
            except Exception as e:
                print(f"❌ 操作错误: {e}")

    def analyze_single_file(self):
        """分析单个文件"""
        srt_files = [f for f in os.listdir(self.srt_folder) 
                    if f.endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到SRT文件")
            return
        
        print(f"\n📝 可用的SRT文件:")
        for i, file in enumerate(srt_files, 1):
            print(f"{i}. {file}")
        
        try:
            choice = int(input(f"\n请选择文件 (1-{len(srt_files)}): "))
            if 1 <= choice <= len(srt_files):
                filepath = os.path.join(self.srt_folder, srt_files[choice-1])
                self.process_single_srt(filepath)
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入有效数字")

    def show_file_status(self):
        """显示文件状态"""
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        output_files = [f for f in os.listdir(self.output_folder) if f.endswith('.txt')]
        
        print(f"\n📊 文件状态:")
        print(f"📝 SRT字幕文件: {len(srt_files)} 个")
        for f in srt_files[:5]:
            print(f"   • {f}")
        if len(srt_files) > 5:
            print(f"   • ... 还有 {len(srt_files)-5} 个文件")
        
        print(f"📄 分析结果文件: {len(output_files)} 个")
        for f in output_files[:5]:
            print(f"   • {f}")
        if len(output_files) > 5:
            print(f"   • ... 还有 {len(output_files)-5} 个文件")

    def check_system_status(self):
        """检查系统状态"""
        print(f"\n🔧 系统状态检查:")
        print(f"📁 字幕目录: {self.srt_folder}/ {'✅ 存在' if os.path.exists(self.srt_folder) else '❌ 不存在'}")
        print(f"📁 输出目录: {self.output_folder}/ {'✅ 存在' if os.path.exists(self.output_folder) else '❌ 不存在'}")
        print(f"💾 缓存目录: {self.cache_folder}/ {'✅ 存在' if os.path.exists(self.cache_folder) else '❌ 不存在'}")
        print(f"🤖 AI配置: {'✅ 已配置' if self.ai_config.get('enabled') else '❌ 未配置'}")

def main():
    """主函数"""
    try:
        analyzer = SRTAnalyzerOnly()
        analyzer.show_main_menu()
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")

if __name__ == "__main__":
    main()

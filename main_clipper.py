
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一智能剪辑系统 - 清理后的完整解决方案
"""

import os
import re
import json
import subprocess
from typing import List, Dict, Optional
from api_config_helper import config_helper

class UnifiedVideoClipper:
    def __init__(self):
        self.config = config_helper.load_config()
        self.enabled = self.config.get('enabled', False)
        
        # 确保必要目录存在
        for dir_name in ['srt', 'videos', 'output_clips']:
            os.makedirs(dir_name, exist_ok=True)

    def process_all_episodes(self) -> Dict:
        """处理所有剧集"""
        print("🚀 启动统一智能剪辑系统")
        print("=" * 50)
        
        # 获取字幕文件
        srt_files = self.get_srt_files()
        if not srt_files:
            print("❌ 未找到字幕文件")
            return {}
        
        print(f"📺 找到 {len(srt_files)} 集")
        
        results = []
        
        for srt_file in srt_files:
            print(f"\n处理: {srt_file}")
            
            # 解析字幕
            subtitles = self.parse_srt(srt_file)
            if not subtitles:
                continue
            
            # AI分析（一次性分析整集）
            analysis = self.analyze_episode(subtitles, srt_file)
            
            # 识别精彩片段
            highlights = self.find_highlights(subtitles, analysis)
            
            # 创建视频片段
            created_clips = self.create_clips(srt_file, highlights)
            
            results.append({
                'episode': srt_file,
                'clips_created': len(created_clips),
                'clips': created_clips
            })
        
        self.generate_summary_report(results)
        return results

    def get_srt_files(self) -> List[str]:
        """获取字幕文件列表"""
        srt_dir = 'srt'
        if not os.path.exists(srt_dir):
            return []
        
        files = [f for f in os.listdir(srt_dir) if f.endswith('.srt')]
        files.sort()
        return files

    def parse_srt(self, srt_file: str) -> List[Dict]:
        """解析SRT字幕"""
        srt_path = os.path.join('srt', srt_file)
        
        try:
            with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 修正常见错误
            content = self.fix_subtitle_errors(content)
            
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
                            text = ' '.join(lines[2:]).strip()
                            
                            subtitles.append({
                                'index': index,
                                'start': start_time,
                                'end': end_time,
                                'text': text,
                                'start_seconds': self.time_to_seconds(start_time),
                                'end_seconds': self.time_to_seconds(end_time)
                            })
                    except (ValueError, IndexError):
                        continue
            
            print(f"  解析完成: {len(subtitles)} 条字幕")
            return subtitles
            
        except Exception as e:
            print(f"  解析失败: {e}")
            return []

    def fix_subtitle_errors(self, content: str) -> str:
        """修正常见字幕错误"""
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '設計': '设计', '開始': '开始', '結束': '结束',
            '聽證會': '听证会', '辯護': '辩护', '審判': '审判', '調查': '调查'
        }
        
        for old, new in corrections.items():
            content = content.replace(old, new)
        
        return content

    def analyze_episode(self, subtitles: List[Dict], episode_file: str) -> Dict:
        """AI分析整集内容"""
        if not self.enabled or not subtitles:
            return self.fallback_analysis(episode_file)
        
        # 构建完整文本（每10分钟一段，避免文本过长）
        full_text = self.build_episode_text(subtitles)
        
        # 提取集数
        episode_match = re.search(r'[Ee](\d+)', episode_file)
        episode_num = episode_match.group(1) if episode_match else "1"
        
        prompt = f"""分析第{episode_num}集电视剧内容，识别3-5个最精彩的片段用于制作短视频。

【剧情内容】
{full_text[:3000]}...

要求：
1. 每个片段要有完整的故事情节
2. 包含情感高潮或剧情转折
3. 时长2-3分钟最佳
4. 确保片段间连贯性

请返回JSON格式：
{{
    "episode_theme": "本集主题",
    "highlights": [
        {{
            "title": "片段标题",
            "time_range": "大约时间（如：10-13分钟）",
            "plot_point": "核心剧情点",
            "emotional_impact": "情感冲击",
            "key_content": "关键内容描述"
        }}
    ]
}}"""

        try:
            print(f"  🤖 调用AI分析...")
            response = config_helper.call_ai_api(prompt, self.config)
            if response:
                print(f"  ✅ AI分析完成")
                return self.parse_ai_response(response)
            else:
                print(f"  ⚠️ AI分析返回空结果，使用备用分析")
        except Exception as e:
            error_msg = str(e)
            if "10054" in error_msg or "远程主机" in error_msg:
                print(f"  🔌 网络连接中断 (Error 10054)")
                print(f"  💡 建议: 检查网络连接或更换API服务商")
            else:
                print(f"  ❌ AI分析失败: {e}")
        
        return self.fallback_analysis(episode_file)

    def build_episode_text(self, subtitles: List[Dict]) -> str:
        """构建完整剧情文本"""
        # 每600秒（10分钟）分一段
        segments = []
        current_segment = []
        last_time = 0
        
        for subtitle in subtitles:
            current_segment.append(subtitle['text'])
            
            if subtitle['start_seconds'] - last_time >= 600:
                segments.append(' '.join(current_segment))
                current_segment = []
                last_time = subtitle['start_seconds']
        
        if current_segment:
            segments.append(' '.join(current_segment))
        
        return '\n\n[时间段分割]\n\n'.join(segments)

    def parse_ai_response(self, response: str) -> Dict:
        """解析AI响应"""
        try:
            # 提取JSON部分
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_text = response[start:end]
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]
            
            return json.loads(json_text)
        except Exception as e:
            print(f"  解析AI响应失败: {e}")
            return {"highlights": []}

    def fallback_analysis(self, episode_file: str) -> Dict:
        """备用分析方法"""
        episode_match = re.search(r'[Ee](\d+)', episode_file)
        episode_num = episode_match.group(1) if episode_match else "1"
        
        return {
            "episode_theme": f"第{episode_num}集精彩内容",
            "highlights": [
                {
                    "title": f"第{episode_num}集精彩片段",
                    "time_range": "10-13分钟",
                    "plot_point": "重要剧情发展",
                    "emotional_impact": "情感高潮",
                    "key_content": "核心剧情内容"
                }
            ]
        }

    def find_highlights(self, subtitles: List[Dict], analysis: Dict) -> List[Dict]:
        """根据分析结果找到具体的字幕片段"""
        highlights = analysis.get('highlights', [])
        result_clips = []
        
        for highlight in highlights:
            # 解析时间范围
            time_range = highlight.get('time_range', '')
            time_match = re.search(r'(\d+)-(\d+)分钟', time_range)
            
            if time_match:
                start_min = int(time_match.group(1))
                end_min = int(time_match.group(2))
                
                start_seconds = start_min * 60
                end_seconds = end_min * 60
                
                # 找到对应字幕
                segment_subs = [sub for sub in subtitles 
                              if start_seconds <= sub['start_seconds'] <= end_seconds]
                
                if segment_subs:
                    # 确保句子完整
                    complete_segment = self.ensure_complete_sentences(segment_subs, subtitles)
                    
                    result_clips.append({
                        'title': highlight.get('title', '精彩片段'),
                        'subtitles': complete_segment,
                        'plot_point': highlight.get('plot_point', ''),
                        'emotional_impact': highlight.get('emotional_impact', ''),
                        'key_content': highlight.get('key_content', '')
                    })
        
        return result_clips

    def ensure_complete_sentences(self, segment_subs: List[Dict], all_subs: List[Dict]) -> List[Dict]:
        """确保句子完整性"""
        if not segment_subs:
            return []
        
        # 找到在全部字幕中的位置
        start_idx = next((i for i, sub in enumerate(all_subs) 
                         if sub['index'] == segment_subs[0]['index']), 0)
        end_idx = next((i for i, sub in enumerate(all_subs) 
                       if sub['index'] == segment_subs[-1]['index']), len(all_subs) - 1)
        
        # 向前扩展确保开头完整
        while start_idx > 0:
            prev_sub = all_subs[start_idx - 1]
            if prev_sub['text'].endswith(('。', '！', '？', '.', '!', '?')):
                break
            start_idx -= 1
        
        # 向后扩展确保结尾完整
        while end_idx < len(all_subs) - 1:
            current_sub = all_subs[end_idx]
            if current_sub['text'].endswith(('。', '！', '？', '.', '!', '?')):
                break
            end_idx += 1
        
        return all_subs[start_idx:end_idx + 1]

    def create_clips(self, episode_file: str, highlights: List[Dict]) -> List[str]:
        """创建视频片段"""
        video_file = self.find_video_file(episode_file)
        if not video_file:
            print(f"  未找到视频文件: {episode_file}")
            return []
        
        created_clips = []
        
        for i, highlight in enumerate(highlights, 1):
            clip_file = self.create_single_clip(video_file, highlight, episode_file, i)
            if clip_file:
                created_clips.append(clip_file)
                # 生成说明文件
                self.create_clip_description(clip_file, highlight)
        
        return created_clips

    def find_video_file(self, srt_file: str) -> Optional[str]:
        """查找对应的视频文件"""
        base_name = os.path.splitext(srt_file)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
        
        videos_dir = 'videos'
        if not os.path.exists(videos_dir):
            return None
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(videos_dir, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 集数匹配
        episode_match = re.search(r'[Ee](\d+)', base_name)
        if episode_match:
            episode_num = episode_match.group(1)
            
            for file in os.listdir(videos_dir):
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    file_episode = re.search(r'[Ee](\d+)', file)
                    if file_episode and file_episode.group(1) == episode_num:
                        return os.path.join(videos_dir, file)
        
        return None

    def create_single_clip(self, video_file: str, highlight: Dict, 
                          episode_file: str, clip_num: int) -> Optional[str]:
        """创建单个视频片段"""
        try:
            subtitles = highlight['subtitles']
            if not subtitles:
                return None
            
            # 计算时间
            start_time = subtitles[0]['start']
            end_time = subtitles[-1]['end']
            
            start_seconds = self.time_to_seconds(start_time) - 2  # 2秒缓冲
            end_seconds = self.time_to_seconds(end_time) + 2
            duration = end_seconds - start_seconds
            
            # 检查时长
            if duration < 30:  # 太短
                print(f"    片段过短，跳过: {duration:.1f}秒")
                return None
            
            if duration > 300:  # 超过5分钟，截取到5分钟
                duration = 300
            
            # 生成文件名
            episode_match = re.search(r'[Ee](\d+)', episode_file)
            ep_num = episode_match.group(1) if episode_match else "1"
            
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', highlight['title'])
            output_name = f"E{ep_num}_{clip_num:02d}_{safe_title}.mp4"
            output_path = os.path.join('output_clips', output_name)
            
            print(f"    剪辑: {highlight['title']} ({duration:.1f}秒)")
            
            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(max(0, start_seconds)),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-crf', '23',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"      ✅ 成功: {size_mb:.1f}MB")
                return output_path
            else:
                print(f"      ❌ 失败: {result.stderr[:100] if result.stderr else '未知错误'}")
                return None
                
        except Exception as e:
            print(f"      ❌ 剪辑出错: {e}")
            return None

    def create_clip_description(self, clip_file: str, highlight: Dict):
        """创建片段说明文件"""
        desc_file = clip_file.replace('.mp4', '_说明.txt')
        
        content = f"""📺 短视频片段说明
{"=" * 30}

片段标题: {highlight['title']}

核心剧情点: {highlight['plot_point']}

情感冲击: {highlight['emotional_impact']}

关键内容: {highlight['key_content']}

剪辑说明: 
本片段从完整剧情中精选，保持了故事的连贯性和完整性。
包含了重要的剧情转折和情感高潮，适合作为短视频展示。

时间轴对应:
"""
        
        # 添加字幕时间轴
        for subtitle in highlight['subtitles'][:5]:  # 显示前5条
            content += f"{subtitle['start']} --> {subtitle['end']}: {subtitle['text']}\n"
        
        if len(highlight['subtitles']) > 5:
            content += f"... 还有 {len(highlight['subtitles']) - 5} 条字幕\n"
        
        try:
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"      创建说明文件失败: {e}")

    def generate_summary_report(self, results: List[Dict]):
        """生成总结报告"""
        report_path = os.path.join('output_clips', '剪辑总结报告.txt')
        
        total_clips = sum(result['clips_created'] for result in results)
        
        content = f"""📺 智能剪辑系统 - 总结报告
{"=" * 50}

📊 总体统计:
• 处理集数: {len(results)} 集
• 创建短视频: {total_clips} 个
• 输出目录: output_clips/

📋 详细信息:
"""
        
        for result in results:
            content += f"\n{result['episode']}:\n"
            content += f"  • 创建短视频: {result['clips_created']} 个\n"
            
            for clip in result['clips']:
                clip_name = os.path.basename(clip)
                content += f"    - {clip_name}\n"
        
        content += f"\n💡 使用建议:\n"
        content += "• 每个短视频都有对应的说明文件\n"
        content += "• 建议按集数和序号顺序观看\n"
        content += "• 所有片段保持了剧情的连贯性\n"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📄 总结报告: {report_path}")
        except Exception as e:
            print(f"生成报告失败: {e}")

    def time_to_seconds(self, time_str: str) -> float:
        """时间转秒数"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0


def main():
    """主函数"""
    print("🎬 统一智能剪辑系统")
    print("=" * 40)
    
    clipper = UnifiedVideoClipper()
    
    # 检查环境
    srt_files = clipper.get_srt_files()
    if not srt_files:
        print("❌ srt/目录中没有字幕文件")
        print("请将.srt字幕文件放入srt/目录")
        return
    
    video_files = []
    if os.path.exists('videos'):
        video_files = [f for f in os.listdir('videos') 
                      if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    
    if not video_files:
        print("❌ videos/目录中没有视频文件")
        print("请将视频文件放入videos/目录")
        return
    
    print(f"✅ 找到 {len(srt_files)} 个字幕文件")
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    # 开始处理
    results = clipper.process_all_episodes()
    
    total_clips = sum(r['clips_created'] for r in results)
    print(f"\n🎉 处理完成!")
    print(f"📺 处理了 {len(results)} 集")
    print(f"🎬 创建了 {total_clips} 个短视频")
    print(f"📁 输出目录: output_clips/")


if __name__ == "__main__":
    main()

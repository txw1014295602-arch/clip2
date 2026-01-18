
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
稳定版智能剪辑系统 - 支持缓存和断点续传
解决API不稳定和剪辑一致性问题
"""

import os
import re
import json
import hashlib
import subprocess
from typing import List, Dict, Optional
from api_config_helper import config_helper

class StableVideoClipper:
    def __init__(self):
        self.config = config_helper.load_config()
        self.enabled = self.config.get('enabled', False)
        
        # 缓存目录
        self.cache_dir = "cache"
        self.analysis_cache_dir = os.path.join(self.cache_dir, "analysis")
        self.video_cache_dir = os.path.join(self.cache_dir, "videos")
        
        # 输入输出目录
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.output_folder = "stable_clips"
        
        # 创建必要目录
        for folder in [self.cache_dir, self.analysis_cache_dir, self.video_cache_dir, 
                      self.srt_folder, self.videos_folder, self.output_folder]:
            os.makedirs(folder, exist_ok=True)

    def get_file_hash(self, filepath: str) -> str:
        """计算文件内容的哈希值，用于缓存key"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return hashlib.md5(content.encode()).hexdigest()
        except:
            return hashlib.md5(filepath.encode()).hexdigest()

    def get_analysis_cache_path(self, srt_file: str) -> str:
        """获取分析结果缓存路径"""
        file_hash = self.get_file_hash(os.path.join(self.srt_folder, srt_file))
        return os.path.join(self.analysis_cache_dir, f"{file_hash}.json")

    def load_cached_analysis(self, srt_file: str) -> Optional[Dict]:
        """加载缓存的分析结果"""
        cache_path = self.get_analysis_cache_path(srt_file)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                print(f"  📋 使用缓存分析: {os.path.basename(cache_path)}")
                return cached_data
            except Exception as e:
                print(f"  ⚠ 加载缓存失败: {e}")
        return None

    def save_analysis_cache(self, srt_file: str, analysis: Dict):
        """保存分析结果到缓存"""
        cache_path = self.get_analysis_cache_path(srt_file)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"  💾 保存分析缓存: {os.path.basename(cache_path)}")
        except Exception as e:
            print(f"  ⚠ 保存缓存失败: {e}")

    def get_clip_cache_path(self, analysis_hash: str, clip_index: int) -> str:
        """获取视频片段缓存路径"""
        return os.path.join(self.video_cache_dir, f"{analysis_hash}_clip_{clip_index}.mp4")

    def get_analysis_hash(self, analysis: Dict) -> str:
        """计算分析结果的哈希值"""
        analysis_str = json.dumps(analysis, sort_keys=True)
        return hashlib.md5(analysis_str.encode()).hexdigest()

    def is_clip_cached(self, analysis: Dict, clip_index: int) -> str:
        """检查视频片段是否已缓存"""
        analysis_hash = self.get_analysis_hash(analysis)
        cache_path = self.get_clip_cache_path(analysis_hash, clip_index)
        
        if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            return cache_path
        return None

    def process_all_episodes(self) -> Dict:
        """处理所有剧集 - 支持缓存和断点续传"""
        print("🚀 启动稳定版智能剪辑系统 (支持缓存)")
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
            
            # 1. 尝试加载缓存的分析结果
            analysis = self.load_cached_analysis(srt_file)
            
            if not analysis:
                # 2. 解析字幕
                subtitles = self.parse_srt(srt_file)
                if not subtitles:
                    continue
                
                # 3. 执行AI分析
                analysis = self.analyze_episode_with_retry(subtitles, srt_file)
                if analysis:
                    # 保存分析结果到缓存
                    self.save_analysis_cache(srt_file, analysis)
                else:
                    print(f"  ❌ 分析失败，跳过")
                    continue
            
            # 4. 创建视频片段（支持断点续传）
            created_clips = self.create_clips_with_cache(srt_file, analysis)
            
            results.append({
                'episode': srt_file,
                'clips_created': len(created_clips),
                'clips': created_clips,
                'analysis': analysis
            })
        
        self.generate_summary_report(results)
        return results

    def analyze_episode_with_retry(self, subtitles: List[Dict], episode_file: str, max_retries: int = 3) -> Dict:
        """AI分析（带重试机制）"""
        if not self.enabled or not subtitles:
            return self.fallback_analysis(episode_file)
        
        # 构建完整文本
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
5. 提供精确的时间范围

请返回JSON格式：
{{
    "episode_theme": "本集主题",
    "highlights": [
        {{
            "title": "片段标题",
            "start_time": "00:10:30,000",
            "end_time": "00:13:45,000",
            "plot_point": "核心剧情点",
            "emotional_impact": "情感冲击",
            "key_content": "关键内容描述"
        }}
    ]
}}"""

        for attempt in range(max_retries):
            try:
                print(f"  🤖 AI分析尝试 {attempt + 1}/{max_retries}")
                response = config_helper.call_ai_api(prompt, self.config)ll_ai_api(prompt, self.config)
                if response:
                    analysis = self.parse_ai_response(response)
                    if analysis.get('highlights'):
                        print(f"  ✅ AI分析成功")
                        return analysis
                    else:
                        print(f"  ⚠️ AI分析返回空结果")
                else:
                    print(f"  ⚠️ AI API返回空响应")
                    
            except Exception as e:
                print(f"  ❌ AI分析失败 (尝试 {attempt + 1}): {e}")
                
            if attempt < max_retries - 1:
                print(f"  ⏰ 等待2秒后重试...")
                import time
                time.sleep(2)
        
        print(f"  ❌ AI分析最终失败，使用备用方案")
        return self.fallback_analysis(episode_file)

    def create_clips_with_cache(self, episode_file: str, analysis: Dict) -> List[str]:
        """创建视频片段（支持缓存）"""
        video_file = self.find_video_file(episode_file)
        if not video_file:
            print(f"  未找到视频文件: {episode_file}")
            return []
        
        highlights = analysis.get('highlights', [])
        if not highlights:
            print(f"  没有可剪辑的片段")
            return []
        
        created_clips = []
        analysis_hash = self.get_analysis_hash(analysis)
        
        print(f"  🎬 开始剪辑 {len(highlights)} 个片段")
        
        for i, highlight in enumerate(highlights):
            # 检查是否已缓存
            cached_clip = self.is_clip_cached(analysis, i)
            if cached_clip:
                # 复制缓存文件到输出目录
                output_name = self.generate_output_name(episode_file, i, highlight['title'])
                output_path = os.path.join(self.output_folder, output_name)
                
                try:
                    import shutil
                    shutil.copy2(cached_clip, output_path)
                    print(f"    ✅ 使用缓存: {output_name}")
                    created_clips.append(output_path)
                    
                    # 创建说明文件
                    self.create_clip_description(output_path, highlight)
                    continue
                except Exception as e:
                    print(f"    ⚠ 复制缓存失败: {e}")
            
            # 执行剪辑
            clip_path = self.create_single_clip_with_retry(video_file, highlight, episode_file, i)
            if clip_path:
                # 保存到缓存
                cache_path = self.get_clip_cache_path(analysis_hash, i)
                try:
                    import shutil
                    shutil.copy2(clip_path, cache_path)
                    print(f"    💾 保存剪辑缓存")
                except Exception as e:
                    print(f"    ⚠ 保存剪辑缓存失败: {e}")
                
                created_clips.append(clip_path)
                self.create_clip_description(clip_path, highlight)
        
        return created_clips

    def create_single_clip_with_retry(self, video_file: str, highlight: Dict, 
                                    episode_file: str, clip_num: int, max_retries: int = 3) -> Optional[str]:
        """创建单个视频片段（带重试）"""
        start_time = highlight.get('start_time')
        end_time = highlight.get('end_time')
        
        if not start_time or not end_time:
            print(f"    ❌ 时间信息不完整")
            return None
        
        output_name = self.generate_output_name(episode_file, clip_num, highlight['title'])
        output_path = os.path.join(self.output_folder, output_name)
        
        for attempt in range(max_retries):
            try:
                print(f"    🎬 剪辑片段 {clip_num + 1} (尝试 {attempt + 1})")
                print(f"        时间: {start_time} --> {end_time}")
                print(f"        标题: {highlight['title']}")
                
                if self.cut_precise_segment(video_file, start_time, end_time, output_path):
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"        ✅ 剪辑成功: {size_mb:.1f}MB")
                    return output_path
                else:
                    print(f"        ❌ 剪辑失败 (尝试 {attempt + 1})")
                    
            except Exception as e:
                print(f"        ❌ 剪辑异常 (尝试 {attempt + 1}): {e}")
                
            if attempt < max_retries - 1:
                print(f"        ⏰ 等待3秒后重试...")
                import time
                time.sleep(3)
        
        print(f"    ❌ 剪辑最终失败")
        return None

    def generate_output_name(self, episode_file: str, clip_num: int, title: str) -> str:
        """生成输出文件名"""
        episode_match = re.search(r'[Ee](\d+)', episode_file)
        ep_num = episode_match.group(1) if episode_match else "1"
        
        safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', title)[:20]
        return f"E{ep_num}_{clip_num + 1:02d}_{safe_title}.mp4"

    def get_srt_files(self) -> List[str]:
        """获取字幕文件列表"""
        if not os.path.exists(self.srt_folder):
            return []
        
        files = [f for f in os.listdir(self.srt_folder) if f.endswith('.srt')]
        files.sort()
        return files

    def parse_srt(self, srt_file: str) -> List[Dict]:
        """解析SRT字幕"""
        srt_path = os.path.join(self.srt_folder, srt_file)
        
        try:
            with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
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

    def build_episode_text(self, subtitles: List[Dict]) -> str:
        """构建完整剧情文本"""
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
            "highlights": []
        }

    def find_video_file(self, srt_file: str) -> Optional[str]:
        """查找对应的视频文件"""
        base_name = os.path.splitext(srt_file)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
        
        if not os.path.exists(self.videos_folder):
            return None
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 集数匹配
        episode_match = re.search(r'[Ee](\d+)', base_name)
        if episode_match:
            episode_num = episode_match.group(1)
            
            for file in os.listdir(self.videos_folder):
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    file_episode = re.search(r'[Ee](\d+)', file)
                    if file_episode and file_episode.group(1) == episode_num:
                        return os.path.join(self.videos_folder, file)
        
        return None

    def cut_precise_segment(self, video_file: str, start_time: str, end_time: str, output_path: str) -> bool:
        """精确剪切视频片段"""
        try:
            start_seconds = self.time_to_seconds(start_time) - 1  # 1秒缓冲
            end_seconds = self.time_to_seconds(end_time) + 1
            duration = end_seconds - start_seconds
            
            if duration <= 0:
                return False
            
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
            
            return result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0
            
        except Exception as e:
            print(f"      剪辑出错: {e}")
            return False

    def create_clip_description(self, clip_file: str, highlight: Dict):
        """创建片段说明文件"""
        desc_file = clip_file.replace('.mp4', '_说明.txt')
        
        content = f"""📺 短视频片段说明
{"=" * 30}

片段标题: {highlight.get('title', '未知')}
核心剧情点: {highlight.get('plot_point', '未知')}
情感冲击: {highlight.get('emotional_impact', '未知')}
关键内容: {highlight.get('key_content', '未知')}

时间轴: {highlight.get('start_time', '')} --> {highlight.get('end_time', '')}

剪辑说明: 
本片段通过AI智能分析生成，保持了完整的故事连贯性。
"""
        
        try:
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"      创建说明文件失败: {e}")

    def generate_summary_report(self, results: List[Dict]):
        """生成总结报告"""
        report_path = os.path.join(self.output_folder, '稳定剪辑总结报告.txt')
        
        total_clips = sum(result['clips_created'] for result in results)
        
        content = f"""📺 稳定版智能剪辑系统 - 总结报告
{"=" * 50}

📊 总体统计:
• 处理集数: {len(results)} 集
• 创建短视频: {total_clips} 个
• 输出目录: {self.output_folder}/
• 缓存目录: {self.cache_dir}/

🔄 缓存机制:
• AI分析结果缓存: {self.analysis_cache_dir}/
• 视频片段缓存: {self.video_cache_dir}/
• 支持断点续传和重复执行

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
        content += "• 缓存保证了多次执行的一致性\n"
        content += "• 支持断点续传，已处理的片段不会重复\n"
        
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

    def clean_old_cache(self, days: int = 7):
        """清理旧缓存文件"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 3600)
        
        cleaned_count = 0
        
        for cache_dir in [self.analysis_cache_dir, self.video_cache_dir]:
            if os.path.exists(cache_dir):
                for file in os.listdir(cache_dir):
                    file_path = os.path.join(cache_dir, file)
                    if os.path.getmtime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                        except:
                            pass
        
        if cleaned_count > 0:
            print(f"🧹 清理了 {cleaned_count} 个过期缓存文件")


def main():
    """主函数"""
    print("🎬 稳定版智能剪辑系统")
    print("=" * 40)
    
    clipper = StableVideoClipper()
    
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
    
    # 清理旧缓存
    clipper.clean_old_cache()
    
    # 开始处理
    results = clipper.process_all_episodes()
    
    total_clips = sum(r['clips_created'] for r in results)
    print(f"\n🎉 处理完成!")
    print(f"📺 处理了 {len(results)} 集")
    print(f"🎬 创建了 {total_clips} 个短视频")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"💾 缓存目录: {clipper.cache_dir}/")


if __name__ == "__main__":
    main()

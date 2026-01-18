#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
稳定AI剪辑系统
解决问题：
1. AI分析失败直接结束，不使用备用分析
2. 分析结果缓存，避免重复API调用
3. 剪辑结果缓存，避免重复剪辑
4. 保证多次执行的一致性
5. 合理的上下文长度
6. 正确的时间段验证
"""

import os
import re
import json
import hashlib
import subprocess
from typing import List, Dict, Optional
from datetime import datetime

class StableAIClipper:
    def __init__(self):
        self.config = self.load_ai_config()
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.output_folder = "stable_clips"
        self.cache_folder = "analysis_cache"

        # 创建必要目录
        for folder in [self.srt_folder, self.videos_folder, self.output_folder, self.cache_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✓ 创建目录: {folder}/")

    def load_ai_config(self) -> Dict:
        """加载AI配置"""
        try:
            with open('.ai_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            print("❌ 未找到AI配置文件，请先运行 python configure_ai.py")
            return {'enabled': False}

    def get_file_hash(self, filepath: str) -> str:
        """获取文件内容的哈希值，用于缓存键"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return hashlib.md5(content.encode()).hexdigest()[:16]
        except:
            return "unknown"

    def get_analysis_cache_path(self, srt_file: str) -> str:
        """获取分析缓存文件路径"""
        file_hash = self.get_file_hash(srt_file)
        base_name = os.path.splitext(os.path.basename(srt_file))[0]
        return os.path.join(self.cache_folder, f"{base_name}_{file_hash}_analysis.json")

    def load_cached_analysis(self, srt_file: str) -> Optional[Dict]:
        """加载缓存的分析结果"""
        cache_path = self.get_analysis_cache_path(srt_file)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                print(f"📂 加载缓存分析: {os.path.basename(srt_file)}")
                return analysis
            except Exception as e:
                print(f"⚠ 缓存读取失败: {e}")
        return None

    def save_analysis_cache(self, srt_file: str, analysis: Dict):
        """保存分析结果到缓存"""
        cache_path = self.get_analysis_cache_path(srt_file)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"💾 保存分析缓存: {os.path.basename(srt_file)}")
        except Exception as e:
            print(f"⚠ 缓存保存失败: {e}")

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT字幕文件"""
        try:
            # 多编码尝试
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except:
                    continue

            # 解析SRT格式
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
                            text = '\n'.join(lines[2:]).strip()

                            if text:
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

            return subtitles
        except Exception as e:
            print(f"❌ 解析字幕文件失败 {filepath}: {e}")
            return []

    def build_smart_context(self, subtitles: List[Dict]) -> str:
        """构建智能上下文 - 全文分析"""
        if not subtitles:
            return ""

        # 构建完整上下文，保留所有对话的连贯性
        context_parts = []
        for sub in subtitles:
            context_parts.append(f"[{sub['start']}] {sub['text']}")

        context = '\n'.join(context_parts)
        print(f"📝 构建完整上下文: 总计{len(subtitles)}条字幕")
        return context

    def ai_analyze_episode(self, subtitles: List[Dict], srt_file: str) -> Optional[Dict]:
        """AI分析整集内容"""
        if not self.config.get('enabled'):
            print("❌ AI未启用，无法进行分析")
            return None

        episode_num = self.extract_episode_number(srt_file)
        context = self.build_smart_context(subtitles)

        prompt = f"""你是专业的电视剧剪辑师。请分析这一集的内容，识别出2-3个最精彩的片段用于短视频制作。

【集数】第{episode_num}集
【完整剧情内容】
{context}

请进行深度分析并返回JSON格式：
{{
    "episode_analysis": {{
        "main_plot": "主要剧情线描述",
        "key_characters": ["主要角色1", "主要角色2"],
        "plot_points": ["关键情节点1", "关键情节点2"],
        "emotional_tone": "整体情感基调"
    }},
    "clips": [
        {{
            "clip_id": 1,
            "title": "片段标题",
            "start_time": "00:05:30,000",
            "end_time": "00:08:15,000",
            "plot_significance": "剧情意义说明",
            "dramatic_elements": ["戏剧元素1", "戏剧元素2"],
            "narration": {{
                "opening": "开场解说",
                "context": "背景解释", 
                "climax": "高潮解说",
                "conclusion": "结论总结"
            }},
            "hook_reason": "为什么这个片段吸引人"
        }}
    ],
    "episode_summary": "本集完整剧情概述"
}}

要求：
1. 每个片段1-3分钟，起始时间必须在字幕时间范围内
2. 片段要包含完整的戏剧结构
3. 时间格式严格按照 HH:MM:SS,mmm 格式
"""

        try:
            response = self.call_ai_api(prompt)
            if not response:
                print("❌ AI API调用失败")
                return None

            # 解析JSON响应
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_text = response[json_start:json_end]
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_text = response[start:end]

            analysis = json.loads(json_text)

            # 验证时间段
            validated_clips = []
            for clip in analysis.get('clips', []):
                if self.validate_time_segment(clip, subtitles):
                    validated_clips.append(clip)

            if not validated_clips:
                print("❌ 没有有效的片段")
                return None

            analysis['clips'] = validated_clips
            return analysis

        except Exception as e:
            print(f"❌ AI分析失败: {e}")
            return None

    def validate_time_segment(self, clip: Dict, subtitles: List[Dict]) -> bool:
        """验证时间段是否合理"""
        try:
            start_time = clip.get('start_time', '')
            end_time = clip.get('end_time', '')

            if not start_time or not end_time:
                return False

            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)

            # 检查时间顺序
            if start_seconds >= end_seconds:
                return False

            # 检查时间段长度
            duration = end_seconds - start_seconds
            if duration < 30 or duration > 300:  # 30秒到5分钟
                return False

            # 检查是否在字幕范围内
            if subtitles:
                subtitle_start = subtitles[0]['start_seconds']
                subtitle_end = subtitles[-1]['end_seconds']

                if start_seconds < subtitle_start or end_seconds > subtitle_end:
                    return False

            return True

        except Exception as e:
            print(f"⚠ 时间段验证失败: {e}")
            return False

    def call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        try:
            import requests

            if self.config.get('api_type') == 'official':
                if self.config.get('model_provider') == 'gemini':
                    return self._call_gemini_api(prompt)
                else:
                    return self._call_official_api(prompt)
            else:
                return self._call_proxy_api(prompt)

        except Exception as e:
            print(f"❌ API调用异常: {e}")
            return None

    def _call_proxy_api(self, prompt: str) -> Optional[str]:
        """调用中转API"""
        try:
            import requests

            payload = {
                "model": self.config['model'],
                "messages": [
                    {"role": "system", "content": "你是专业的影视剪辑师和剧情分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000,
                "temperature": 0.7
            }

            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }

            url = self.config['base_url'].rstrip('/') + "/chat/completions"

            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"❌ API调用失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 中转API调用失败: {e}")
            return None

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai

            client = genai.Client(api_key=self.config['api_key'])
            response = client.models.generate_content(
                model=self.config['model'],
                contents=prompt
            )
            return response.text

        except ImportError:
            print("❌ 缺少google-genai库")
            return None
        except Exception as e:
            print(f"❌ Gemini API调用失败: {e}")
            return None

    def _call_official_api(self, prompt: str) -> Optional[str]:
        """调用其他官方API"""
        try:
            import requests

            payload = {
                "model": self.config['model'],
                "messages": [
                    {"role": "system", "content": "你是专业的影视剪辑师和剧情分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000,
                "temperature": 0.7
            }

            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }

            url = self.config.get('base_url', 'https://api.openai.com/v1').rstrip('/') + "/chat/completions"

            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"❌ 官方API调用失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 官方API调用失败: {e}")
            return None

    def get_video_clip_path(self, analysis: Dict, clip: Dict) -> str:
        """获取视频片段路径"""
        episode_num = analysis.get('episode_number', '00')
        clip_id = clip.get('clip_id', 1)
        title = re.sub(r'[^\w\-_\.]', '_', clip.get('title', '片段'))[:20]
        return os.path.join(self.output_folder, f"E{episode_num}_C{clip_id:02d}_{title}.mp4")

    def is_clip_already_created(self, clip_path: str) -> bool:
        """检查视频片段是否已经创建"""
        return os.path.exists(clip_path) and os.path.getsize(clip_path) > 1024

    def find_matching_video(self, srt_file: str) -> Optional[str]:
        """查找匹配的视频文件"""
        base_name = os.path.splitext(os.path.basename(srt_file))[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 模糊匹配
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                file_base = os.path.splitext(filename)[0]
                episode_match = re.search(r'[Ee](\d+)', base_name)
                video_match = re.search(r'[Ee](\d+)', file_base)

                if episode_match and video_match and episode_match.group(1) == video_match.group(1):
                    return os.path.join(self.videos_folder, filename)

        return None

    def create_video_clip(self, video_file: str, clip: Dict, clip_path: str) -> bool:
        """创建单个视频片段"""
        try:
            if self.is_clip_already_created(clip_path):
                print(f"    ✓ 片段已存在: {os.path.basename(clip_path)}")
                return True

            start_seconds = self.time_to_seconds(clip['start_time'])
            end_seconds = self.time_to_seconds(clip['end_time'])
            duration = end_seconds - start_seconds

            print(f"    🎬 剪辑片段: {os.path.basename(clip_path)}")
            print(f"       时间: {clip['start_time']} --> {clip['end_time']}")

            # 验证时间段
            if duration <= 0:
                print(f"       ❌ 无效时间段: 持续时间 {duration:.1f}秒")
                return False

            if start_seconds < 0:
                print(f"       ❌ 无效时间段: 开始时间为负数")
                return False

            print(f"       ✓ 时间段有效: {duration:.1f}秒")

            # FFmpeg剪切命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                '-movflags', '+faststart',
                clip_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and os.path.exists(clip_path):
                if os.path.getsize(clip_path) > 1024:
                    file_size = os.path.getsize(clip_path) / (1024 * 1024)
                    print(f"       ✅ 创建成功: {file_size:.1f}MB")
                    return True
                else:
                    print(f"       ❌ 输出文件太小")
                    if os.path.exists(clip_path):
                        os.remove(clip_path)
                    return False
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"
                print(f"       ❌ 剪切失败: {error_msg}")
                return False

        except subprocess.TimeoutExpired:
            print(f"       ❌ 剪切超时")
            return False
        except Exception as e:
            print(f"       ❌ 处理出错: {e}")
            return False

    def process_single_episode(self, srt_file: str) -> bool:
        """处理单集"""
        print(f"\n🎬 处理: {os.path.basename(srt_file)}")

        # 检查缓存的分析结果
        cached_analysis = self.load_cached_analysis(srt_file)

        if cached_analysis:
            analysis = cached_analysis
        else:
            # 解析字幕
            subtitles = self.parse_srt_file(srt_file)
            if not subtitles:
                print("  ❌ 字幕解析失败")
                return False

            print(f"  📝 解析字幕: {len(subtitles)} 条")

            # AI分析
            analysis = self.ai_analyze_episode(subtitles, srt_file)
            if not analysis:
                print("  ❌ AI分析失败，跳过此集")
                return False

            # 添加集数信息
            analysis['episode_number'] = self.extract_episode_number(srt_file)

            # 保存分析结果
            self.save_analysis_cache(srt_file, analysis)

        print(f"  🎯 识别精彩片段: {len(analysis['clips'])} 个")

        # 查找视频文件
        video_file = self.find_matching_video(srt_file)
        if not video_file:
            print("  ❌ 未找到匹配的视频文件")
            return False

        print(f"  📹 匹配视频: {os.path.basename(video_file)}")

        # 创建视频片段
        success_count = 0
        for clip in analysis['clips']:
            clip_path = self.get_video_clip_path(analysis, clip)
            if self.create_video_clip(video_file, clip, clip_path):
                success_count += 1

        if success_count > 0:
            # 创建说明文档
            self.create_episode_description(analysis, srt_file)
            print(f"  ✅ 完成: {success_count}/{len(analysis['clips'])} 个片段")
            return True
        else:
            print(f"  ❌ 没有成功创建任何片段")
            return False

    def create_episode_description(self, analysis: Dict, srt_file: str):
        """创建集数说明文档"""
        episode_number = analysis['episode_number']
        desc_path = os.path.join(self.output_folder, f"E{episode_number}_剧情解析.txt")

        content = f"""📺 第{episode_number}集 AI剧情解析报告
{'=' * 80}

🎭 剧情分析:
主要剧情线: {analysis['episode_analysis'].get('main_plot', '未知')}
主要角色: {', '.join(analysis['episode_analysis'].get('key_characters', []))}
情感基调: {analysis['episode_analysis'].get('emotional_tone', '未知')}

📋 剧情要点:
"""
        for point in analysis['episode_analysis'].get('plot_points', []):
            content += f"• {point}\n"

        content += f"""

🎬 精彩片段详情 ({len(analysis['clips'])}个):
"""

        for clip in analysis['clips']:
            content += f"""
片段 {clip['clip_id']}: {clip['title']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ 时间: {clip['start_time']} --> {clip['end_time']}
🎯 剧情意义: {clip['plot_significance']}
🎭 戏剧元素: {', '.join(clip['dramatic_elements'])}
🎪 吸引点: {clip['hook_reason']}

📝 专业旁白解说:
开场: {clip['narration'].get('opening', '')}
背景: {clip['narration'].get('context', '')}
高潮: {clip['narration'].get('climax', '')}
结论: {clip['narration'].get('conclusion', '')}
"""

        content += f"""

📖 本集完整概述:
{analysis['episode_summary']}

📊 技术信息:
• 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• 源文件: {os.path.basename(srt_file)}
• AI分析: 是
"""

        with open(desc_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"    📄 生成解析文档: E{episode_number}_剧情解析.txt")

    def extract_episode_number(self, filename: str) -> str:
        """提取集数"""
        base_name = os.path.splitext(os.path.basename(filename))[0]
        return base_name

    def time_to_seconds(self, time_str: str) -> float:
        """时间转秒"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

    def run_complete_analysis(self):
        """运行完整分析流程"""
        print("🚀 启动稳定AI剪辑系统")
        print("=" * 60)

        # 检查AI配置
        if not self.config.get('enabled'):
            print("❌ AI配置未启用，请先运行: python configure_ai.py")
            return

        print(f"🤖 AI模型: {self.config.get('model_provider', 'unknown')} / {self.config.get('model', 'unknown')}")
        print(f"📂 缓存目录: {self.cache_folder}/")

        # 获取所有SRT文件
        srt_files = []

        # 检查当前目录
        for file in os.listdir('.'):
            if file.endswith('.srt') or file.endswith('.txt'):
                if any(char.isdigit() for char in file):  # 包含数字的文件
                    srt_files.append(file)

        # 检查srt目录
        if os.path.exists(self.srt_folder):
            for file in os.listdir(self.srt_folder):
                if file.endswith('.srt') or file.endswith('.txt'):
                    srt_files.append(os.path.join(self.srt_folder, file))

        if not srt_files:
            print("❌ 未找到字幕文件")
            return

        srt_files.sort()
        print(f"✅ 找到 {len(srt_files)} 个字幕文件")

        # 检查视频目录
        video_files = []
        if os.path.exists(self.videos_folder):
            video_files = [f for f in os.listdir(self.videos_folder) 
                          if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]

        if not video_files:
            print("❌ videos目录中没有视频文件")
            return

        print(f"✅ 找到 {len(video_files)} 个视频文件")

        # 处理所有集数
        success_count = 0
        for srt_file in srt_files:
            try:
                if self.process_single_episode(srt_file):
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理失败 {srt_file}: {e}")

        print(f"\n📊 处理完成统计:")
        print(f"✅ 成功处理: {success_count}/{len(srt_files)} 集")
        print(f"📁 输出目录: {self.output_folder}/")
        print(f"💾 缓存目录: {self.cache_folder}/")

def main():
    """主函数"""
    clipper = StableAIClipper()
    clipper.run_complete_analysis()

if __name__ == "__main__":
    main()
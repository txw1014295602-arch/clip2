#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能视频剪辑器 - 实现精准剪辑和专业字幕
"""

import os
import json
import subprocess
from typing import List, Dict, Optional
from smart_analyzer import analyze_all_episodes_smartly

class SmartVideoClipper:
    def __init__(self, video_folder: str = "videos", output_folder: str = "clips"):
        self.video_folder = video_folder
        self.output_folder = output_folder

        # 创建输出文件夹
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"✓ 创建输出目录: {self.output_folder}/")

    def get_video_file(self, episode_subtitle_name: str) -> Optional[str]:
        """根据字幕文件名找到对应视频"""
        base_name = os.path.basename(episode_subtitle_name)
        base_name = base_name.replace('.txt', '').replace('.srt', '')

        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']

        # 检查videos目录
        if not os.path.exists(self.video_folder):
            print(f"❌ 视频目录不存在: {self.video_folder}")
            return None

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 模糊匹配
        for file in os.listdir(self.video_folder):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                file_base = os.path.splitext(file)[0]

                # 提取集数信息进行匹配
                import re
                subtitle_episode = re.search(r'[se](\d+)[ex](\d+)', base_name.lower())
                video_episode = re.search(r'[se](\d+)[ex](\d+)', file_base.lower())

                if subtitle_episode and video_episode:
                    if subtitle_episode.groups() == video_episode.groups():
                        return os.path.join(self.video_folder, file)

        print(f"⚠ 未找到匹配的视频文件: {base_name}")
        return None

    def create_single_clip(self, video_file: str, plan: Dict) -> bool:
        """创建单个短视频片段"""
        try:
            segment = plan['segment']

            # 获取时间信息
            start_seconds = self.time_to_seconds(segment['start_time'])
            end_seconds = self.time_to_seconds(segment['end_time'])
            duration = end_seconds - start_seconds

            # 智能缓冲时间，确保完整场景
            buffer_start = max(0, start_seconds - 3)  # 前3秒缓冲
            buffer_end = end_seconds + 3              # 后3秒缓冲
            actual_duration = buffer_end - buffer_start

            # 输出文件名
            safe_theme = plan['theme'].replace('：', '_').replace('/', '_').replace('?', '').replace('*', '')
            output_name = f"{safe_theme}.mp4"
            output_path = os.path.join(self.output_folder, output_name)

            print(f"  🎯 剪辑: {segment['start_time']} --> {segment['end_time']} (实际: {actual_duration:.1f}秒)")

            # 第一步：精确剪辑
            temp_clip = output_path.replace('.mp4', '_temp.mp4')

            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(actual_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-crf', '20',  # 高质量
                '-preset', 'medium',
                '-movflags', '+faststart',
                '-avoid_negative_ts', 'make_zero',
                temp_clip,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, 
                                          timeout=300, encoding='utf-8', errors='ignore')

            if result.returncode != 0:
                print(f"    ❌ 视频剪辑失败: {result.stderr[:100]}")
                return False

            # 第二步：添加专业字幕和标题
            success = self.add_professional_overlay(temp_clip, plan, output_path)

            # 清理临时文件
            if os.path.exists(temp_clip):
                os.remove(temp_clip)

            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"    ✅ 生成短视频: {os.path.basename(output_path)} ({file_size:.1f}MB)")
                return True
            else:
                print(f"    ❌ 添加字幕失败")
                return False

        except Exception as e:
            print(f"    ❌ 处理出错: {e}")
            return False

    def add_professional_overlay(self, video_path: str, plan: Dict, output_path: str) -> bool:
        """添加专业字幕和标题"""
        try:
            theme = plan['theme']
            significance = plan['plot_significance']
            highlights = ', '.join(plan['content_highlights'][:2])  # 取前2个亮点

            # 清理文本，避免FFmpeg错误
            title_text = theme.replace("'", "").replace('"', '').replace(':', '-')[:35]
            content_text = significance.replace("'", "").replace('"', '')[:30]
            highlight_text = highlights.replace("'", "").replace('"', '')[:40]

            # 构建字幕滤镜
            filter_parts = []

            # 主标题 (0-4秒)
            filter_parts.append(
                f"drawtext=text='{title_text}':fontsize=28:fontcolor=white:x=(w-text_w)/2:y=60:"
                f"box=1:boxcolor=black@0.8:boxborderw=6:enable='between(t,0,4)'"
            )

            # 剧情意义 (1-5秒)
            filter_parts.append(
                f"drawtext=text='{content_text}':fontsize=18:fontcolor=yellow:x=(w-text_w)/2:y=110:"
                f"box=1:boxcolor=black@0.7:boxborderw=4:enable='between(t,1,5)'"
            )

            # 内容亮点 (6秒后)
            filter_parts.append(
                f"drawtext=text='{highlight_text}':fontsize=16:fontcolor=lightblue:x=(w-text_w)/2:y=(h-80):"
                f"box=1:boxcolor=black@0.6:boxborderw=3:enable='gt(t,6)'"
            )

            # 精彩标识
            filter_parts.append(
                f"drawtext=text='🔥 精彩片段':fontsize=14:fontcolor=red:x=20:y=20:"
                f"box=1:boxcolor=black@0.6:boxborderw=3:enable='gt(t,2)'"
            )

            filter_text = ",".join(filter_parts)

            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_text,
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '22',
                output_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, 
                                          timeout=120, encoding='utf-8', errors='ignore')

            return result.returncode == 0

        except Exception as e:
            print(f"    ⚠ 添加字幕失败: {e}")
            return False

    def create_episode_clips(self, plans: List[Dict]) -> List[str]:
        """为所有集数创建短视频"""
        print(f"\n🎬 开始创建短视频 ({len(plans)} 集)")
        print("=" * 60)

        created_clips = []

        for plan in plans:
            episode_file = plan['episode']
            video_file = self.get_video_file(episode_file)

            if not video_file:
                print(f"❌ 未找到视频文件: {os.path.basename(episode_file)}")
                continue

            print(f"\n📺 处理: {plan['theme']}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"⏱️ 时长: {plan['segment']['duration']:.1f}秒")
            print(f"🎯 内容: {plan['plot_significance']}")

            if self.create_single_clip(video_file, plan):
                output_name = f"{plan['theme'].replace('：', '_').replace('/', '_').replace('?', '').replace('*', '')}.mp4"
                output_path = os.path.join(self.output_folder, output_name)
                created_clips.append(output_path)

                # 生成说明文件
                self.create_clip_description(output_path, plan)

        print(f"\n✅ 成功创建 {len(created_clips)}/{len(plans)} 个短视频")
        return created_clips

    def create_clip_description(self, clip_path: str, plan: Dict):
        """为每个短视频创建说明文件"""
        try:
            desc_path = clip_path.replace('.mp4', '_说明.txt')

            content = f"""短视频剪辑说明
================================

📺 主题: {plan['theme']}
⏱️ 时间片段: {plan['segment']['start_time']} --> {plan['segment']['end_time']}
📏 片段时长: {plan['segment']['duration']:.1f} 秒
⭐ 重要性评分: {plan['segment']['score']:.1f}/10

🎯 剧情意义:
{plan['plot_significance']}

💡 内容亮点:
"""
            for highlight in plan['content_highlights']:
                content += f"• {highlight}\n"

            content += f"""
📝 关键台词:
"""
            for dialogue in plan['key_dialogues']:
                content += f"{dialogue}\n"

            content += f"""
🔗 与下一集衔接:
{plan['next_episode_connection']}

📄 核心内容预览:
{plan['core_content_preview']}
"""

            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"    📄 生成说明文件: {os.path.basename(desc_path)}")

        except Exception as e:
            print(f"    ⚠ 生成说明文件失败: {e}")

    def create_series_compilation(self, clips: List[str]) -> Optional[str]:
        """创建完整剧集精彩合集"""
        if not clips:
            return None

        print(f"\n🎭 创建完整剧集精彩合集...")

        list_file = "temp_series_list.txt"
        try:
            with open(list_file, 'w', encoding='utf-8') as f:
                for clip in clips:
                    if os.path.exists(clip):
                        abs_path = os.path.abspath(clip).replace('\\', '/')
                        f.write(f"file '{abs_path}'\n")

            output_path = os.path.join(self.output_folder, "完整剧集精彩合集.mp4")

            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, 
                                          timeout=600, encoding='utf-8', errors='ignore')

            if result.returncode == 0:
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"✅ 完整合集: 完整剧集精彩合集.mp4 ({file_size:.1f}MB)")
                return output_path
            else:
                print(f"❌ 创建合集失败: {result.stderr[:100]}")

        except Exception as e:
            print(f"❌ 创建合集失败: {e}")
        finally:
            if os.path.exists(list_file):
                os.remove(list_file)

        return None

    def time_to_seconds(self, time_str: str) -> float:
        """时间转换"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0

def process_all_episodes_smartly():
    """完整智能剪辑流程"""
    print("🚀 启动完整智能化视频剪辑系统")
    print("=" * 60)
    print("📋 剪辑规则:")
    print("• 单集核心聚焦: 每集1个核心剧情点，2-3分钟")
    print("• 主线剧情优先: 四二八案、628旧案、听证会")
    print("• 跨集连贯性: 保持故事线逻辑一致")
    print("• 专业字幕: 标题+内容+亮点展示")
    print("=" * 60)

    # 第一步：智能分析
    print("\n🧠 第一步：智能剧情分析...")
    episodes_plans = analyze_all_episodes_smartly()

    if not episodes_plans:
        print("❌ 没有分析结果")
        return

    # 第二步：创建视频
    print(f"\n🎬 第二步：创建短视频...")
    clipper = SmartVideoClipper()

    # 检查videos目录
    if not os.path.exists(clipper.video_folder):
        print(f"❌ 视频目录不存在: {clipper.video_folder}")
        print("请创建videos目录并放入视频文件")
        return

    video_files = [f for f in os.listdir(clipper.video_folder) 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]

    if not video_files:
        print(f"❌ videos目录中没有视频文件")
        return

    print(f"✅ 找到 {len(video_files)} 个视频文件")

    # 创建短视频
    created_clips = clipper.create_episode_clips(episodes_plans)

    # 第三步：创建完整合集
    if created_clips:
        print(f"\n🎭 第三步：创建完整剧集合集...")
        clipper.create_series_compilation(created_clips)

    # 生成总结报告
    print(f"\n📊 剪辑完成统计：")
    print(f"✅ 分析集数: {len(episodes_plans)} 集")
    print(f"✅ 创建短视频: {len(created_clips)} 个")
    print(f"📁 输出目录: {clipper.output_folder}/")
    print(f"📄 每个短视频都有对应的说明文件")
    print(f"🎬 专业字幕包含: 主题+剧情意义+内容亮点")

    return created_clips

if __name__ == "__main__":
    process_all_episodes_smartly()
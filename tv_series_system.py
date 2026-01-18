#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧AI剪辑系统 - 主程序集成模块
整合所有功能模块，提供完整的电视剧剪辑流程
"""

import os
import re
from typing import List, Dict, Optional
from tv_ai_analyzer import TVAIAnalyzer
from tv_video_clipper import TVVideoClipper
from tv_subtitle_generator import TVSubtitleGenerator


class TVSeriesClipperSystem:
    """电视剧AI剪辑系统 - 主控制器"""

    def __init__(self, ai_config: Dict):
        """初始化系统"""
        self.ai_config = ai_config

        # 目录配置
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.output_folder = "tv_clips"
        self.cache_folder = "tv_cache"
        self.analysis_folder = "tv_analysis"

        # 创建目录
        for folder in [self.output_folder, self.cache_folder, self.analysis_folder]:
            os.makedirs(folder, exist_ok=True)

        # 初始化各个模块
        self.ai_analyzer = TVAIAnalyzer(ai_config, self.cache_folder)
        self.video_clipper = TVVideoClipper(self.output_folder, self.cache_folder)
        self.subtitle_generator = TVSubtitleGenerator(self.output_folder)

        # 跨集连贯性：存储上一集的衔接信息
        self.previous_episode_context = None

        print("📺 电视剧AI剪辑系统已初始化")

    def parse_subtitles(self, srt_path: str) -> Dict:
        """解析字幕文件"""
        print(f"📖 解析字幕: {os.path.basename(srt_path)}")

        # 多编码尝试
        content = None
        for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5']:
            try:
                with open(srt_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                if content.strip():
                    break
            except:
                continue

        if not content:
            return

        # 智能错误修正
        corrections = {
            '防衛': '防卫', '正當': '正当', '証據': '证据', '檢察官': '检察官',
            '發現': '发现', '決定': '决定', '選擇': '选择', '開始': '开始',
            '結束': '结束', '問題': '问题', '機會': '机会', '実現': '实现',
            '対話': '对话', '関係': '关系', '実際': '实际', '変化': '变化'
        }

        for old, new in corrections.items():
            content = content.replace(old, new)

        # 解析字幕
        subtitles = []
        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0]) if lines[0].isdigit() else len(subtitles) + 1
                    time_match = re.search(
                        r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})',
                        lines[1]
                    )
                    if time_match:
                        start_time = time_match.group(1).replace('.', ',')
                        end_time = time_match.group(2).replace('.', ',')
                        text = '\n'.join(lines[2:]).strip()

                        if text:
                            subtitles.append({
                                'index': index,
                                'start_time': start_time,
                                'end_time': end_time,
                                'text': text,
                                'start_seconds': self._time_to_seconds(start_time),
                                'end_seconds': self._time_to_seconds(end_time)
                            })
                except:
                    continue

        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return {
            'filename': os.path.basename(srt_path),
            'total_subtitles': len(subtitles),
            'subtitles': subtitles,
            'total_duration': subtitles[-1]['end_seconds'] if subtitles else 0
        }

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def process_single_episode(self, srt_filename: str) -> bool:
        """
        处理单集电视剧

        Args:
            srt_filename: 字幕文件名

        Returns:
            是否处理成功
        """
        print(f"\n{'='*60}")
        print(f"📺 处理集数: {srt_filename}")
        print(f"{'='*60}")

        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_filename)
        subtitle_data = self.parse_subtitles(srt_path)

        if not subtitle_data or not subtitle_data.get('subtitles'):
            print("❌ 字幕解析失败")
            return False

        # 2. AI分析（支持缓存）
        episode_name = os.path.splitext(srt_filename)[0]
        analysis = self.ai_analyzer.analyze_episode(
            episode_name,
            subtitle_data['subtitles'],
            self.previous_episode_context
        )

        if not analysis:
            print("❌ AI分析失败，直接返回")
            return False

        # 3. 查找对应视频文件
        video_file = self.find_video_file(episode_name)
        if not video_file:
            print("❌ 未找到对应视频文件")
            return False

        print(f"📹 视频文件: {os.path.basename(video_file)}")

        # 4. 创建视频片段（支持断点续传）
        created_clips = self.video_clipper.create_clips_from_analysis(
            episode_name,
            video_file,
            analysis
        )

        if not created_clips:
            print("❌ 视频剪辑失败")
            return False

        # 5. 为每个片段生成旁白字幕和分析报告
        print(f"\n📝 生成旁白字幕和分析报告")
        for i, clip_path in enumerate(created_clips, 1):
            clip_data = analysis['highlight_clips'][i-1]

            # 生成旁白字幕
            self.subtitle_generator.generate_subtitle_for_clip(
                clip_path,
                clip_data,
                episode_name,
                i
            )

            # 生成分析报告
            self.subtitle_generator.generate_analysis_report(
                clip_path,
                clip_data,
                episode_name,
                i
            )

        # 6. 保存跨集连贯信息
        self.previous_episode_context = analysis.get('next_episode_connection')

        print(f"\n✅ 处理完成！生成 {len(created_clips)} 个精彩片段")
        return True

    def find_video_file(self, episode_name: str) -> Optional[str]:
        """查找对应的视频文件"""
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, episode_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 模糊匹配
        if os.path.exists(self.videos_folder):
            for filename in os.listdir(self.videos_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    file_base = os.path.splitext(filename)[0].lower()
                    episode_base = episode_name.lower()
                    # 检查是否包含主要关键词
                    if any(part in file_base for part in episode_base.split('_') if len(part) > 2):
                        return os.path.join(self.videos_folder, filename)

        return None

    def get_all_srt_files(self) -> List[str]:
        """获取所有字幕文件"""
        if not os.path.exists(self.srt_folder):
            return []

        srt_files = [
            f for f in os.listdir(self.srt_folder)
            if f.lower().endswith(('.srt', '.txt')) and not f.startswith('.')
        ]

        # 按文件名排序（保证集数顺序）
        srt_files.sort()
        return srt_files

    def process_all_episodes(self) -> Dict:
        """
        批量处理所有集数

        Returns:
            处理统计信息
        """
        print("\n" + "="*60)
        print("📺 电视剧AI剪辑系统 - 批量处理模式")
        print("="*60)

        # 获取所有字幕文件
        srt_files = self.get_all_srt_files()

        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return {'success': 0, 'total': 0, 'failed': []}

        print(f"📝 找到 {len(srt_files)} 个字幕文件")

        # 处理统计
        success_count = 0
        failed_episodes = []

        # 逐集处理
        for i, srt_file in enumerate(srt_files, 1):
            print(f"\n{'🎬'*20}")
            print(f"进度: {i}/{len(srt_files)}")
            print(f"{'🎬'*20}")

            try:
                if self.process_single_episode(srt_file):
                    success_count += 1
                else:
                    failed_episodes.append(srt_file)
            except Exception as e:
                print(f"❌ 处理异常: {e}")
                failed_episodes.append(srt_file)

        # 返回统计信息
        return {
            'success': success_count,
            'total': len(srt_files),
            'failed': failed_episodes
        }

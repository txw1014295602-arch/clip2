#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
电视剧视频剪辑模块
支持缓存机制、断点续传、确保多次执行结果一致
"""

import os
import re
import json
import hashlib
import subprocess
from typing import Dict, List, Optional


class TVVideoClipper:
    """电视剧视频剪辑器 - 支持缓存和断点续传"""

    def __init__(self, output_folder: str = "tv_clips", cache_folder: str = "tv_cache"):
        """初始化视频剪辑器"""
        self.output_folder = output_folder
        self.cache_folder = cache_folder
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(cache_folder, exist_ok=True)

    def create_clips_from_analysis(
        self,
        episode_name: str,
        video_file: str,
        analysis: Dict
    ) -> List[str]:
        """
        根据AI分析结果创建视频片段

        Args:
            episode_name: 集数名称
            video_file: 视频文件路径
            analysis: AI分析结果

        Returns:
            成功创建的视频文件路径列表
        """
        if not analysis or not analysis.get('highlight_clips'):
            print("❌ 无有效分析结果")
            return []

        clips = analysis['highlight_clips']
        created_files = []

        print(f"\n🎬 开始剪辑 {len(clips)} 个片段")

        for i, clip in enumerate(clips, 1):
            clip_path = self._get_clip_path(episode_name, clip, i)

            # 检查是否已经剪辑过
            if os.path.exists(clip_path):
                print(f"  [{i}/{len(clips)}] ✅ 已存在，跳过: {os.path.basename(clip_path)}")
                created_files.append(clip_path)
                continue

            # 执行剪辑
            print(f"  [{i}/{len(clips)}] 🎬 剪辑中: {clip.get('title', f'片段{i}')}")
            if self._create_single_clip(video_file, clip, clip_path):
                created_files.append(clip_path)
                print(f"  [{i}/{len(clips)}] ✅ 成功")
            else:
                print(f"  [{i}/{len(clips)}] ❌ 失败")

        return created_files

    def _get_clip_path(self, episode_name: str, clip: Dict, index: int) -> str:
        """生成剪辑文件路径（确保一致性）"""
        # 使用剪辑内容的哈希值确保相同内容得到相同文件名
        clip_hash = hashlib.md5(
            json.dumps({
                'start': clip.get('start_time'),
                'end': clip.get('end_time'),
                'title': clip.get('title')
            }, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest()[:8]

        safe_episode = self._safe_filename(episode_name)
        safe_title = self._safe_filename(clip.get('title', f'片段{index}'))

        filename = f"{safe_episode}_片段{index:02d}_{safe_title}_{clip_hash}.mp4"
        return os.path.join(self.output_folder, filename)

    def _create_single_clip(self, video_file: str, clip: Dict, output_path: str) -> bool:
        """创建单个视频片段"""
        try:
            start_time = clip.get('start_time')
            end_time = clip.get('end_time')

            if not start_time or not end_time:
                print("    ⚠️ 缺少时间信息")
                return False

            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds

            if duration <= 0:
                print("    ⚠️ 时长无效")
                return False

            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path,
                '-y'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"    📦 大小: {size_mb:.1f}MB")
                return True
            else:
                print(f"    ⚠️ FFmpeg错误")
                return False

        except Exception as e:
            print(f"    ❌ 异常: {e}")
            return False

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def _safe_filename(self, name: str) -> str:
        """安全文件名"""
        return re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', name)[:50]

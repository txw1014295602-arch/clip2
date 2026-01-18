#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频提取模块
从视频文件中提取音频轨道
"""

import os
import subprocess
import hashlib
from typing import Optional, Dict
from config_manager import ConfigManager


class AudioExtractor:
    """音频提取器 - 从视频提取音频"""

    def __init__(self, config_manager: ConfigManager):
        """初始化音频提取器"""
        self.config_manager = config_manager
        paths = config_manager.get_paths()
        self.audio_cache_folder = paths.get('audio_cache', 'audio_cache')

        # 创建缓存目录
        os.makedirs(self.audio_cache_folder, exist_ok=True)

    def extract_audio(self, video_path: str, output_format: str = 'mp3') -> Optional[str]:
        """
        从视频提取音频

        Args:
            video_path: 视频文件路径
            output_format: 输出音频格式（mp3, wav, m4a）

        Returns:
            音频文件路径，失败返回None
        """
        if not os.path.exists(video_path):
            print(f"❌ 视频文件不存在: {video_path}")
            return None

        # 检查缓存
        cached_audio = self.check_audio_cache(video_path, output_format)
        if cached_audio:
            print(f"💾 使用缓存的音频: {os.path.basename(cached_audio)}")
            return cached_audio

        # 生成音频文件路径
        audio_path = self._get_audio_cache_path(video_path, output_format)

        print(f"🎵 提取音频: {os.path.basename(video_path)}")

        # 执行FFmpeg提取
        success = self._extract_with_ffmpeg(video_path, audio_path, output_format)

        if success and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / (1024 * 1024)
            print(f"✅ 音频提取成功: {file_size:.1f}MB")
            return audio_path
        else:
            print(f"❌ 音频提取失败")
            return None

    def _extract_with_ffmpeg(
        self,
        video_path: str,
        audio_path: str,
        output_format: str
    ) -> bool:
        """使用FFmpeg提取音频"""
        try:
            processing_config = self.config_manager.get_processing_config()
            audio_quality = processing_config.get('audio_quality', '192k')

            # 根据格式选择编码器
            codec_map = {
                'mp3': 'libmp3lame',
                'wav': 'pcm_s16le',
                'm4a': 'aac'
            }

            codec = codec_map.get(output_format, 'libmp3lame')

            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # 不处理视频
                '-acodec', codec,
                '-ar', '16000',  # 采样率（Whisper推荐16kHz）
                '-ac', '1',  # 单声道
                '-b:a', audio_quality,
                audio_path,
                '-y'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            return result.returncode == 0

        except Exception as e:
            print(f"⚠️ FFmpeg执行失败: {e}")
            return False

    def check_audio_cache(self, video_path: str, output_format: str = 'mp3') -> Optional[str]:
        """检查音频缓存是否存在"""
        audio_path = self._get_audio_cache_path(video_path, output_format)
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1024:
            return audio_path
        return None

    def _get_audio_cache_path(self, video_path: str, output_format: str) -> str:
        """生成音频缓存文件路径"""
        # 使用视频文件内容哈希生成唯一标识
        video_hash = self._get_file_hash(video_path)
        video_basename = os.path.splitext(os.path.basename(video_path))[0]

        # 安全文件名
        safe_name = self._safe_filename(video_basename)
        audio_filename = f"{safe_name}_{video_hash}.{output_format}"

        return os.path.join(self.audio_cache_folder, audio_filename)

    def _get_file_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """计算文件哈希值（仅读取前1MB以提高速度）"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # 只读取前1MB用于哈希计算
                data = f.read(1024 * 1024)
                hasher.update(data)
            return hasher.hexdigest()[:12]
        except Exception as e:
            # 如果读取失败，使用文件名和大小作为哈希
            file_stat = os.stat(file_path)
            fallback = f"{os.path.basename(file_path)}_{file_stat.st_size}"
            return hashlib.md5(fallback.encode()).hexdigest()[:12]

    def _safe_filename(self, name: str) -> str:
        """生成安全的文件名"""
        import re
        return re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', name)[:50]

    def get_audio_info(self, audio_path: str) -> Optional[Dict]:
        """获取音频信息"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                audio_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)

                audio_stream = None
                for stream in info.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break

                if audio_stream:
                    duration = float(info.get('format', {}).get('duration', 0))
                    return {
                        'duration': duration,
                        'sample_rate': audio_stream.get('sample_rate'),
                        'channels': audio_stream.get('channels'),
                        'codec': audio_stream.get('codec_name'),
                        'bitrate': audio_stream.get('bit_rate')
                    }

            return None

        except Exception as e:
            print(f"⚠️ 获取音频信息失败: {e}")
            return None

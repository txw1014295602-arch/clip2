#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音转文字模块
使用AI API将音频转换为文字字幕
"""

import os
import json
import hashlib
from typing import Optional, Dict, List
from config_manager import ConfigManager
from multi_module_api_helper import MultiModuleAPIHelper


class SpeechToText:
    """语音转文字 - 使用AI API进行语音识别"""

    def __init__(self, config_manager: ConfigManager, api_helper: MultiModuleAPIHelper):
        """初始化语音转文字模块"""
        self.config_manager = config_manager
        self.api_helper = api_helper

        paths = config_manager.get_paths()
        self.srt_folder = paths.get('srt_folder', 'srt')
        self.cache_folder = paths.get('analysis_cache', 'cache')

        # 创建目录
        os.makedirs(self.srt_folder, exist_ok=True)
        os.makedirs(self.cache_folder, exist_ok=True)

    def transcribe_audio(self, audio_path: str, video_name: str = None) -> Optional[str]:
        """
        转录音频为文字并生成SRT字幕

        Args:
            audio_path: 音频文件路径
            video_name: 视频名称（用于生成字幕文件名）

        Returns:
            SRT字幕文件路径，失败返回None
        """
        if not os.path.exists(audio_path):
            print(f"❌ 音频文件不存在: {audio_path}")
            return None

        # 检查缓存
        cached_srt = self.check_transcription_cache(audio_path)
        if cached_srt:
            print(f"💾 使用缓存的字幕: {os.path.basename(cached_srt)}")
            return cached_srt

        print(f"🎙️ 开始语音识别: {os.path.basename(audio_path)}")

        # 调用API进行转录
        transcription = self._call_transcription_api(audio_path)

        if not transcription:
            print(f"❌ 语音识别失败")
            return None

        # 生成SRT文件
        srt_path = self._generate_srt_file(transcription, audio_path, video_name)

        if srt_path:
            print(f"✅ 字幕生成成功: {os.path.basename(srt_path)}")
            # 保存缓存
            self._save_transcription_cache(audio_path, transcription, srt_path)
            return srt_path
        else:
            print(f"❌ 字幕生成失败")
            return None

    def _call_transcription_api(self, audio_path: str) -> Optional[Dict]:
        """调用API进行语音识别"""
        module_config = self.config_manager.get_module_config('speech_to_text')

        if not module_config or not module_config.get('enabled'):
            print(f"❌ 语音转文字模块未启用")
            return None

        provider = module_config.get('provider', '').lower()

        try:
            if provider == 'openai':
                return self._transcribe_with_openai(audio_path, module_config)
            elif provider == 'gemini':
                return self._transcribe_with_gemini(audio_path, module_config)
            else:
                print(f"❌ 不支持的语音识别提供商: {provider}")
                return None
        except Exception as e:
            print(f"❌ 语音识别API调用失败: {e}")
            return None

    def _transcribe_with_openai(self, audio_path: str, config: Dict) -> Optional[Dict]:
        """使用OpenAI Whisper API转录"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=config['api_key'],
                base_url=config.get('base_url', 'https://api.openai.com/v1')
            )

            with open(audio_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=config.get('model', 'whisper-1'),
                    file=audio_file,
                    response_format='verbose_json',
                    language=config.get('language', 'zh')
                )

            # 解析响应
            return self._parse_whisper_response(transcript)

        except Exception as e:
            print(f"⚠️ OpenAI Whisper API调用失败: {e}")
            return None

    def _transcribe_with_gemini(self, audio_path: str, config: Dict) -> Optional[Dict]:
        """使用Gemini API转录（如果支持）"""
        print(f"⚠️ Gemini语音识别功能暂未实现")
        return None

    def _parse_whisper_response(self, transcript) -> Dict:
        """解析Whisper API响应"""
        segments = []

        if hasattr(transcript, 'segments'):
            for seg in transcript.segments:
                segments.append({
                    'start': seg.get('start', 0),
                    'end': seg.get('end', 0),
                    'text': seg.get('text', '').strip()
                })
        else:
            # 如果没有分段信息，创建单个分段
            segments.append({
                'start': 0,
                'end': 0,
                'text': transcript.text if hasattr(transcript, 'text') else str(transcript)
            })

        return {
            'text': transcript.text if hasattr(transcript, 'text') else '',
            'segments': segments
        }

    def _generate_srt_file(
        self,
        transcription: Dict,
        audio_path: str,
        video_name: str = None
    ) -> Optional[str]:
        """生成SRT字幕文件"""
        try:
            segments = transcription.get('segments', [])

            if not segments:
                print(f"⚠️ 没有可用的字幕分段")
                return None

            # 生成SRT文件路径
            if video_name:
                srt_filename = f"{video_name}.srt"
            else:
                audio_basename = os.path.splitext(os.path.basename(audio_path))[0]
                srt_filename = f"{audio_basename}.srt"

            srt_path = os.path.join(self.srt_folder, srt_filename)

            # 生成SRT内容
            srt_content = self._build_srt_content(segments)

            # 保存文件
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)

            return srt_path

        except Exception as e:
            print(f"⚠️ SRT文件生成失败: {e}")
            return None

    def _build_srt_content(self, segments: List[Dict]) -> str:
        """构建SRT格式内容"""
        srt_lines = []

        for i, segment in enumerate(segments, 1):
            start_time = self._format_timestamp(segment['start'])
            end_time = self._format_timestamp(segment['end'])
            text = segment['text'].strip()

            if text:
                srt_lines.append(f"{i}")
                srt_lines.append(f"{start_time} --> {end_time}")
                srt_lines.append(text)
                srt_lines.append("")

        return '\n'.join(srt_lines)

    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳为SRT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    def check_transcription_cache(self, audio_path: str) -> Optional[str]:
        """检查转录缓存"""
        cache_path = self._get_cache_path(audio_path)

        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    srt_path = cache_data.get('srt_path')

                    if srt_path and os.path.exists(srt_path):
                        return srt_path
            except:
                pass

        return None

    def _save_transcription_cache(
        self,
        audio_path: str,
        transcription: Dict,
        srt_path: str
    ):
        """保存转录缓存"""
        try:
            cache_path = self._get_cache_path(audio_path)
            cache_data = {
                'audio_path': audio_path,
                'srt_path': srt_path,
                'transcription': transcription,
                'timestamp': os.path.getmtime(audio_path)
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")

    def _get_cache_path(self, audio_path: str) -> str:
        """获取缓存文件路径"""
        audio_hash = self._get_file_hash(audio_path)
        cache_filename = f"transcription_{audio_hash}.json"
        return os.path.join(self.cache_folder, cache_filename)

    def _get_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                data = f.read(1024 * 1024)  # 读取前1MB
                hasher.update(data)
            return hasher.hexdigest()[:12]
        except:
            file_stat = os.stat(file_path)
            fallback = f"{os.path.basename(file_path)}_{file_stat.st_size}"
            return hashlib.md5(fallback.encode()).hexdigest()[:12]

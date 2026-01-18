#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整视频处理器
整合音频提取、语音转文字、AI分析、视频剪辑的完整流程
"""

import os
from typing import Optional, Dict, List
from config_manager import ConfigManager
from multi_module_api_helper import MultiModuleAPIHelper
from audio_extractor import AudioExtractor
from speech_to_text import SpeechToText
from tv_ai_analyzer import TVAIAnalyzer
from tv_video_clipper import TVVideoClipper
from tv_subtitle_generator import TVSubtitleGenerator


class CompleteVideoProcessor:
    """完整视频处理器 - 从原始视频到精彩片段的完整流程"""

    def __init__(self, config_manager: ConfigManager):
        """初始化完整视频处理器"""
        self.config_manager = config_manager

        # 初始化API助手
        self.api_helper = MultiModuleAPIHelper(config_manager)

        # 初始化各个模块
        self.audio_extractor = AudioExtractor(config_manager)
        self.speech_to_text = SpeechToText(config_manager, self.api_helper)

        # 获取AI分析器配置
        ai_config = config_manager.get_module_config('content_analysis')
        if not ai_config:
            ai_config = {'enabled': False}

        self.ai_analyzer = TVAIAnalyzer(ai_config, config_manager.get_paths().get('analysis_cache', 'cache'))
        self.video_clipper = TVVideoClipper(config_manager.get_paths().get('output_clips', 'clips'))
        self.subtitle_generator = TVSubtitleGenerator(config_manager.get_paths().get('output_clips', 'clips'))

        # 获取路径配置
        paths = config_manager.get_paths()
        self.input_videos_folder = paths.get('input_videos', 'videos')
        self.srt_folder = paths.get('srt_folder', 'srt')

        print("✅ 完整视频处理器初始化成功")

    def process_video_from_scratch(self, video_path: str) -> Dict:
        """
        从原始视频完整处理到精彩片段

        Args:
            video_path: 视频文件路径

        Returns:
            处理结果字典
        """
        print(f"\n{'='*60}")
        print(f"🎬 开始完整视频处理")
        print(f"📹 视频: {os.path.basename(video_path)}")
        print(f"{'='*60}")

        result = {
            'success': False,
            'video_path': video_path,
            'audio_path': None,
            'srt_path': None,
            'clips': [],
            'error': None
        }

        try:
            # 步骤1: 提取音频
            print(f"\n📍 步骤 1/5: 提取音频")
            audio_path = self.audio_extractor.extract_audio(video_path)
            if not audio_path:
                result['error'] = "音频提取失败"
                return result
            result['audio_path'] = audio_path

            # 步骤2: 语音转文字
            print(f"\n📍 步骤 2/5: 语音转文字")
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            srt_path = self.speech_to_text.transcribe_audio(audio_path, video_name)
            if not srt_path:
                result['error'] = "语音识别失败"
                return result
            result['srt_path'] = srt_path

            # 步骤3-5: 使用现有字幕继续处理
            print(f"\n📍 步骤 3-5: AI分析和视频剪辑")
            clip_result = self.process_with_existing_srt(video_path, srt_path)

            result['clips'] = clip_result.get('clips', [])
            result['success'] = clip_result.get('success', False)
            result['error'] = clip_result.get('error')

            return result

        except Exception as e:
            result['error'] = f"处理异常: {e}"
            print(f"❌ 处理异常: {e}")
            return result

    def process_with_existing_srt(self, video_path: str, srt_path: str) -> Dict:
        """
        使用现有字幕处理视频（兼容旧模式）

        Args:
            video_path: 视频文件路径
            srt_path: 字幕文件路径

        Returns:
            处理结果字典
        """
        result = {
            'success': False,
            'video_path': video_path,
            'srt_path': srt_path,
            'clips': [],
            'error': None
        }

        try:
            # 步骤3: 解析字幕
            print(f"\n📍 步骤 3/5: 解析字幕")
            from tv_series_system import TVSeriesSystem
            tv_system = TVSeriesSystem(self.config_manager)
            subtitle_data = tv_system.parse_subtitles(srt_path)

            if not subtitle_data or not subtitle_data.get('subtitles'):
                result['error'] = "字幕解析失败"
                return result

            # 步骤4: AI分析
            print(f"\n📍 步骤 4/5: AI分析精彩片段")
            episode_name = os.path.splitext(os.path.basename(video_path))[0]
            analysis = self.ai_analyzer.analyze_episode(
                episode_name,
                subtitle_data['subtitles'],
                None
            )

            if not analysis:
                result['error'] = "AI分析失败"
                return result

            # 步骤5: 视频剪辑
            print(f"\n📍 步骤 5/5: 视频剪辑")
            created_clips = self.video_clipper.create_clips_from_analysis(
                episode_name,
                video_path,
                analysis
            )

            if not created_clips:
                result['error'] = "视频剪辑失败"
                return result

            result['clips'] = created_clips
            result['success'] = True

            print(f"\n✅ 处理完成！生成 {len(created_clips)} 个精彩片段")
            return result

        except Exception as e:
            result['error'] = f"处理异常: {e}"
            print(f"❌ 处理异常: {e}")
            return result

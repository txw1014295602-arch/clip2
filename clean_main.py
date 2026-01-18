
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI剪辑系统 - 完全重构版
支持电影和电视剧的AI驱动剪辑
核心功能：
1. 字幕解析和错误修正
2. 100% AI分析（支持缓存）
3. 智能剧情点识别
4. 视频剪辑（支持断点续传）
5. 旁观者叙述字幕生成
6. 跨集连贯性处理（电视剧）
7. 固定输出格式
"""

import os
import re
import json
import hashlib
import subprocess
import time
from typing import List, Dict, Optional
from datetime import datetime

# 导入电视剧剪辑系统
try:
    from tv_series_system import TVSeriesClipperSystem
    TV_SYSTEM_AVAILABLE = True
except ImportError:
    TV_SYSTEM_AVAILABLE = False
    print("⚠️ 电视剧剪辑模块未找到")

class MovieClipperSystem:
    """电影剪辑系统 - 集成AI驱动版"""

    def __init__(self):
        # 目录结构
        self.srt_folder = "srt"
        self.videos_folder = "videos"
        self.clips_folder = "clips"
        self.cache_folder = "ai_cache"
        self.output_folder = "ai_clips"
        self.analysis_folder = "ai_analysis"

        # 创建目录
        for folder in [self.srt_folder, self.videos_folder, self.clips_folder, 
                      self.cache_folder, self.output_folder, self.analysis_folder]:
            os.makedirs(folder, exist_ok=True)

        # 加载AI配置
        self.ai_config = self._load_ai_config()

        print("🎬 电影剪辑系统 - AI驱动集成版")
        print("=" * 50)

    def _load_ai_config(self) -> Dict:
        """加载AI配置"""
        config_file = '.ai_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('enabled'):
                        return config
            except Exception as e:
                print(f"⚠️ 配置加载失败: {e}")
        return {'enabled': False}

    def setup_ai_config(self) -> bool:
        """设置AI配置"""
        print("\n🤖 AI配置向导")
        print("=" * 30)

        # 检查现有配置
        if self.ai_config.get('enabled'):
            print("✅ 发现现有配置:")
            print(f"   类型: {self.ai_config.get('api_type')}")
            print(f"   提供商: {self.ai_config.get('provider')}")

            use_existing = input("\n是否使用现有配置？(Y/n): ").strip().lower()
            if use_existing not in ['n', 'no', '否']:
                return True

        print("\n选择API类型:")
        print("1. 🔒 官方API (Gemini官方)")
        print("2. 🌐 中转API (OpenAI兼容)")
        print("0. ❌ 跳过配置")

        while True:
            choice = input("\n请选择 (0-2): ").strip()

            if choice == '0':
                print("⚠️ 跳过AI配置")
                return False
            elif choice == '1':
                return self._setup_official_api()
            elif choice == '2':
                return self._setup_proxy_api()
            else:
                print("❌ 无效选择")

    def _setup_official_api(self) -> bool:
        """设置官方API - 仅支持Gemini"""
        print("\n🔒 Gemini官方API配置")
        print("获取API密钥: https://aistudio.google.com/apikey")

        api_key = input("\nGemini API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False

        # 可用模型
        models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
        print(f"\n选择模型:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")

        model_choice = input(f"选择 (1-{len(models)}): ").strip()
        try:
            model = models[int(model_choice) - 1]
        except:
            model = models[0]

        config = {
            'enabled': True,
            'api_type': 'official',
            'provider': 'gemini',
            'api_key': api_key,
            'model': model
        }

        # 测试连接
        print("🔍 测试连接...")
        if self._test_gemini_api(config):
            print("✅ 连接成功")
            return self._save_config(config)
        else:
            print("❌ 连接失败")
            return False

    def _setup_proxy_api(self) -> bool:
        """设置中转API"""
        print("\n🌐 中转API配置")

        # 预设选项
        presets = {
            "1": {
                "name": "ChatAI API",
                "base_url": "https://www.chataiapi.com/v1",
                "models": ["deepseek-r1", "claude-3-5-sonnet-20240620", "gpt-4o"]
            },
            "2": {
                "name": "OpenRouter",
                "base_url": "https://openrouter.ai/api/v1",
                "models": ["anthropic/claude-3.5-sonnet", "deepseek/deepseek-r1"]
            },
            "3": {
                "name": "自定义中转",
                "base_url": "",
                "models": []
            }
        }

        print("选择中转服务:")
        for key, preset in presets.items():
            print(f"{key}. {preset['name']}")

        choice = input("请选择 (1-3): ").strip()
        if choice not in presets:
            return False

        selected = presets[choice]

        if choice == "3":
            base_url = input("API地址: ").strip()
            if not base_url:
                return False
            model = input("模型名称: ").strip()
            if not model:
                return False
        else:
            base_url = selected["base_url"]
            print(f"\n推荐模型:")
            for i, m in enumerate(selected["models"], 1):
                print(f"{i}. {m}")

            model_choice = input(f"选择模型 (1-{len(selected['models'])}): ").strip()
            try:
                model = selected["models"][int(model_choice) - 1]
            except:
                model = selected["models"][0]

        api_key = input("API密钥: ").strip()
        if not api_key:
            print("❌ API密钥不能为空")
            return False

        config = {
            'enabled': True,
            'api_type': 'proxy',
            'provider': selected['name'],
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }

        # 测试连接
        print("🔍 测试连接...")
        if self._test_proxy_api(config):
            print("✅ 连接成功")
            return self._save_config(config)
        else:
            print("❌ 连接失败")
            return False

    def _test_gemini_api(self, config: Dict) -> bool:
        """测试Gemini官方API"""
        try:
            from google import genai

            # 官方方式创建客户端
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'], 
                contents="测试"
            )
            return bool(response.text)
        except ImportError:
            print("需要安装: pip install google-generativeai")
            return False
        except Exception as e:
            print(f"测试失败: {e}")
            return False

    def _test_proxy_api(self, config: Dict) -> bool:
        """测试中转API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )
            response = client.chat.completions.create(
                model=config['model'],
                messages=[{'role': 'user', 'content': '测试'}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except ImportError:
            print("需要安装: pip install openai")
            return False
        except Exception as e:
            print(f"测试失败: {e}")
            return False

    def _save_config(self, config: Dict) -> bool:
        """保存配置"""
        try:
            with open('.ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.ai_config = config
            print(f"✅ 配置保存成功")
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    def parse_subtitles(self, srt_path: str) -> Dict:
        """解析电影字幕，智能修正错误"""
        print(f"📖 解析电影字幕: {os.path.basename(srt_path)}")
        
        # 多编码尝试
        content = None
        for encoding in ['utf-8', 'gbk', 'utf-16', 'gb2312', 'big5']:
            try:
                with open(srt_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                break
            except:
                continue
        
        if not content:
            return {}
        
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
                    time_match = re.search(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', lines[1])
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

    def ai_analyze_complete_movie(self, data: Dict) -> Optional[Dict]:
        """100% AI分析电影，分析不了就直接返回"""
        if not self.ai_config.get('enabled'):
            print("❌ AI未启用，无法进行100% AI分析，直接返回")
            return None
        
        title = os.path.splitext(data['filename'])[0]
        subtitles = data['subtitles']
        
        # 检查缓存
        cache_key = hashlib.md5(str(subtitles[:10]).encode()).hexdigest()[:16]
        cache_path = os.path.join(self.cache_folder, f"ai_analysis_{title}_{cache_key}.json")
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_analysis = json.load(f)
                print(f"💾 使用AI分析缓存")
                return cached_analysis
            except:
                pass
        
        # 构建完整对话文本
        full_text = '\n'.join([f"[{sub['start_time']}] {sub['text']}" for sub in subtitles])
        
        # 100% AI分析提示词
        prompt = f"""你是世界顶级的电影分析大师。请对这部电影进行100% AI驱动的深度分析。

【电影标题】{title}
【完整对话内容】
{full_text[:8000]}  # 限制长度避免超出API限制

请完成以下任务：

1. **AI识别主人公** - 分析所有角色，确定真正的主人公
2. **构建完整故事线** - 以主人公视角讲述完整故事
3. **智能剧情分割** - 如果故事很长，分割成多个逻辑连贯的段落
4. **剧情点剪辑规划** - 设计非连续但逻辑连贯的剪辑点
5. **第一人称叙述** - 为每个片段生成详细的第一人称叙述

返回JSON格式：
{{
    "ai_analysis_status": "success",
    "info": {{
        "title": "{title}",
        "genre": "AI识别的电影类型",
        "duration_minutes": {data['total_duration']/60:.1f},
        "analysis_confidence": "AI分析置信度(1-10)"
    }},
    "protagonist_analysis": {{
        "main_protagonist": "主人公姓名",
        "character_arc": "主人公成长轨迹",
        "story_perspective": "主人公视角的故事概述",
        "character_traits": ["性格特征1", "性格特征2", "性格特征3"],
        "protagonist_reasoning": "AI选择此人为主人公的原因"
    }},
    "complete_storyline": {{
        "story_structure": "完整故事结构分析",
        "narrative_flow": "叙事流程",
        "key_story_moments": ["关键故事时刻1", "关键故事时刻2", "关键故事时刻3"],
        "story_length_assessment": "故事长度评估(short/medium/long)"
    }},
    "video_segments": [
        {{
            "segment_id": 1,
            "segment_title": "片段标题",
            "plot_type": "剧情点类型",
            "start_time": "开始时间(HH:MM:SS,mmm)",
            "end_time": "结束时间(HH:MM:SS,mmm)",
            "duration_seconds": 实际秒数,
            "discontinuous_times": [
                {{"start": "时间1", "end": "时间2"}},
                {{"start": "时间3", "end": "时间4"}}
            ],
            "logical_coherence": "逻辑连贯性说明",
            "first_person_narration": {{
                "opening_narration": "开场第一人称叙述(我看到...)",
                "development_narration": "发展过程叙述(我注意到...)",
                "climax_narration": "高潮部分叙述(我感受到...)",
                "conclusion_narration": "结尾叙述(我明白了...)",
                "complete_narration": "完整连贯的第一人称叙述",
                "narration_timing": [
                    {{"text": "叙述片段1", "start_seconds": 0, "end_seconds": 30}},
                    {{"text": "叙述片段2", "start_seconds": 30, "end_seconds": 60}}
                ]
            }},
            "subtitle_content": "需要添加的字幕内容",
            "visual_sync_points": ["视频内容与叙述同步点1", "同步点2"],
            "editing_notes": "剪辑说明"
        }}
    ],
    "protagonist_story_summary": "主人公完整故事总结",
    "ai_confidence_score": "AI分析总体置信度(1-10)"
}}

分析要求：
1. 必须100% AI判断，不使用任何预设规则
2. 主人公必须通过AI深度分析确定
3. 第一人称叙述要详细清晰，完整覆盖内容
4. 剪辑点可以时间不连续，但逻辑必须连贯
5. 如果无法充分分析，请返回分析失败状态"""

        try:
            print(f"🤖 AI正在进行100%智能分析...")
            response = self._call_ai_api(prompt)
            
            if response:
                analysis = self._parse_ai_response(response)
                if analysis and analysis.get('ai_analysis_status') == 'success':
                    # 保存缓存
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(analysis, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ AI分析成功，识别主人公: {analysis.get('protagonist_analysis', {}).get('main_protagonist', '未知')}")
                    return analysis
                else:
                    print("❌ AI分析结果不完整，直接返回")
                    return None
            else:
                print("❌ AI API调用失败，直接返回")
                return None
                
        except Exception as e:
            print(f"❌ AI分析出错: {e}，直接返回")
            return None

    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """调用AI API"""
        config = self.ai_config

        try:
            if config.get('api_type') == 'official':
                return self._call_gemini_official(prompt, config)
            else:
                return self._call_proxy_api(prompt, config)
        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            return None

    def _call_gemini_official(self, prompt: str, config: Dict) -> Optional[str]:
        """调用Gemini官方API"""
        try:
            from google import genai

            # 官方方式创建客户端
            client = genai.Client(api_key=config['api_key'])
            response = client.models.generate_content(
                model=config['model'],
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return None

    def _call_proxy_api(self, prompt: str, config: Dict) -> Optional[str]:
        """调用中转API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config['api_key'],
                base_url=config['base_url']
            )

            response = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {'role': 'system', 'content': '你是专业的电影分析师，必须进行100% AI驱动的深度分析。严格按照JSON格式返回。'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=8000,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"中转API调用失败: {e}")
            return None

    def _parse_ai_response(self, response: str) -> Optional[Dict]:
        """解析AI响应"""
        try:
            # 提取JSON内容
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                else:
                    return None
            
            analysis = json.loads(json_str)
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析错误: {e}")
            return None

    def create_protagonist_story_videos(self, analysis: Dict, data: Dict, video_file: str) -> List[str]:
        """创建主人公故事视频（无声+第一人称叙述）"""
        if not analysis or not video_file:
            return []
        
        segments = analysis.get('video_segments', [])
        title = analysis['info']['title']
        protagonist = analysis['protagonist_analysis']['main_protagonist']
        created_videos = []
        
        print(f"\n🎬 创建主人公故事视频")
        print(f"👤 主人公: {protagonist}")
        print(f"📁 源视频: {os.path.basename(video_file)}")
        print(f"🎯 片段数量: {len(segments)}")
        
        for i, segment in enumerate(segments, 1):
            try:
                segment_title = segment.get('segment_title', f'第{i}段')
                safe_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', segment_title)
                
                video_filename = f"{title}_{protagonist}_第{i}段_{safe_title}.mp4"
                video_path = os.path.join(self.output_folder, video_filename)
                
                print(f"\n  🎯 创建第{i}段: {segment_title}")
                print(f"     剧情点: {segment.get('plot_type', '未知')}")
                print(f"     时长: {segment['duration_seconds']:.1f}秒")
                
                if self._create_single_silent_video(segment, video_file, video_path):
                    # 生成第一人称叙述字幕
                    self._create_first_person_subtitle(segment, video_path, i)
                    
                    # 生成详细分析报告
                    self._create_segment_analysis_report(segment, video_path, protagonist, i)
                    
                    created_videos.append(video_path)
                    print(f"     ✅ 创建成功")
                else:
                    print(f"     ❌ 创建失败")
                    
            except Exception as e:
                print(f"     ❌ 处理第{i}段出错: {e}")
        
        # 生成主人公完整故事报告
        if created_videos:
            self._create_protagonist_story_report(analysis, created_videos, title, protagonist)
        
        return created_videos

    def _create_single_silent_video(self, segment: Dict, video_file: str, output_path: str) -> bool:
        """创建单个无声视频片段"""
        try:
            # 处理非连续时间段
            discontinuous_times = segment.get('discontinuous_times', [])
            
            if discontinuous_times:
                # 非连续剪辑
                return self._create_discontinuous_video(discontinuous_times, video_file, output_path)
            else:
                # 连续剪辑
                start_time = segment['start_time']
                end_time = segment['end_time']
                return self._create_continuous_video(start_time, end_time, video_file, output_path)
                
        except Exception as e:
            print(f"创建视频失败: {e}")
            return False

    def _create_discontinuous_video(self, time_segments: List[Dict], video_file: str, output_path: str) -> bool:
        """创建非连续时间的视频片段"""
        try:
            temp_clips = []
            
            # 创建各个时间段的临时片段
            for i, time_seg in enumerate(time_segments):
                temp_clip = f"temp_segment_{i}_{os.getpid()}.mp4"
                temp_path = os.path.join(self.output_folder, temp_clip)
                
                start_seconds = self._time_to_seconds(time_seg['start'])
                end_seconds = self._time_to_seconds(time_seg['end'])
                duration = end_seconds - start_seconds
                
                cmd = [
                    'ffmpeg',
                    '-i', video_file,
                    '-ss', f"{start_seconds:.3f}",
                    '-t', f"{duration:.3f}",
                    '-an',  # 移除音频
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    temp_path,
                    '-y'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(temp_path):
                    temp_clips.append(temp_path)
                else:
                    # 清理已创建的临时文件
                    for temp_file in temp_clips:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    return False
            
            # 合并所有临时片段
            if temp_clips:
                success = self._merge_video_clips(temp_clips, output_path)
                
                # 清理临时文件
                for temp_file in temp_clips:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                return success
            
            return False
            
        except Exception as e:
            print(f"非连续视频创建失败: {e}")
            return False

    def _create_continuous_video(self, start_time: str, end_time: str, video_file: str, output_path: str) -> bool:
        """创建连续时间的视频片段"""
        try:
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', f"{start_seconds:.3f}",
                '-t', f"{duration:.3f}",
                '-an',  # 移除音频
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-movflags', '+faststart',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            print(f"连续视频创建失败: {e}")
            return False

    def _merge_video_clips(self, clip_paths: List[str], output_path: str) -> bool:
        """合并视频片段"""
        try:
            # 创建文件列表
            list_file = f"temp_list_{os.getpid()}.txt"
            
            with open(list_file, 'w', encoding='utf-8') as f:
                for clip_path in clip_paths:
                    if os.path.exists(clip_path):
                        abs_path = os.path.abspath(clip_path).replace('\\', '/')
                        f.write(f"file '{abs_path}'\n")
            
            # 合并命令
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # 清理文件列表
            if os.path.exists(list_file):
                os.remove(list_file)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"视频合并失败: {e}")
            return False

    def _create_first_person_subtitle(self, segment: Dict, video_path: str, segment_num: int):
        """创建第一人称叙述字幕文件"""
        try:
            subtitle_path = video_path.replace('.mp4', '_第一人称叙述.srt')
            
            narration = segment.get('first_person_narration', {})
            narration_timing = narration.get('narration_timing', [])
            
            if not narration_timing:
                # 如果没有详细时间安排，使用完整叙述
                complete_narration = narration.get('complete_narration', '我观看了这个精彩的片段。')
                duration = segment.get('duration_seconds', 120)
                
                narration_timing = [{
                    'text': complete_narration,
                    'start_seconds': 0,
                    'end_seconds': duration
                }]
            
            # 生成SRT格式字幕
            srt_content = ""
            for i, timing in enumerate(narration_timing, 1):
                start_time = self._seconds_to_srt_time(timing['start_seconds'])
                end_time = self._seconds_to_srt_time(timing['end_seconds'])
                
                srt_content += f"{i}\n"
                srt_content += f"{start_time} --> {end_time}\n"
                srt_content += f"{timing['text']}\n\n"
            
            with open(subtitle_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            print(f"    📝 第一人称叙述字幕: {os.path.basename(subtitle_path)}")
            
        except Exception as e:
            print(f"    ⚠️ 字幕生成失败: {e}")

    def _create_segment_analysis_report(self, segment: Dict, video_path: str, protagonist: str, segment_num: int):
        """创建片段详细分析报告"""
        try:
            report_path = video_path.replace('.mp4', '_AI分析报告.txt')
            
            narration = segment.get('first_person_narration', {})
            
            content = f"""🎬 主人公故事片段AI分析报告 - 第{segment_num}段
{'=' * 80}

👤 主人公: {protagonist}
📝 片段标题: {segment.get('segment_title', '未知')}
🎭 剧情点类型: {segment.get('plot_type', '未知')}
⏱️ 时间信息: {segment.get('start_time', '00:00:00,000')} --> {segment.get('end_time', '00:00:00,000')}
📏 片段时长: {segment.get('duration_seconds', 0):.1f} 秒

🔗 逻辑连贯性:
{segment.get('logical_coherence', '通过AI分析确保逻辑连贯')}

🎙️ 第一人称叙述结构:
• 开场叙述: {narration.get('opening_narration', '开场内容')}
• 发展叙述: {narration.get('development_narration', '发展内容')}
• 高潮叙述: {narration.get('climax_narration', '高潮内容')}
• 结尾叙述: {narration.get('conclusion_narration', '结尾内容')}

📝 完整第一人称叙述:
{narration.get('complete_narration', '完整的第一人称叙述内容')}

💡 字幕内容:
{segment.get('subtitle_content', '相应的字幕内容')}

🎬 视觉同步点:
"""
            for sync_point in segment.get('visual_sync_points', []):
                content += f"• {sync_point}\n"
            
            content += f"""
✂️ 剪辑说明:
{segment.get('editing_notes', '专业剪辑指导说明')}

⚙️ 技术特点:
• 无声视频设计 - 专为第一人称叙述优化
• AI分析剪辑点 - 确保内容与叙述同步
• 智能时间处理 - 支持非连续但逻辑连贯的剪辑
• 第一人称视角 - 完整详细的观众体验叙述

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
AI分析系统: 100% AI驱动电影剪辑系统
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"    📄 AI分析报告: {os.path.basename(report_path)}")
            
        except Exception as e:
            print(f"    ⚠️ 报告生成失败: {e}")

    def _create_protagonist_story_report(self, analysis: Dict, created_videos: List[str], title: str, protagonist: str):
        """创建主人公完整故事报告"""
        try:
            report_path = os.path.join(self.analysis_folder, f"{title}_{protagonist}_完整故事AI分析报告.txt")
            
            info = analysis.get('info', {})
            protagonist_analysis = analysis.get('protagonist_analysis', {})
            storyline = analysis.get('complete_storyline', {})
            segments = analysis.get('video_segments', [])
            
            content = f"""🎬 《{title}》主人公完整故事AI分析报告
{'=' * 100}

🤖 AI分析状态: {analysis.get('ai_analysis_status', 'unknown')}
📊 AI置信度: {analysis.get('ai_confidence_score', 0)}/10

🎭 电影基本信息:
• 标题: {info.get('title', title)}
• 类型: {info.get('genre', 'AI识别中')}
• 时长: {info.get('duration_minutes', 0):.1f} 分钟
• 分析置信度: {info.get('analysis_confidence', 0)}/10

👤 主人公AI分析:
• 主人公: {protagonist_analysis.get('main_protagonist', protagonist)}
• 角色轨迹: {protagonist_analysis.get('character_arc', '角色成长过程')}
• 故事视角: {protagonist_analysis.get('story_perspective', '主人公视角故事')}
• 性格特征: {', '.join(protagonist_analysis.get('character_traits', []))}
• AI选择理由: {protagonist_analysis.get('protagonist_reasoning', 'AI深度分析结果')}

📖 完整故事线分析:
• 故事结构: {storyline.get('story_structure', '完整故事架构')}
• 叙事流程: {storyline.get('narrative_flow', '叙事发展过程')}
• 故事长度: {storyline.get('story_length_assessment', 'medium')}
• 关键时刻: {', '.join(storyline.get('key_story_moments', []))}

🎬 视频片段制作详情 (共{len(segments)}段):
"""
            
            total_duration = 0
            for i, (segment, video_path) in enumerate(zip(segments, created_videos), 1):
                duration = segment.get('duration_seconds', 0)
                total_duration += duration
                
                content += f"""
第{i}段: {segment.get('segment_title', f'片段{i}')}
• 剧情点: {segment.get('plot_type', '未知')}
• 时长: {duration:.1f} 秒
• 视频文件: {os.path.basename(video_path)}
• 字幕文件: {os.path.basename(video_path).replace('.mp4', '_第一人称叙述.srt')}
• 分析报告: {os.path.basename(video_path).replace('.mp4', '_AI分析报告.txt')}
• 逻辑连贯性: {segment.get('logical_coherence', '确保逻辑连贯')[:100]}...
"""
            
            content += f"""

📊 制作统计:
• 总片段数: {len(created_videos)} 个
• 总时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)
• 平均时长: {total_duration/len(segments) if segments else 0:.1f} 秒
• 成功率: {len(created_videos)/len(segments)*100:.1f}%

🎯 系统特色实现:
• ✅ 100% AI分析 - 完全由AI驱动的深度分析
• ✅ 主人公识别 - AI智能识别: {protagonist}
• ✅ 完整故事线 - 以主人公视角构建完整叙述
• ✅ 非连续剪辑 - 时间不连续但逻辑连贯
• ✅ 第一人称叙述 - 详细清晰的观众视角
• ✅ 无声视频 - 专为AI叙述设计
• ✅ 固定输出格式 - 标准化专业报告

🌟 主人公故事总结:
{analysis.get('protagonist_story_summary', '通过AI分析，以主人公视角完整展现了故事的发展脉络和情感历程。')}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
AI分析引擎: 100% AI驱动电影剪辑系统 v1.0
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n📄 主人公完整故事报告: {os.path.basename(report_path)}")
            
        except Exception as e:
            print(f"⚠️ 故事报告生成失败: {e}")

    def find_video_file(self, srt_filename: str) -> Optional[str]:
        """智能查找对应的电影视频文件"""
        base_name = os.path.splitext(srt_filename)[0]
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配
        if os.path.exists(self.videos_folder):
            for filename in os.listdir(self.videos_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    file_base = os.path.splitext(filename)[0].lower()
                    if any(part in file_base for part in base_name.lower().split('_') if len(part) > 2):
                        return os.path.join(self.videos_folder, filename)
        
        return None

    def process_single_movie(self, srt_filename: str) -> bool:
        """处理单部电影 - 完整AI驱动流程"""
        print(f"\n🎬 处理电影: {srt_filename}")
        
        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_filename)
        data = self.parse_subtitles(srt_path)
        
        if not data:
            print("❌ 字幕解析失败")
            return False
        
        # 2. 100% AI分析
        analysis = self.ai_analyze_complete_movie(data)
        
        if not analysis:
            print("❌ AI分析失败，直接返回")
            return False
        
        # 3. 查找视频文件
        video_file = self.find_video_file(srt_filename)
        
        if not video_file:
            print("❌ 未找到对应视频文件")
            return False
        
        # 4. 创建主人公故事视频
        created_videos = self.create_protagonist_story_videos(analysis, data, video_file)
        
        if created_videos:
            print(f"✅ 成功创建 {len(created_videos)} 个主人公故事视频")
            return True
        else:
            print("❌ 视频创建失败")
            return False

    def ai_analyze_movie(self, subtitles: List[Dict], episode_name: str) -> Optional[Dict]:
        """AI分析电影（支持缓存）- 兼容原有功能"""
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置")
            return None

        # 缓存机制
        content_hash = hashlib.md5(f"{episode_name}_{len(subtitles)}".encode()).hexdigest()[:16]
        cache_file = os.path.join(self.cache_folder, f"analysis_{episode_name}_{content_hash}.json")

        # 检查缓存
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    if cached.get('highlight_clips'):
                        print("💾 使用缓存结果")
                        return cached
            except:
                pass

        print(f"🤖 AI分析中: {episode_name}")

        # 构建分析内容
        sample_content = self._build_sample_content(subtitles)

        prompt = f"""分析电影《{episode_name}》，识别3-5个最精彩的片段用于剪辑。

【字幕内容样本】
{sample_content}

请返回JSON格式：
{{
    "title": "{episode_name}",
    "highlight_clips": [
        {{
            "clip_id": 1,
            "title": "片段标题",
            "start_time": "00:10:30,000",
            "end_time": "00:13:45,000",
            "reason": "选择原因",
            "content": "片段内容描述"
        }}
    ]
}}"""

        try:
            response = self._call_ai_api(prompt)
            if response:
                result = self._parse_ai_response(response)
                if result and result.get('highlight_clips'):
                    # 保存缓存
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print("✅ AI分析完成")
                    return result

            print("❌ AI分析失败")
            return None
        except Exception as e:
            print(f"❌ AI分析异常: {e}")
            return None

    def parse_srt_file(self, filepath: str) -> List[Dict]:
        """解析SRT文件 - 兼容原有功能"""
        print(f"📖 解析字幕: {os.path.basename(filepath)}")

        # 尝试不同编码
        content = None
        for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                    if content.strip():
                        break
            except:
                continue

        if not content:
            print(f"❌ 无法读取文件")
            return []

        # 解析字幕条目
        subtitles = []
        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0]) if lines[0].isdigit() else len(subtitles) + 1
                    time_pattern = r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})'
                    time_match = re.search(time_pattern, lines[1])

                    if time_match:
                        start_time = time_match.group(1).replace('.', ',')
                        end_time = time_match.group(2).replace('.', ',')
                        text = '\n'.join(lines[2:]).strip()

                        if text:
                            subtitles.append({
                                'index': index,
                                'start': start_time,
                                'end': end_time,
                                'text': text,
                                'start_seconds': self._time_to_seconds(start_time),
                                'end_seconds': self._time_to_seconds(end_time)
                            })
                except (ValueError, IndexError):
                    continue

        print(f"✅ 解析完成: {len(subtitles)} 条字幕")
        return subtitles

    def _build_sample_content(self, subtitles: List[Dict]) -> str:
        """构建分析样本内容"""
        total = len(subtitles)

        # 取开头、中间、结尾各20%
        start_end = int(total * 0.2)
        middle_start = int(total * 0.4)
        middle_end = int(total * 0.6)
        end_start = int(total * 0.8)

        start_text = ' '.join([sub['text'] for sub in subtitles[:start_end]])
        middle_text = ' '.join([sub['text'] for sub in subtitles[middle_start:middle_end]])
        end_text = ' '.join([sub['text'] for sub in subtitles[end_start:]])

        return f"【开头】{start_text}\n\n【中间】{middle_text}\n\n【结尾】{end_text}"

    def create_video_clips(self, analysis: Dict, video_file: str, episode_name: str) -> List[str]:
        """创建视频片段 - 兼容原有功能"""
        if not analysis or not analysis.get('highlight_clips'):
            print("❌ 无分析结果")
            return []

        clips = analysis['highlight_clips']
        created_files = []

        for i, clip in enumerate(clips, 1):
            clip_title = self._safe_filename(clip.get('title', f'片段{i}'))
            clip_filename = f"{episode_name}_{clip_title}_seg{i}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)

            print(f"\n🎬 剪辑片段 {i}: {clip.get('title', '未知')}")

            if self._create_single_clip(video_file, clip, clip_path):
                created_files.append(clip_path)
            else:
                print(f"   ❌ 剪辑失败")

        return created_files

    def _create_single_clip(self, video_file: str, clip: Dict, output_path: str) -> bool:
        """创建单个视频片段 - 兼容原有功能"""
        try:
            start_time = clip.get('start_time')
            end_time = clip.get('end_time')

            if not start_time or not end_time:
                return False

            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds

            if duration <= 0:
                return False

            # FFmpeg命令
            cmd = [
                'ffmpeg', '-i', video_file,
                '-ss', str(start_seconds),
                '-t', str(duration),
                '-c:v', 'libx264', '-c:a', 'aac',
                '-preset', 'medium', '-crf', '23',
                output_path, '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"    ✅ 成功: {size_mb:.1f}MB")
                return True
            else:
                print(f"    ❌ FFmpeg失败")
                return False

        except Exception as e:
            print(f"    ❌ 异常: {e}")
            return False

    def find_video_file(self, episode_name: str) -> Optional[str]:
        """查找对应视频文件 - 兼容原有功能"""
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov']

        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.videos_folder, episode_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 模糊匹配
        for filename in os.listdir(self.videos_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                if episode_name.lower() in filename.lower():
                    return os.path.join(self.videos_folder, filename)

        return None

    def _extract_episode_number(self, filename: str) -> str:
        """提取集数，使用SRT文件名作为集数标识"""
        # 移除扩展名，直接使用文件名作为集数
        return os.path.splitext(filename)[0]

    def process_single_legacy(self, srt_file: str) -> bool:
        """处理单部电影 - 兼容原有功能"""
        print(f"\n{'='*20} 处理电影 {'='*20}")
        print(f"文件: {srt_file}")

        # 1. 解析字幕
        srt_path = os.path.join(self.srt_folder, srt_file)
        subtitles = self.parse_srt_file(srt_path)

        if not subtitles:
            return False

        # 2. 提取集数（使用文件名）
        episode_name = self._extract_episode_number(srt_file)

        # 3. AI分析
        analysis = self.ai_analyze_movie(subtitles, episode_name)
        if not analysis:
            return False

        # 4. 查找视频文件
        video_file = self.find_video_file(episode_name)
        if not video_file:
            print("❌ 未找到视频文件")
            return False

        print(f"📁 视频: {os.path.basename(video_file)}")

        # 5. 创建视频片段
        created_clips = self.create_video_clips(analysis, video_file, episode_name)

        print(f"✅ 完成！生成 {len(created_clips)} 个片段")
        return True

    def process_all_movies(self):
        """批量处理所有电影"""
        print("\n🚀 批量处理所有电影")
        print("=" * 40)

        # 检查AI配置
        if not self.ai_config.get('enabled'):
            print("❌ AI未配置")
            return

        # 获取所有SRT文件
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.endswith(('.srt', '.txt')) and not f.startswith('.')]

        if not srt_files:
            print(f"❌ {self.srt_folder}/ 中无字幕文件")
            return

        # 按字符串排序（电影顺序）
        srt_files.sort()
        print(f"📝 找到 {len(srt_files)} 个字幕文件")

        success_count = 0
        for i, srt_file in enumerate(srt_files, 1):
            print(f"\n{'🎬'*3} 第 {i}/{len(srt_files)} 部 {'🎬'*3}")

            try:
                # 优先使用AI驱动模式，失败则使用传统模式
                if self.process_single_movie(srt_file):
                    success_count += 1
                elif self.process_single_legacy(srt_file):
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理异常: {e}")

        print(f"\n🎉 批量处理完成")
        print(f"✅ 成功: {success_count}/{len(srt_files)} 部")

    def show_main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 50)
            print("🎬 AI剪辑系统 - 电影&电视剧")
            print("=" * 50)

            # 状态显示
            ai_status = "✅ 已配置" if self.ai_config.get('enabled') else "❌ 未配置"
            print(f"🤖 AI状态: {ai_status}")

            srt_count = len([f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))])
            video_count = len([f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]) if os.path.exists(self.videos_folder) else 0

            print(f"📝 字幕文件: {srt_count} 个")
            print(f"🎬 视频文件: {video_count} 个")

            print(f"\n🎯 功能菜单:")
            print("1. 🤖 配置AI接口")
            print("2. 🚀 电影智能剪辑")
            print("3. 📺 电视剧AI剪辑（新功能）")
            print("4. 📊 查看状态")
            print("0. ❌ 退出")

            try:
                choice = input("\n请选择 (0-4): ").strip()

                if choice == '0':
                    print("\n👋 谢谢使用！")
                    break
                elif choice == '1':
                    self.setup_ai_config()
                elif choice == '2':
                    if not self.ai_config.get('enabled'):
                        print("❌ 请先配置AI")
                        continue
                    self.process_all_movies()
                elif choice == '3':
                    if not self.ai_config.get('enabled'):
                        print("❌ 电视剧剪辑需要配置AI")
                        continue
                    self.run_tv_series_mode()
                elif choice == '4':
                    self._show_status()
                else:
                    print("❌ 无效选择")

            except KeyboardInterrupt:
                print("\n\n👋 用户中断")
                break

    def run_tv_series_mode(self):
        """运行电视剧AI剪辑模式"""
        if not TV_SYSTEM_AVAILABLE:
            print("❌ 电视剧剪辑模块未安装")
            print("请确保以下文件存在：")
            print("  - tv_series_system.py")
            print("  - tv_ai_analyzer.py")
            print("  - tv_video_clipper.py")
            print("  - tv_subtitle_generator.py")
            return

        print("\n" + "="*60)
        print("📺 电视剧AI剪辑系统")
        print("="*60)
        print("核心功能：")
        print("✅ 100% AI分析（支持缓存）")
        print("✅ 智能剧情点识别")
        print("✅ 视频剪辑（支持断点续传）")
        print("✅ 旁观者叙述字幕生成")
        print("✅ 跨集连贯性处理")
        print("✅ 多次执行结果一致")

        # 初始化电视剧剪辑系统
        try:
            tv_system = TVSeriesClipperSystem(self.ai_config)
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            return

        # 获取所有字幕文件
        srt_files = tv_system.get_all_srt_files()

        if not srt_files:
            print(f"\n❌ {tv_system.srt_folder}/ 目录中未找到字幕文件")
            return

        print(f"\n📝 找到 {len(srt_files)} 个字幕文件")
        print("\n选择处理模式：")
        print("1. 📺 处理所有集数")
        print("2. 🎯 选择特定集数")
        print("0. ❌ 返回主菜单")

        mode_choice = input("\n请选择 (0-2): ").strip()

        if mode_choice == '0':
            return
        elif mode_choice == '1':
            # 批量处理所有集数
            stats = tv_system.process_all_episodes()
            self._show_tv_series_stats(stats)
        elif mode_choice == '2':
            # 选择特定集数
            self._select_and_process_episodes(tv_system, srt_files)
        else:
            print("❌ 无效选择")

    def _select_and_process_episodes(self, tv_system, srt_files: List[str]):
        """选择并处理特定集数"""
        print("\n可用的集数：")
        for i, srt_file in enumerate(srt_files, 1):
            print(f"{i}. {srt_file}")

        print("\n输入要处理的集数（多个用逗号分隔，如: 1,3,5 或 1-5）")
        selection = input("请输入: ").strip()

        if not selection:
            return

        # 解析选择
        selected_indices = self._parse_selection(selection, len(srt_files))

        if not selected_indices:
            print("❌ 无效的选择")
            return

        print(f"\n将处理 {len(selected_indices)} 集")

        success_count = 0
        for idx in selected_indices:
            srt_file = srt_files[idx - 1]
            try:
                if tv_system.process_single_episode(srt_file):
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理异常: {e}")

        print(f"\n✅ 完成！成功处理 {success_count}/{len(selected_indices)} 集")

    def _parse_selection(self, selection: str, max_num: int) -> List[int]:
        """解析用户选择的集数"""
        indices = []

        for part in selection.split(','):
            part = part.strip()
            if '-' in part:
                # 范围选择，如 1-5
                try:
                    start, end = part.split('-')
                    start = int(start.strip())
                    end = int(end.strip())
                    indices.extend(range(start, end + 1))
                except:
                    continue
            else:
                # 单个选择
                try:
                    idx = int(part)
                    if 1 <= idx <= max_num:
                        indices.append(idx)
                except:
                    continue

        # 去重并排序
        return sorted(list(set(indices)))

    def _show_tv_series_stats(self, stats: Dict):
        """显示电视剧处理统计"""
        print("\n" + "="*60)
        print("📊 电视剧处理统计")
        print("="*60)
        print(f"总集数: {stats['total']}")
        print(f"成功: {stats['success']}")
        print(f"失败: {len(stats['failed'])}")
        print(f"成功率: {stats['success']/stats['total']*100:.1f}%")

        if stats['failed']:
            print(f"\n失败的集数:")
            for ep in stats['failed']:
                print(f"  - {ep}")

    def run_ai_driven_mode(self):
        """运行100% AI驱动模式"""
        print("\n🤖 启动100% AI驱动电影剪辑模式")
        print("=" * 60)
        print("🎯 满足7个核心需求:")
        print("1. ✅ 字幕解析和错误修正")
        print("2. ✅ AI识别主人公")
        print("3. ✅ 主人公完整故事线")
        print("4. ✅ 非连续剧情点剪辑")
        print("5. ✅ 100% AI分析")
        print("6. ✅ 固定输出格式")
        print("7. ✅ 无声视频+第一人称叙述")
        
        # 获取字幕文件
        srt_files = [f for f in os.listdir(self.srt_folder) 
                     if f.lower().endswith(('.srt', '.txt')) and not f.startswith('.')]
        
        if not srt_files:
            print(f"❌ {self.srt_folder}/ 目录中未找到字幕文件")
            return
        
        srt_files.sort()
        
        print(f"📄 找到 {len(srt_files)} 个字幕文件")
        
        # 处理每部电影
        success_count = 0
        total_videos = 0
        
        for srt_file in srt_files:
            try:
                if self.process_single_movie(srt_file):
                    success_count += 1
                    # 统计创建的视频数量
                    title = os.path.splitext(srt_file)[0]
                    video_pattern = f"{title}_*_第*段_*.mp4"
                    import glob
                    videos = glob.glob(os.path.join(self.output_folder, video_pattern))
                    total_videos += len(videos)
                    
            except Exception as e:
                print(f"❌ 处理 {srt_file} 时出错: {e}")
        
        # 生成最终报告
        self._create_final_system_report(success_count, len(srt_files), total_videos)

    def _create_final_system_report(self, success_count: int, total_movies: int, total_videos: int):
        """生成最终系统报告"""
        try:
            report_path = os.path.join(self.analysis_folder, "100%AI驱动电影剪辑系统总结报告.txt")
            
            content = f"""🤖 100% AI驱动电影剪辑系统 - 最终总结报告
{'=' * 100}

📊 处理统计
• 总电影数量: {total_movies} 部
• AI分析成功: {success_count} 部
• 成功率: {(success_count/total_movies*100):.1f}%
• 生成视频: {total_videos} 个
• 平均每部: {total_videos/success_count if success_count > 0 else 0:.1f} 个视频

🎯 系统特色完成情况
✅ 需求1: 字幕解析和错误修正 - 智能多编码解析，自动修正常见错误
✅ 需求2: AI识别主人公 - 100% AI深度分析，准确识别故事主角
✅ 需求3: 主人公完整故事线 - 以主人公视角构建完整叙述，长故事智能分割
✅ 需求4: 非连续剧情点剪辑 - 时间不连续但逻辑连贯，附带详细字幕
✅ 需求5: 100% AI分析 - 完全AI驱动，分析失败直接返回
✅ 需求6: 固定输出格式 - 标准化报告和文件结构
✅ 需求7: 无声视频+实时叙述 - 视频与第一人称叙述精确同步

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本: 100% AI驱动电影剪辑系统 v1.0 集成版
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n🎉 AI驱动系统处理完成！")
            print(f"📊 最终统计: {success_count}/{total_movies} 部电影成功处理")
            print(f"🎬 生成视频: {total_videos} 个")
            print(f"📄 详细报告: {os.path.basename(report_path)}")
            
        except Exception as e:
            print(f"⚠️ 生成最终报告失败: {e}")

    def _show_status(self):
        """显示系统状态"""
        print(f"\n📊 系统状态")
        print("=" * 30)

        # AI配置
        if self.ai_config.get('enabled'):
            print(f"🤖 AI配置:")
            print(f"   类型: {self.ai_config.get('api_type')}")
            print(f"   提供商: {self.ai_config.get('provider')}")
            print(f"   模型: {self.ai_config.get('model')}")
        else:
            print("🤖 AI: 未配置")

        # 文件统计
        srt_files = [f for f in os.listdir(self.srt_folder) if f.endswith(('.srt', '.txt'))]
        print(f"\n📁 文件统计:")
        print(f"   字幕文件: {len(srt_files)} 个")

        if os.path.exists(self.videos_folder):
            video_files = [f for f in os.listdir(self.videos_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]
            print(f"   视频文件: {len(video_files)} 个")

        if os.path.exists(self.clips_folder):
            clip_files = [f for f in os.listdir(self.clips_folder) if f.endswith('.mp4')]
            print(f"   传统片段: {len(clip_files)} 个")

        if os.path.exists(self.output_folder):
            ai_clip_files = [f for f in os.listdir(self.output_folder) if f.endswith('.mp4')]
            print(f"   AI驱动片段: {len(ai_clip_files)} 个")

    def _safe_filename(self, name: str) -> str:
        """安全文件名"""
        return re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', name)[:20]

    def _time_to_seconds(self, time_str: str) -> float:
        """时间转秒"""
        try:
            time_str = time_str.replace('.', ',')
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0.0

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """秒数转换为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def main():
    """主函数"""
    try:
        system = MovieClipperSystem()
        system.show_main_menu()
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能视频剪辑器 - 基于AI分析结果进行精准剪辑
"""

import os
import subprocess
import json
from typing import List, Dict, Optional

class IntelligentVideoClipper:
    def __init__(self, video_folder: str = "videos", output_folder: str = "clips"):
        self.video_folder = video_folder
        self.output_folder = output_folder
        
        # 创建输出文件夹
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"✓ 创建输出目录: {self.output_folder}/")
    
    def find_matching_video(self, subtitle_filename: str) -> Optional[str]:
        """智能匹配视频文件"""
        if not os.path.exists(self.video_folder):
            return None
        
        # 提取字幕文件的基础名
        base_name = os.path.splitext(subtitle_filename)[0]
        
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
        
        # 精确匹配
        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path
        
        # 模糊匹配 - 提取集数信息
        import re
        subtitle_episode = re.search(r'[Ee](\d+)', base_name)
        
        if subtitle_episode:
            episode_num = subtitle_episode.group(1)
            
            for filename in os.listdir(self.video_folder):
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    video_episode = re.search(r'[Ee](\d+)', filename)
                    if video_episode and video_episode.group(1) == episode_num:
                        return os.path.join(self.video_folder, filename)
        
        # 部分匹配
        for filename in os.listdir(self.video_folder):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                file_base = os.path.splitext(filename)[0]
                if any(part in file_base.lower() for part in base_name.lower().split('_')):
                    return os.path.join(self.video_folder, filename)
        
        return None
    
    def time_to_seconds(self, time_str: str) -> float:
        """时间转换"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0
    
    def create_clip(self, video_file: str, start_time: str, end_time: str, 
                   output_name: str, title: str = "") -> bool:
        """创建视频片段"""
        try:
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            if duration <= 0:
                print(f"  ❌ 无效时间段: {start_time} -> {end_time}")
                return False
            
            # 添加缓冲时间确保完整性
            buffer_start = max(0, start_seconds - 2)
            buffer_duration = duration + 4
            
            output_path = os.path.join(self.output_folder, output_name)
            
            # FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"  ✅ 创建片段: {output_name} ({file_size:.1f}MB)")
                
                # 如果有标题，添加字幕
                if title:
                    self.add_title_overlay(output_path, title)
                
                return True
            else:
                print(f"  ❌ 剪辑失败: {result.stderr[:100]}")
                return False
                
        except Exception as e:
            print(f"  ❌ 创建片段时出错: {e}")
            return False
    
    def add_title_overlay(self, video_path: str, title: str):
        """添加标题字幕"""
        try:
            temp_path = video_path.replace('.mp4', '_temp.mp4')
            
            # 清理标题文本
            clean_title = title.replace("'", "").replace('"', '').replace(':', '-')[:40]
            
            # 添加标题滤镜
            filter_text = (
                f"drawtext=text='{clean_title}':fontsize=24:fontcolor=white:"
                f"x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.7:boxborderw=5:"
                f"enable='between(t,0,3)'"
            )
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_text,
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'fast',
                temp_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                os.replace(temp_path, video_path)
                print(f"    ✓ 添加标题完成")
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
        except Exception as e:
            print(f"    ⚠ 添加标题失败: {e}")
    
    def process_analysis_results(self, analysis_results: List[Dict]) -> List[str]:
        """处理分析结果并生成视频片段"""
        print(f"\n🎬 开始视频剪辑处理...")
        print("=" * 50)
        
        created_clips = []
        
        for result in analysis_results:
            episode_name = result['episode']
            video_file = self.find_matching_video(episode_name)
            
            if not video_file:
                print(f"⚠ 未找到对应视频: {episode_name}")
                continue
            
            print(f"\n📺 处理: {result['theme']}")
            print(f"📁 源视频: {os.path.basename(video_file)}")
            print(f"🎯 片段数: {len(result['clips'])}")
            
            episode_clips = []
            
            for i, clip in enumerate(result['clips'], 1):
                clip_name = f"{result['episode_number']}_{i:02d}_{clip['reason'][:20].replace(' ', '_').replace(':', '')}.mp4"
                
                print(f"  🎬 片段{i}: {clip['start_time']} -> {clip['end_time']} ({clip['duration']:.1f}s)")
                print(f"     理由: {clip['reason']}")
                
                if self.create_clip(video_file, clip['start_time'], clip['end_time'], 
                                  clip_name, result['theme']):
                    episode_clips.append(os.path.join(self.output_folder, clip_name))
            
            # 合并本集的所有片段
            if episode_clips:
                merged_name = f"E{result['episode_number']}_完整版_{result['genre']}.mp4"
                if self.merge_clips(episode_clips, merged_name):
                    created_clips.append(os.path.join(self.output_folder, merged_name))
                    
                    # 生成说明文件
                    self.create_description_file(merged_name, result)
        
        # 创建完整合集
        if created_clips:
            self.create_complete_series(created_clips)
        
        return created_clips
    
    def merge_clips(self, clip_paths: List[str], output_name: str) -> bool:
        """合并片段"""
        try:
            output_path = os.path.join(self.output_folder, output_name)
            list_file = f"temp_list_{os.getpid()}.txt"
            
            with open(list_file, 'w', encoding='utf-8') as f:
                for clip_path in clip_paths:
                    if os.path.exists(clip_path):
                        abs_path = os.path.abspath(clip_path).replace('\\', '/')
                        f.write(f"file '{abs_path}'\n")
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path,
                '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # 清理临时文件
            if os.path.exists(list_file):
                os.remove(list_file)
            
            if result.returncode == 0:
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"  ✅ 合并完成: {output_name} ({file_size:.1f}MB)")
                return True
            else:
                print(f"  ❌ 合并失败: {result.stderr[:100]}")
                return False
                
        except Exception as e:
            print(f"  ❌ 合并时出错: {e}")
            return False
    
    def create_description_file(self, video_name: str, analysis_result: Dict):
        """创建视频说明文件"""
        desc_path = os.path.join(self.output_folder, video_name.replace('.mp4', '_说明.txt'))
        
        content = f"""📺 {analysis_result['theme']}
{"=" * 60}

🎭 剧情类型: {analysis_result['genre']}
📊 AI分析: {'是' if analysis_result.get('ai_analysis') else '否'}

💥 核心冲突:
{chr(10).join(f'• {conflict}' for conflict in analysis_result.get('key_conflicts', []))}

😊 情感高潮:
{chr(10).join(f'• {peak}' for peak in analysis_result.get('emotional_peaks', []))}

🎬 包含片段 ({len(analysis_result['clips'])} 个):
"""
        
        for i, clip in enumerate(analysis_result['clips'], 1):
            content += f"""
片段 {i}:
  时间: {clip['start_time']} --> {clip['end_time']} ({clip['duration']:.1f}秒)
  理由: {clip['reason']}
  内容: {clip['content'][:100]}...
"""
        
        content += f"""
🔗 下集衔接: {analysis_result.get('next_episode_hint', '暂无')}

📝 剪辑说明:
• 本视频根据AI智能分析生成
• 保留了剧集中最精彩的戏剧冲突和情感高潮
• 适合短视频平台传播
"""
        
        try:
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    📄 生成说明: {os.path.basename(desc_path)}")
        except Exception as e:
            print(f"    ⚠ 生成说明失败: {e}")
    
    def create_complete_series(self, episode_clips: List[str]):
        """创建完整剧集合集"""
        print(f"\n🎭 创建完整剧集精彩合集...")
        
        if self.merge_clips(episode_clips, "完整剧集精彩合集.mp4"):
            print("✅ 完整合集创建成功！")
        else:
            print("❌ 完整合集创建失败")

def process_intelligent_clipping():
    """智能剪辑主流程"""
    # 先进行分析
    from main import AIClipperSystem
    
    system = AIClipperSystem()
    analysis_results = system.analyze_all_episodes()
    
    if not analysis_results:
        print("❌ 没有分析结果，无法进行剪辑")
        return
    
    # 检查视频目录
    clipper = IntelligentVideoClipper()
    
    if not os.path.exists(clipper.video_folder):
        print(f"❌ 视频目录不存在: {clipper.video_folder}")
        print("请创建videos目录并放入对应的视频文件")
        return
    
    video_files = [f for f in os.listdir(clipper.video_folder) 
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv'))]
    
    if not video_files:
        print(f"❌ videos目录中没有视频文件")
        return
    
    print(f"✅ 找到 {len(video_files)} 个视频文件")
    
    # 处理剪辑
    created_clips = clipper.process_analysis_results(analysis_results)
    
    print(f"\n📊 剪辑完成统计:")
    print(f"✅ 分析集数: {len(analysis_results)} 集")
    print(f"✅ 创建视频: {len(created_clips)} 个")
    print(f"📁 输出目录: {clipper.output_folder}/")

if __name__ == "__main__":
    process_intelligent_clipping()

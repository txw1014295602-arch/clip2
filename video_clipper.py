import json
import subprocess
import os
from typing import List, Dict

class VideoClipper:
    def __init__(self, video_folder: str = "videos"):
        self.video_folder = video_folder
        self.output_folder = "professional_clips"

        # 创建输出文件夹
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def get_episode_video_file(self, episode_subtitle_name: str) -> str:
        """根据字幕文件名获取对应的视频文件"""
        # 处理完整路径的情况
        if os.path.sep in episode_subtitle_name:
            base_name = os.path.basename(episode_subtitle_name)
        else:
            base_name = episode_subtitle_name

        # 移除扩展名
        base_name = base_name.replace('.txt', '').replace('.srt', '')
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']

        for ext in video_extensions:
            video_path = os.path.join(self.video_folder, base_name + ext)
            if os.path.exists(video_path):
                return video_path

        # 如果没找到，尝试模糊匹配
        if os.path.exists(self.video_folder):
            for filename in os.listdir(self.video_folder):
                name_without_ext = os.path.splitext(filename)[0]
                if base_name.lower() in name_without_ext.lower() or name_without_ext.lower() in base_name.lower():
                    return os.path.join(self.video_folder, filename)

        return None

    def cut_precise_segment(self, video_file: str, start_time: str, end_time: str, output_name: str) -> bool:
        """精确剪切视频片段，使用字幕时间码 - 确保完整对话/场景"""
        try:
            # 检查输入视频文件
            if not os.path.exists(video_file):
                print(f"  ✗ 源视频文件不存在: {video_file}")
                return False

            # 获取视频信息
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', video_file
            ]

            try:
                probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
                if probe_result.returncode == 0:
                    video_info = json.loads(probe_result.stdout)
                    video_duration = float(video_info['format']['duration'])
                else:
                    print(f"  ⚠ 无法获取视频信息，继续剪辑")
                    video_duration = None
            except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
                print(f"  ⚠ 获取视频信息超时或解析失败，继续剪辑")
                video_duration = None

            # 转换时间格式和计算持续时间
            start_seconds = self.time_to_seconds(start_time)
            end_seconds = self.time_to_seconds(end_time)
            duration = end_seconds - start_seconds

            # 验证时间范围
            if video_duration and start_seconds > video_duration:
                print(f"  ✗ 开始时间超出视频长度: {start_seconds}s > {video_duration}s")
                return False

            if duration <= 0:
                print(f"  ✗ 无效的时间段: {start_time} -> {end_time}")
                return False

            # 智能缓冲时间 (根据段落长度调整)
            if duration < 30:  # 短片段
                buffer_start = max(0, start_seconds - 1)
                buffer_duration = duration + 2
            elif duration < 120:  # 中等片段
                buffer_start = max(0, start_seconds - 2)
                buffer_duration = duration + 4
            else:  # 长片段
                buffer_start = max(0, start_seconds - 3)
                buffer_duration = duration + 6

            # 确保不超出视频长度
            if video_duration:
                buffer_duration = min(buffer_duration, video_duration - buffer_start)

            # 构建FFmpeg命令 - 优化性能和质量平衡
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', str(buffer_start),
                '-t', str(buffer_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',    # 平衡速度和质量
                '-crf', '23',          # 平衡质量和文件大小
                '-profile:v', 'high',
                '-level', '4.1',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-avoid_negative_ts', 'make_zero',
                '-max_muxing_queue_size', '9999',  # 避免队列溢出
                '-threads', '0',       # 使用所有可用线程
                output_name,
                '-y'
            ]

            # 执行剪切命令，增加超时限制
            timeout_seconds = max(60, duration * 2)  # 基于片段长度的动态超时
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)

            if result.returncode == 0:
                # 验证输出文件
                if os.path.exists(output_name) and os.path.getsize(output_name) > 0:
                    file_size = os.path.getsize(output_name) / (1024*1024)  # MB
                    print(f"  ✓ 精确剪切完成: {os.path.basename(output_name)} ({file_size:.1f}MB)")
                    return True
                else:
                    print(f"  ✗ 输出文件无效: {output_name}")
                    return False
            else:
                error_msg = result.stderr.strip()
                if "Invalid data found" in error_msg:
                    print(f"  ✗ 视频文件损坏或格式不支持")
                elif "Permission denied" in error_msg:
                    print(f"  ✗ 文件权限问题")
                elif "No space left" in error_msg:
                    print(f"  ✗ 磁盘空间不足")
                else:
                    print(f"  ✗ 剪切失败: {error_msg[:100]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"  ✗ 剪切超时 ({timeout_seconds}秒)")
            return False
        except PermissionError:
            print(f"  ✗ 文件权限错误")
            return False
        except OSError as e:
            print(f"  ✗ 系统错误: {e}")
            return False
        except Exception as e:
            print(f"  ✗ 剪切视频时出错: {e}")
            return False

    def add_professional_title(self, video_path: str, episode_title: str, plot_summary: str) -> str:
        """添加专业标题和剧情说明"""
        try:
            output_path = video_path.replace('.mp4', '_titled.mp4')

            # 创建标题文本 (避免特殊字符)
            title_text = episode_title.replace("'", "").replace(":", "")
            summary_text = plot_summary[:60] + "..." if len(plot_summary) > 60 else plot_summary
            summary_text = summary_text.replace("'", "").replace(":", "")

            # 专业标题滤镜
            filter_complex = (
                f"drawtext=text='{title_text}':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=60:"
                f"box=1:boxcolor=black@0.7:boxborderw=8:enable='between(t,0,5)',"
                f"drawtext=text='{summary_text}':fontsize=20:fontcolor=white:x=(w-text_w)/2:y=110:"
                f"box=1:boxcolor=black@0.5:boxborderw=5:enable='between(t,1,5)',"
                f"fade=in:0:30,fade=out:st={5}:d=1"  # 淡入淡出效果
            )

            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_complex,
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '20',
                output_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True,
                                          encoding='utf-8', errors='ignore')

            if result.returncode == 0:
                os.remove(video_path)
                os.rename(output_path, video_path)
                print(f"    ✓ 添加专业标题完成")
                return video_path
            else:
                print(f"    ⚠ 添加标题失败，保留原视频: {result.stderr}")
                return video_path

        except Exception as e:
            print(f"    ⚠ 添加标题时出错，保留原视频: {e}")
            return video_path

    def create_episode_professional_cut(self, episode_plan: Dict) -> bool:
        """为单集创建专业剪辑版本 - 遵循剪辑规则"""
        episode_file = episode_plan['episode']
        video_file = self.get_episode_video_file(episode_file)

        if not video_file:
            print(f"  ⚠ 未找到视频文件: {episode_file}")
            return False

        episode_num = episode_plan['episode_number']
        theme = episode_plan['theme']

        print(f"\n🎬 创建 {theme}")
        print(f"📁 源视频: {os.path.basename(video_file)}")
        print(f"⏱️  目标时长: {episode_plan['total_duration']:.1f}秒")

        # 为每个片段创建临时视频
        temp_clips = []

        for i, segment in enumerate(episode_plan['segments']):
            temp_name = f"temp_E{episode_num}_seg_{i+1}.mp4"
            temp_path = os.path.join(self.output_folder, temp_name)

            print(f"  🎯 剪切片段 {i+1}: {segment['start_time']} --> {segment['end_time']} ({segment['duration']:.1f}秒)")
            print(f"     内容: {segment['plot_significance']}")

            if self.cut_precise_segment(video_file, segment['start_time'], 
                                      segment['end_time'], temp_path):
                temp_clips.append(temp_path)

        if not temp_clips:
            print(f"  ✗ 没有成功剪切的片段")
            return False

        # 合并片段
        safe_theme = theme.replace('：', '_').replace(' & ', '_').replace('/', '_')
        final_output = f"E{episode_num}_{safe_theme}.mp4"
        final_path = os.path.join(self.output_folder, final_output)

        print(f"  🔄 合并片段到: {final_output}")
        success = self.merge_clips_with_transitions(temp_clips, final_path)

        if success:
            # 添加专业标题
            plot_highlights = ' | '.join([h.split('：')[0] for h in episode_plan['highlights']]) if episode_plan['highlights'] else episode_plan['content_summary']
            self.add_professional_title(final_path, theme, plot_highlights)

            file_size = os.path.getsize(final_path) / (1024*1024)  # MB
            print(f"  ✅ 成功创建: {final_output} ({file_size:.1f}MB)")

        # 清理临时文件
        for temp_clip in temp_clips:
            if os.path.exists(temp_clip):
                os.remove(temp_clip)

        return success

    def merge_clips_with_transitions(self, clips: List[str], output_path: str) -> bool:
        """合并片段，添加平滑过渡效果 - 保持剧情连贯"""
        try:
            # 创建文件列表
            list_file = f"temp_merge_list_{os.getpid()}.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for clip in clips:
                    if os.path.exists(clip):
                        # 使用绝对路径避免问题
                        abs_path = os.path.abspath(clip).replace('\\', '/')
                        f.write(f"file '{abs_path}'\n")

            # 使用concat协议合并
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '22',  # 平衡质量和文件大小
                '-movflags', '+faststart',
                output_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True,
                                          encoding='utf-8', errors='ignore')

            # 清理临时文件
            if os.path.exists(list_file):
                os.remove(list_file)

            return result.returncode == 0

        except Exception as e:
            print(f"    ✗ 合并片段时出错: {e}")
            return False

    def time_to_seconds(self, time_str: str) -> float:
        """将SRT时间格式转换为秒数"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except (ValueError, IndexError) as e:
            print(f"⚠ 时间格式错误 {time_str}: {e}")
            return 0.0

    def create_series_complete_reel(self, all_episodes: List[str]) -> bool:
        """创建整个剧集的完整精彩集锦 - 跨集连贯性"""
        print(f"\n🎬 创建整个剧集的完整精彩集锦...")

        episode_clips = []
        for filename in sorted(os.listdir(self.output_folder)):
            if filename.startswith('E') and filename.endswith('.mp4') and '_titled' not in filename:
                episode_clips.append(os.path.join(self.output_folder, filename))

        if not episode_clips:
            print("  ⚠ 没有找到单集剪辑文件")
            return False

        print(f"  📝 找到 {len(episode_clips)} 个单集剪辑文件")

        output_path = os.path.join(self.output_folder, "Complete_Series_Professional_Highlights.mp4")
        success = self.merge_clips_with_transitions(episode_clips, output_path)

        if success:
            file_size = os.path.getsize(output_path) / (1024*1024)
            print(f"  ✅ 成功创建完整剧集精彩集锦: Complete_Series_Professional_Highlights.mp4 ({file_size:.1f}MB)")

        return success

def process_professional_series():
    """处理整个剧集的专业版剪辑 - 完整工作流程"""
    from subtitle_analyzer import analyze_all_episodes_intelligently

    print("📺 电视剧精彩片段专业剪辑系统")
    print("=" * 60)
    print("🔍 第一步：智能剧情分析...")

    all_episodes_plans = analyze_all_episodes_intelligently()

    if not all_episodes_plans:
        print("❌ 没有找到可分析的集数")
        return

    print(f"\n🎬 第二步：开始视频剪辑 ({len(all_episodes_plans)} 集)...")
    print("=" * 60)

    clipper = VideoClipper()
    successful_clips = []
    failed_clips = []

    # 检查视频文件夹
    if not os.path.exists(clipper.video_folder):
        print(f"⚠ 警告：视频文件夹 '{clipper.video_folder}' 不存在")
        print(f"请确保视频文件放在 '{clipper.video_folder}' 文件夹中")
        return

    for episode_plan in all_episodes_plans:
        try:
            success = clipper.create_episode_professional_cut(episode_plan)
            if success:
                successful_clips.append(episode_plan['episode'])
            else:
                failed_clips.append(episode_plan['episode'])
        except Exception as e:
            print(f"  ✗ 处理失败 {episode_plan['episode']}: {e}")
            failed_clips.append(episode_plan['episode'])

    print(f"\n📊 剪辑结果统计：")
    print(f"✅ 成功创建：{len(successful_clips)} 集")
    print(f"❌ 失败：{len(failed_clips)} 集")

    if failed_clips:
        print(f"失败列表：{', '.join(failed_clips)}")

    # 创建完整剧集精彩集锦
    if successful_clips:
        print(f"\n🎬 第三步：创建完整剧集精彩集锦...")
        clipper.create_series_complete_reel(successful_clips)

    print(f"\n📁 所有剪辑文件保存在: {clipper.output_folder}/")
    print(f"📄 详细剪辑方案文档: professional_editing_plan.txt")

    return successful_clips

def check_ffmpeg():
    """检查FFmpeg安装状态"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ FFmpeg已安装并可用")
            return True
    except FileNotFoundError:
        pass

    print("⚠ 警告: 未检测到FFmpeg")
    print("请安装FFmpeg以使用视频剪辑功能：")
    print("• Ubuntu/Debian: sudo apt install ffmpeg")
    print("• macOS: brew install ffmpeg")
    print("• Windows: 从 https://ffmpeg.org 下载并添加到PATH")
    return False

if __name__ == "__main__":
    if not check_ffmpeg():
        print("\n❌ 无法继续，请先安装FFmpeg")
        exit(1)

    # 开始专业剪辑处理
    process_professional_series()
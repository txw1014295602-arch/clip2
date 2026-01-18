#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频智能剪辑系统 - 主程序
支持从原始视频到精彩片段的完整流程
"""

import os
import sys
from config_manager import ConfigManager
from multi_module_api_helper import MultiModuleAPIHelper
from complete_video_processor import CompleteVideoProcessor


def main():
    """主函数"""
    print("=" * 60)
    print("🎬 视频智能剪辑系统")
    print("=" * 60)

    # 初始化配置管理器
    config_manager = ConfigManager()
    config_manager.create_directories()

    # 初始化API助手
    api_helper = MultiModuleAPIHelper(config_manager)

    # 初始化完整视频处理器
    processor = CompleteVideoProcessor(config_manager)

    # 显示主菜单
    show_main_menu(config_manager, api_helper, processor)


def show_main_menu(config_manager, api_helper, processor):
    """显示主菜单"""
    while True:
        print("\n" + "=" * 60)
        print("📋 主菜单")
        print("=" * 60)

        # 显示模块状态
        show_module_status(config_manager)

        print("\n🎯 功能选项:")
        print("1. 🎬 完整视频处理（从原始视频开始）")
        print("2. 📝 使用现有字幕处理")
        print("3. 🤖 配置AI模块")
        print("4. 🔍 测试模块连接")
        print("5. 📊 查看系统状态")
        print("0. ❌ 退出")

        try:
            choice = input("\n请选择操作 (0-5): ").strip()

            if choice == '1':
                process_video_from_scratch(processor)
            elif choice == '2':
                process_with_existing_srt(processor)
            elif choice == '3':
                configure_modules(config_manager, api_helper)
            elif choice == '4':
                test_module_connections(api_helper, config_manager)
            elif choice == '5':
                show_system_status(config_manager)
            elif choice == '0':
                print("\n👋 感谢使用视频智能剪辑系统！")
                break
            else:
                print("❌ 无效选择，请输入0-5")

        except KeyboardInterrupt:
            print("\n\n👋 用户中断，程序退出")
            break
        except Exception as e:
            print(f"❌ 操作错误: {e}")


def show_module_status(config_manager):
    """显示模块状态"""
    modules = config_manager.get_all_modules()

    print("\n📦 模块状态:")
    for module_name, module_config in modules.items():
        status = "✅ 已启用" if module_config.get('enabled') else "❌ 未启用"
        provider = module_config.get('provider', '未配置')

        # 模块名称映射
        name_map = {
            'speech_to_text': '语音转文字',
            'content_analysis': '内容分析',
            'subtitle_generation': '字幕生成'
        }

        display_name = name_map.get(module_name, module_name)
        print(f"  • {display_name}: {status} ({provider})")


def process_video_from_scratch(processor):
    """从原始视频开始处理"""
    print("\n" + "=" * 60)
    print("🎬 完整视频处理")
    print("=" * 60)

    # 获取视频文件
    video_path = input("\n请输入视频文件路径: ").strip().strip('"')

    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        input("\n按回车键返回...")
        return

    # 开始处理
    result = processor.process_video_from_scratch(video_path)

    # 显示结果
    if result['success']:
        print(f"\n✅ 处理成功！")
        print(f"📝 字幕文件: {result.get('srt_path')}")
        print(f"🎬 生成片段: {len(result.get('clips', []))} 个")
    else:
        print(f"\n❌ 处理失败: {result.get('error')}")

    input("\n按回车键返回...")


def configure_modules(config_manager, api_helper):
    """配置AI模块"""
    print("\n" + "=" * 60)
    print("🤖 配置AI模块")
    print("=" * 60)

    modules = config_manager.get_all_modules()
    module_list = list(modules.keys())

    print("\n可配置的模块:")
    for i, module_name in enumerate(module_list, 1):
        name_map = {
            'speech_to_text': '语音转文字',
            'content_analysis': '内容分析',
            'subtitle_generation': '字幕生成'
        }
        display_name = name_map.get(module_name, module_name)
        status = "✅" if modules[module_name].get('enabled') else "❌"
        print(f"{i}. {status} {display_name}")

    print("0. 返回")

    try:
        choice = input("\n请选择要配置的模块 (0-3): ").strip()
        choice_num = int(choice)

        if choice_num == 0:
            return
        elif 1 <= choice_num <= len(module_list):
            module_name = module_list[choice_num - 1]
            configure_single_module(config_manager, module_name)
        else:
            print("❌ 无效选择")

    except ValueError:
        print("❌ 请输入数字")

def process_with_existing_srt(processor):
    """使用现有字幕处理"""
    print("\n" + "=" * 60)
    print("📝 使用现有字幕处理")
    print("=" * 60)

    # 获取视频和字幕文件
    video_path = input("\n请输入视频文件路径: ").strip().strip('"')
    srt_path = input("请输入字幕文件路径: ").strip().strip('"')

    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        input("\n按回车键返回...")
        return

    if not os.path.exists(srt_path):
        print(f"❌ 字幕文件不存在: {srt_path}")
        input("\n按回车键返回...")
        return

    # 开始处理
    result = processor.process_with_existing_srt(video_path, srt_path)

    # 显示结果
    if result['success']:
        print(f"\n✅ 处理成功！")
        print(f"🎬 生成片段: {len(result.get('clips', []))} 个")
    else:
        print(f"\n❌ 处理失败: {result.get('error')}")

    input("\n按回车键返回...")


def configure_modules(config_manager, api_helper):
    """配置AI模块"""
    print("\n" + "=" * 60)
    print("🤖 配置AI模块")
    print("=" * 60)

    modules = config_manager.get_all_modules()
    module_list = list(modules.keys())

    print("\n可配置的模块:")
    for i, module_name in enumerate(module_list, 1):
        name_map = {
            'speech_to_text': '语音转文字',
            'content_analysis': '内容分析',
            'subtitle_generation': '字幕生成'
        }
        display_name = name_map.get(module_name, module_name)
        status = "✅" if modules[module_name].get('enabled') else "❌"
        print(f"{i}. {status} {display_name}")

    print("0. 返回")

    try:
        choice = input("\n请选择要配置的模块 (0-3): ").strip()
        choice_num = int(choice)

        if choice_num == 0:
            return
        elif 1 <= choice_num <= len(module_list):
            module_name = module_list[choice_num - 1]
            configure_single_module(config_manager, module_name)
        else:
            print("❌ 无效选择")

    except ValueError:
        print("❌ 请输入数字")


def configure_single_module(config_manager, module_name):
    """配置单个模块"""
    print(f"\n配置模块: {module_name}")
    current_config = config_manager.get_module_config(module_name)

    print("\n请输入配置信息:")
    provider = input(f"提供商 (当前: {current_config.get('provider', '')}): ").strip() or current_config.get('provider', '')
    api_key = input(f"API密钥: ").strip() or current_config.get('api_key', '')
    base_url = input(f"Base URL (当前: {current_config.get('base_url', '')}): ").strip() or current_config.get('base_url', '')
    model = input(f"模型 (当前: {current_config.get('model', '')}): ").strip() or current_config.get('model', '')

    new_config = {
        'enabled': True,
        'provider': provider,
        'api_key': api_key,
        'base_url': base_url,
        'model': model
    }

    if config_manager.set_module_config(module_name, new_config):
        print("✅ 配置保存成功")
    else:
        print("❌ 配置保存失败")


def test_module_connections(api_helper, config_manager):
    """测试模块连接"""
    print("\n" + "=" * 60)
    print("🔍 测试模块连接")
    print("=" * 60)

    enabled_modules = config_manager.get_enabled_modules()

    if not enabled_modules:
        print("\n⚠️ 没有已启用的模块")
        input("\n按回车键返回...")
        return

    for module_name in enabled_modules:
        api_helper.test_module_connection(module_name)

    input("\n按回车键返回...")


def show_system_status(config_manager):
    """显示系统状态"""
    print("\n" + "=" * 60)
    print("📊 系统状态")
    print("=" * 60)

    paths = config_manager.get_paths()

    print("\n📁 目录状态:")
    for path_name, path_value in paths.items():
        exists = "✅" if os.path.exists(path_value) else "❌"
        print(f"  {exists} {path_name}: {path_value}")

    print("\n📦 模块状态:")
    show_module_status(config_manager)

    input("\n按回车键返回...")


if __name__ == "__main__":
    main()

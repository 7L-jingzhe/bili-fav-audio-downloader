#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
import config


def load_bvid_data(filename="bvid.json"):
    """从指定文件加载视频信息"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"成功加载 {len(data)} 个视频信息")
            return data
    except FileNotFoundError:
        print(f" 错误: {filename} 文件不存在")
        return []
    except json.JSONDecodeError as e:
        print(f" 错误: {filename} 文件格式错误 - {e}")
        return []


def save_failed_downloads(failed_downloads):
    """
    保存未成功下载的视频信息到JSON文件

    Args:
        failed_downloads: 未成功下载的视频信息列表，格式与bvid.json相同
    """
    if not failed_downloads:
        print("\n 没有失败的下载记录")
        return

    filename = config.FILE_CONFIG.get("failed_downloads_file", "failed_downloads.json")

    try:
        # 检查是否已存在文件，如果存在则合并（避免覆盖之前的手动添加）
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # 合并数据并去重（基于bvid）
        all_failed = existing_data + failed_downloads
        unique_failed = []
        seen_bvids = set()

        for item in all_failed:
            bvid = item.get("bvid")
            if bvid and bvid not in seen_bvids:
                unique_failed.append(item)
                seen_bvids.add(bvid)

        # 保存到文件
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(unique_failed, f, ensure_ascii=False, indent=2)

        print(f"\n 已保存 {len(failed_downloads)} 个失败视频信息到 {filename}")
        print(f"   (去重后总计 {len(unique_failed)} 条失败记录)")

    except Exception as e:
        print(f"\n 保存失败下载信息时出错: {e}")


def cleanup_temp_files():
    """
    清理临时文件（jpg, webp等）
    """
    output_dir = config.DOWNLOAD_CONFIG.get("default_output_dir", "./music")
    music_dir = Path(output_dir)
    if not music_dir.exists():
        return

    temp_extensions = config.DOWNLOAD_CONFIG.get(
        "temp_file_extensions",
        [".jpg", ".jpeg", ".webp", ".png", ".part", ".temp", ".ytdl"],
    )

    cleaned_count = 0
    for ext in temp_extensions:
        for temp_file in music_dir.glob(f"*{ext}"):
            try:
                temp_file.unlink()
                cleaned_count += 1
                print(f"  清理临时文件: {temp_file.name}")
            except Exception as e:
                print(f"  清理失败 {temp_file.name}: {e}")

    if cleaned_count > 0:
        print(f" 已清理 {cleaned_count} 个临时文件")


def print_download_summary(results, failed_downloads):
    """
    打印下载结果汇总

    Args:
        results: 所有下载结果列表
        failed_downloads: 失败下载的视频信息列表
    """
    success_count = len([r for r in results if r.get("status") == "success"])
    failed_count = len([r for r in results if r.get("error")])
    not_found_count = len(
        [r for r in results if r.get("status") == "downloaded_but_file_not_found"]
    )
    total_count = len(results)

    print("\n" + "=" * 60)
    print(" 下载完成！结果汇总：")
    print("=" * 60)
    print(f" 总计: {total_count} 个视频")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {failed_count} 个")
    if not_found_count > 0:
        print(f"   文件未找到: {not_found_count} 个")
    print("=" * 60)

    if failed_downloads:
        failed_file = config.FILE_CONFIG.get(
            "failed_downloads_file", "failed_downloads.json"
        )
        print(f"\n📁 失败的视频信息已保存至: {failed_file}")


def retry_failed_downloads():
    """
    重试失败的下载
    """
    print(f"\n 开始重试失败的下载...")
    failed_file = config.FILE_CONFIG.get(
        "failed_downloads_file", "failed_downloads.json"
    )
    failed_list = load_bvid_data(failed_file)

    if not failed_list:
        print("没有失败的下载记录需要重试")
        return []

    print(f"找到 {len(failed_list)} 个需要重试的视频")
    return failed_list


def prepare_video_list(args):
    """
    根据命令行参数准备待下载的视频列表

    Args:
        args: 解析后的命令行参数

    Returns:
        list: 视频信息列表，如果无法获取则返回空列表
    """
    single_mode = args.bvid is not None

    if single_mode:
        video_info = {"bvid": args.bvid}
        if args.title:
            video_info["title"] = args.title
        if args.artist:
            video_info["artist"] = args.artist
        if args.album:
            video_info["album"] = args.album

        default_title = args.bvid
        default_artist = config.DOWNLOAD_CONFIG.get(
            "default_unknown_artist", "未知作者"
        )
        default_album = config.DOWNLOAD_CONFIG.get("default_album", "Bilibili音频")

        video_info.setdefault("title", default_title)
        video_info.setdefault("artist", default_artist)
        video_info.setdefault("album", default_album)

        video_list = [video_info]
        print(f"\n 单个下载模式: {video_info['title']}")

        if args.start != 1 or args.end is not None:
            print(" 提示：范围参数在单个下载模式中无效，将被忽略")
    else:
        if args.retry:
            video_list = retry_failed_downloads()
            if not video_list:
                return []
        else:
            video_list = load_bvid_data(args.input)
            if not video_list:
                return []

        start_idx = max(1, args.start) - 1
        end_idx = args.end if args.end else len(video_list)

        if start_idx >= len(video_list):
            print(f" 起始索引 {args.start} 超过总视频数 {len(video_list)}")
            return []

        if end_idx > len(video_list):
            end_idx = len(video_list)
            print(f" 结束索引已调整为 {end_idx} (总视频数)")

        if start_idx > 0 or end_idx < len(video_list):
            video_list = video_list[start_idx:end_idx]
            print(
                f" 将下载第 {args.start} 到第 {end_idx} 个视频 (共 {len(video_list)} 个)"
            )

    return video_list

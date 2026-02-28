import json
from time import sleep
from datetime import datetime
from dowload import download_with_ytdlp
from pathlib import Path


def log(data):
    """保存未成功下载的音频到日志"""
    logstr = f"{'-' * 17}\n下载失败\n{datetime.now()}\n"
    logstr += f"bvid: {data.get('bvid')}\n"
    logstr += f"title: {data.get('title')}\n"
    logstr += f"artist: {data.get('artist')}\n"
    logstr += f"error: {data.get('error')}\n\n"

    with open("download_error.log", "a", encoding="utf-8") as f:
        f.write(logstr)


def load_bvid_data():
    """从 bvid.json 文件加载视频信息"""
    try:
        with open("failed_downloads.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"成功加载 {len(data)} 个视频信息")
            return data
    except FileNotFoundError:
        print(" 错误: bvid.json 文件不存在")
        return []
    except json.JSONDecodeError as e:
        print(f" 错误: bvid.json 文件格式错误 - {e}")
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

    filename = "failed_downloads.json"

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
    music_dir = Path("./music")
    if not music_dir.exists():
        return

    # 要清理的文件扩展名
    temp_extensions = [".jpg", ".jpeg", ".webp", ".png", ".part", ".temp"]

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
        print(f"  已清理 {cleaned_count} 个临时文件")


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
    print("下载完成！结果汇总：")
    print("=" * 60)
    print(f" 总计: {total_count} 个视频")
    print(f" 成功: {success_count} 个")
    print(f" 失败: {failed_count} 个")
    if not_found_count > 0:
        print(f" 文件未找到: {not_found_count} 个")
    print("=" * 60)

    if failed_downloads:
        print(f"\n 失败的视频信息已保存至: failed_downloads.json")


def main():
    # 从 bvid.json 加载视频信息
    video_list = load_bvid_data()

    if not video_list:
        print("没有可下载的视频信息，程序退出")
        return

    # 存储所有下载结果
    all_results = []
    # 存储所有未成功下载的视频信息
    failed_downloads = []

    print("\n开始批量下载音频...")
    print(f"总共 {len(video_list)} 个视频")
    print("=" * 50)

    # 依次下载所有的音频
    for index, video_info in enumerate(video_list, 1):
        print(f"\n处理进度: {index}/{len(video_list)}")
        print(f"当前视频: {video_info.get('title')} - {video_info.get('artist')}")

        try:
            # 下载音频
            result = download_with_ytdlp(video_info)
            all_results.append(result)

            # 检查是否有错误
            if result.get("error"):
                print(f"❌ 下载失败，已记录到日志")
                log(result)  # 记录错误到日志
                failed_downloads.append(video_info)  # 保存原始视频信息
            elif result.get("status") == "downloaded_but_file_not_found":
                print(f"⚠️ 下载成功但文件未找到")
                # failed_downloads.append(video_info)  # 文件未找到也算作失败
            else:
                print(f"✅ 下载完成")

        except Exception as e:
            print(f"❌ 发生异常: {e}")
            error_data = {
                "bvid": video_info.get("bvid"),
                "title": video_info.get("title"),
                "artist": video_info.get("artist"),
                "error": str(e),
            }
            all_results.append(error_data)
            log(error_data)
            failed_downloads.append(video_info)  # 异常也算作失败
            continue

        # 最后一个视频不需要等待
        if index < len(video_list):
            print("间隔3秒后继续下一个...")
            sleep(3)

    # 将未下载成功的音频信息保存到json文件
    save_failed_downloads(failed_downloads)

    # 无论成功与否，都清理临时文件
    cleanup_temp_files()

    # 打印下载结果汇总
    print_download_summary(all_results, failed_downloads)


if __name__ == "__main__":
    main()

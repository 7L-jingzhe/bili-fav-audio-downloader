import subprocess
import os
import re
import shutil
import glob
import time
import config
from datetime import datetime


def log(data):
    """保存未成功下载的音频到日志"""
    logstr = f"{'-' * 17}\n下载失败\n{datetime.now()}\n"
    logstr += f"bvid: {data.get('bvid')}\n"
    logstr += f"title: {data.get('title')}\n"
    logstr += f"artist: {data.get('artist')}\n"
    logstr += f"error: {data.get('error')}\n\n"

    log_file = config.FILE_CONFIG.get("error_log_file", "download_error.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(logstr)


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
    filename = re.sub(illegal_chars, "", filename)
    filename = re.sub(r"\s+", " ", filename).strip()
    max_len = config.OUTPUT_CONFIG.get("max_filename_length", 100)
    return filename[:max_len]


def find_ytdlp():
    """查找 yt-dlp 的完整路径"""
    ytdlp_path = shutil.which("yt-dlp")
    if ytdlp_path:
        return ytdlp_path

    common_paths = config.YTDLP_COMMON_PATHS
    for pattern in common_paths:
        expanded = os.path.expanduser(pattern)
        matches = glob.glob(expanded)
        if matches:
            return matches[0]

    return "yt-dlp"


def check_ytdlp_available(ytdlp_cmd):
    """检查 yt-dlp 是否可用"""
    try:
        subprocess.run([ytdlp_cmd, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def print_ytdlp_installation_instructions():
    """打印 yt-dlp 安装说明"""
    print(" yt-dlp 未安装或无法找到")
    print("\n请安装 yt-dlp:")
    print("   pip install yt-dlp")
    print("   或")
    print("   uv pip install yt-dlp")


def prepare_download_environment(bvid, title, output_dir):
    """准备下载环境，创建必要的目录"""
    safe_title = sanitize_filename(title) if title else bvid
    output_filename = f"{bvid}.%(ext)s"
    output_path = os.path.join(output_dir, output_filename)
    os.makedirs(output_dir, exist_ok=True)
    url = f"https://www.bilibili.com/video/{bvid}"
    return output_path, url, safe_title


def build_ytdlp_command(ytdlp_cmd, output_path, url, title, artist, album):
    """构建 yt-dlp 下载命令"""
    metadata_args = f'-metadata title="{title}" -metadata artist="{artist}" -metadata album="{album}"'
    cmd = [
        ytdlp_cmd,
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--embed-thumbnail",
        "--add-metadata",
        "--postprocessor-args",
        f"ffmpeg:{metadata_args}",
        "-o",
        output_path,
        url,
    ]
    return cmd


def find_downloaded_file(bvid, output_dir):
    """查找下载的MP3文件"""
    found_files = []
    for file in os.listdir(output_dir):
        if bvid in file and file.endswith(".mp3"):
            mp3_file = os.path.join(output_dir, file)
            found_files.append(mp3_file)
            print(f"文件已保存: {mp3_file}")
    return found_files


def list_music_directory(output_dir):
    """列出指定目录下的所有文件"""
    print(f"{output_dir} 目录中的文件:")
    for file in os.listdir(output_dir):
        print(f"  - {file}")


def create_success_result(bvid, title, artist, file_path):
    return {
        "bvid": bvid,
        "title": title,
        "artist": artist,
        "file_path": file_path,
        "status": "success",
    }


def create_error_result(bvid, title, error_message):
    return {"bvid": bvid, "title": title, "error": error_message}


def create_file_not_found_result(bvid, title):
    return {"bvid": bvid, "title": title, "status": "downloaded_but_file_not_found"}


def download_with_ytdlp(video_info, output_dir=None):
    """
    使用 yt-dlp 下载单个音频

    Args:
        video_info: 包含 bvid, title, artist, album 的字典
        output_dir: 输出目录，若为 None 则使用配置中的默认目录

    Returns:
        dict: 下载结果
    """
    if output_dir is None:
        output_dir = config.DOWNLOAD_CONFIG.get("default_output_dir", "./music")

    bvid = video_info.get("bvid", "")
    title = video_info.get("title", "")
    artist = video_info.get("artist", "")
    default_album = config.DOWNLOAD_CONFIG.get("default_album", "Bilibili音频")
    album = video_info.get("album", default_album)

    print("-" * 50)
    print(f"开始下载: {bvid}")
    print(f"标题: {title}")
    print(f"歌手: {artist}")

    ytdlp_cmd = find_ytdlp()
    if not check_ytdlp_available(ytdlp_cmd):
        print_ytdlp_installation_instructions()
        return create_error_result(bvid, title, "yt-dlp not found")

    output_path, url, safe_title = prepare_download_environment(bvid, title, output_dir)
    cmd = build_ytdlp_command(ytdlp_cmd, output_path, url, title, artist, album)

    print("正在下载并转换...")
    print(f"使用命令: {ytdlp_cmd}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f" 下载失败: {result.stderr}")
            return create_error_result(bvid, title, result.stderr)

        print(f" 下载成功！")
        time.sleep(1)

        found_files = find_downloaded_file(bvid, output_dir)

        if found_files:
            return create_success_result(bvid, title, artist, found_files[0])
        else:
            print(" 文件已下载，但找不到 MP3 文件")
            list_music_directory(output_dir)
            return create_file_not_found_result(bvid, title)

    except Exception as e:
        print(f" 发生错误: {str(e)}")
        return create_error_result(bvid, title, str(e))


def batch_download(video_list, output_dir=None, sleep_interval=3):
    """
    批量下载音频

    Args:
        video_list: 视频信息列表
        output_dir: 输出目录，若为 None 则使用配置中的默认目录
        sleep_interval: 下载间隔（秒）

    Returns:
        tuple: (all_results, failed_downloads)
    """
    if output_dir is None:
        output_dir = config.DOWNLOAD_CONFIG.get("default_output_dir", "./music")

    all_results = []
    failed_downloads = []

    print("\n 开始批量下载音频...")
    print(f" 输出目录: {output_dir}")
    print(f" 下载间隔: {sleep_interval}秒")
    print(f" 总共 {len(video_list)} 个视频")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)

    for index, video_info in enumerate(video_list, 1):
        print(f"\n 处理进度: \033[36m{index}/{len(video_list)}\033[0m")
        print(f" 当前视频: {video_info.get('title')} - {video_info.get('artist')}")

        try:
            result = download_with_ytdlp(video_info, output_dir)
            all_results.append(result)

            if result.get("error"):
                print(f" \033[31m下载失败，已记录到日志\033[0m")
                log(result)
                failed_downloads.append(video_info)
            elif result.get("status") == "downloaded_but_file_not_found":
                print(f" \033[33m下载成功但文件未找到\033[0m")
            else:
                print(f" \033[32m下载完成\033[0m")

        except Exception as e:
            print(f" \033[31m发生异常\033[0m: {e}")
            error_data = {
                "bvid": video_info.get("bvid"),
                "title": video_info.get("title"),
                "artist": video_info.get("artist"),
                "error": str(e),
            }
            all_results.append(error_data)
            log(error_data)
            failed_downloads.append(video_info)
            continue

        if index < len(video_list):
            print(f" 等待 {sleep_interval}秒后继续下一个...")
            time.sleep(sleep_interval)

    return all_results, failed_downloads

import subprocess
import os
import re
import shutil
import glob
import time
# from typing import Dict, Optional, List


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
    filename = re.sub(illegal_chars, "", filename)
    filename = re.sub(r"\s+", " ", filename).strip()
    return filename[:100]


def find_ytdlp():
    """查找 yt-dlp 的完整路径"""
    # 尝试在系统 PATH 中查找
    ytdlp_path = shutil.which("yt-dlp")
    if ytdlp_path:
        return ytdlp_path

    # 常见的安装路径
    common_paths = [
        os.path.expanduser("~/.local/bin/yt-dlp"),
        os.path.expanduser(
            "~/AppData/Local/Programs/Python/Python*/Scripts/yt-dlp.exe"
        ),
        "C:/Python*/Scripts/yt-dlp.exe",
        "C:/Program Files/Python*/Scripts/yt-dlp.exe",
    ]

    for pattern in common_paths:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    return "yt-dlp"  # 如果找不到，返回默认命令


def check_ytdlp_available(ytdlp_cmd):
    """
    检查 yt-dlp 是否可用

    Args:
        ytdlp_cmd: yt-dlp 命令路径

    Returns:
        bool: 是否可用
    """
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


def prepare_download_environment(bvid, title):
    """
    准备下载环境，创建必要的目录

    Args:
        bvid: 视频BV号
        title: 视频标题

    Returns:
        tuple: (output_path, url, safe_title)
    """
    # 构建输出文件名
    safe_title = sanitize_filename(title) if title else bvid
    output_filename = f"{safe_title}-{bvid}.%(ext)s"
    output_path = os.path.join("./music", output_filename)

    # 确保输出目录存在
    os.makedirs("./music", exist_ok=True)

    # 视频URL
    url = f"https://www.bilibili.com/video/{bvid}"

    return output_path, url, safe_title


def build_ytdlp_command(ytdlp_cmd, output_path, url, title, artist, album):
    """
    构建 yt-dlp 下载命令

    Args:
        ytdlp_cmd: yt-dlp 命令路径
        output_path: 输出文件路径
        url: 视频URL
        title: 视频标题
        artist: 歌手或视频作者
        album: 专辑

    Returns:
        list: 命令参数列表
    """
    # 构建传递给 ffmpeg 的元数据参数
    # 构建元数据字符串
    # 注意：这里需要正确处理引号和空格
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


def find_downloaded_file(bvid):
    """
    查找下载的MP3文件

    Args:
        bvid: 视频BV号

    Returns:
        list: 找到的文件路径列表
    """
    found_files = []
    for file in os.listdir("./music"):
        if bvid in file and file.endswith(".mp3"):
            mp3_file = os.path.join("./music", file)
            found_files.append(mp3_file)
            print(f"文件已保存: {mp3_file}")

    return found_files


def list_music_directory():
    """列出 music 目录下的所有文件"""
    print("music 目录中的文件:")
    for file in os.listdir("./music"):
        print(f"  - {file}")


def create_success_result(bvid, title, artist, file_path):
    """创建成功结果字典"""
    return {
        "bvid": bvid,
        "title": title,
        "artist": artist,
        "file_path": file_path,
        "status": "success",
    }


def create_error_result(bvid, title, error_message):
    """创建错误结果字典"""
    return {"bvid": bvid, "title": title, "error": error_message}


def create_file_not_found_result(bvid, title):
    """创建文件未找到结果字典"""
    return {
        "bvid": bvid,
        "title": title,
        "status": "downloaded_but_file_not_found",
    }


def download_with_ytdlp(video_info):
    """
    使用 yt-dlp 下载音频
    数据结构如下：
    video_info: {
        "bvid": "BV16H4y1Q7NS",
        "title": "九九八十一",
        "artist": "迷柚mio原原宿宿Yado"
    }
    """
    bvid = video_info.get("bvid", "")
    title = video_info.get("title", "")
    artist = video_info.get("artist", "")
    album = video_info.get("album", "Bilibili音频")

    # 打印下载信息
    print("-" * 50)
    print(f"开始下载: {bvid}")
    print(f"标题: {title}")
    print(f"歌手: {artist}")

    # 检查 yt-dlp 是否可用
    ytdlp_cmd = find_ytdlp()
    if not check_ytdlp_available(ytdlp_cmd):
        print_ytdlp_installation_instructions()
        return create_error_result(bvid, title, "yt-dlp not found")

    # 准备下载环境
    output_path, url, safe_title = prepare_download_environment(bvid, title)

    # 构建并执行命令
    cmd = build_ytdlp_command(ytdlp_cmd, output_path, url, title, artist, album)

    print("正在下载并转换...")
    print(f"使用命令: {ytdlp_cmd}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f" 下载失败: {result.stderr}")
            return create_error_result(bvid, title, result.stderr)

        # 下载成功
        print(f" 下载成功！")
        time.sleep(1)  # 等待文件系统刷新

        # 查找下载的文件
        found_files = find_downloaded_file(bvid)

        if found_files:
            return create_success_result(bvid, title, artist, found_files[0])
        else:
            print(" 文件已下载，但找不到 MP3 文件")
            list_music_directory()
            return create_file_not_found_result(bvid, title)

    except Exception as e:
        print(f" 发生错误: {str(e)}")
        return create_error_result(bvid, title, str(e))


if __name__ == "__main__":
    # 单个下载测试
    video_info = {
        "bvid": "BV16H4y1Q7NS",
        "title": "九九八十一",
        "artist": "迷柚mio原宿宿Yado",
    }
    result = download_with_ytdlp(video_info)

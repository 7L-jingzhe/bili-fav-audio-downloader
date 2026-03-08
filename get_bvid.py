# -*- coding: utf-8 -*-
import requests
import os
import time
import sys
import io
import re
import json
import argparse

# 导入配置
import config

# 修改系统标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    # 移除Windows系统非法字符
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
    filename = re.sub(illegal_chars, "", filename)
    # 替换连续空格为单个下划线
    filename = re.sub(r"\s+", " ", filename).strip()
    # 截断过长文件名
    return filename[: config.OUTPUT_CONFIG["max_filename_length"]]


def get_collection_list(fid, pn=1, ps=20):
    """获取收藏夹内容"""
    api_url = "https://api.bilibili.com/x/v3/fav/resource/list"

    # 从配置获取请求头
    headers = config.get_headers()

    params = {
        "media_id": fid,
        "pn": pn,
        "ps": ps,
        "keyword": "",
        "order": "mtime",
        "type": "0",
        "tid": "0",
        "platform": "web",
    }

    for attempt in range(config.API_CONFIG["max_retries"]):
        try:
            response = requests.get(
                api_url,
                headers=headers,
                params=params,
                timeout=config.API_CONFIG["timeout"],
            )
            response.encoding = "utf-8"
            response.raise_for_status()
            data = response.json()

            if data["code"] != 0:
                print(f"API错误: {data['message']}")
                return None

            return data["data"]

        except Exception as e:
            print(
                f"请求失败 (尝试 {attempt + 1}/{config.API_CONFIG['max_retries']}): {str(e)}"
            )
            if attempt < config.API_CONFIG["max_retries"] - 1:
                time.sleep(2)  # 重试前等待
            else:
                return None
    return None


def get_video_detail(bvid):
    """获取视频详细信息"""
    api_url = "https://api.bilibili.com/x/web-interface/view"

    # 从配置获取请求头
    headers = config.get_headers()

    params = {
        "bvid": bvid,
    }

    for attempt in range(config.API_CONFIG["max_retries"]):
        try:
            response = requests.get(
                api_url,
                headers=headers,
                params=params,
                timeout=config.API_CONFIG["timeout"],
            )
            response.encoding = "utf-8"
            response.raise_for_status()
            data = response.json()

            if data["code"] != 0:
                print(f"获取视频详情失败 {bvid}: {data['message']}")
                return None

            return data["data"]

        except Exception as e:
            print(
                f"请求视频详情失败 {bvid} (尝试 {attempt + 1}/{config.API_CONFIG['max_retries']}): {str(e)}"
            )
            if attempt < config.API_CONFIG["max_retries"] - 1:
                time.sleep(2)
            else:
                return None
    return None


def get_video_tags(bvid):
    """获取视频的真实标签列表"""
    api_url = "https://api.bilibili.com/x/tag/archive/tags"

    # 从配置获取请求头
    headers = config.get_headers()

    params = {"bvid": bvid}

    for attempt in range(config.API_CONFIG["max_retries"]):
        try:
            resp = requests.get(
                api_url,
                headers=headers,
                params=params,
                timeout=config.API_CONFIG["timeout"],
            )
            resp.encoding = "utf-8"
            data = resp.json()
            if data["code"] == 0 and data["data"]:
                # 返回标签名称列表
                return [tag["tag_name"] for tag in data["data"]]
        except Exception as e:
            print(
                f"获取标签失败 {bvid} (尝试 {attempt + 1}/{config.API_CONFIG['max_retries']}): {e}"
            )
            if attempt < config.API_CONFIG["max_retries"] - 1:
                time.sleep(1)
    return []  # 失败则返回空列表


def save_video_list_json(video_info_list, filename="bvid_list.json"):
    """保存视频信息为JSON格式"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(video_info_list, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(video_info_list)} 个视频信息到 {os.path.abspath(filename)}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="爬取B站收藏夹视频信息")
    parser.add_argument(
        "-n", "--num", type=int, default=None, help="要爬取的视频数量，不指定则爬取全部"
    )
    parser.add_argument(
        "-f",
        "--fid",
        type=str,
        default=config.DEFAULT_FAVORITE_ID,
        help=f"收藏夹ID，默认为{config.DEFAULT_FAVORITE_ID}",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=config.OUTPUT_CONFIG["default_json"],
        help=f"输出文件名，默认为{config.OUTPUT_CONFIG['default_json']}",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=config.API_CONFIG["base_delay"],
        help=f"请求延迟秒数，默认为{config.API_CONFIG['base_delay']}",
    )
    return parser.parse_args()


def main():
    # 解析命令行参数
    args = parse_arguments()

    # 获取参数
    fid = args.fid
    max_videos = args.num
    delay = args.delay

    # 初始化参数
    video_info_list = []
    page = 1
    has_more = True
    collected_count = 0

    print(f"开始爬取收藏夹: {fid}")
    if max_videos:
        print(f"目标数量: {max_videos} 个视频")
    else:
        print("目标数量: 全部视频")
    print(f"请求延迟: {delay}秒")

    # 开始爬取
    while has_more:
        print(f"\n正在获取第 {page} 页...")
        data = get_collection_list(fid, pn=page)

        if not data or not data.get("medias"):
            print("没有更多数据了")
            break

        # 提取视频信息
        for media in data["medias"]:
            # 检查是否已达到目标数量
            if max_videos and collected_count >= max_videos:
                print(f"\n已达到目标数量 {max_videos} 个视频，停止爬取")
                has_more = False
                break

            if media["type"] == 2:  # 只处理视频类型
                bvid = media["bv_id"]
                print(
                    f"\n正在获取视频详情 ({collected_count + 1}/{max_videos if max_videos else '?'}): {bvid}"
                )

                # 获取视频详细信息
                detail = get_video_detail(bvid)

                if detail:
                    tags = get_video_tags(bvid)  # 获取真实标签
                    video_info = {
                        "bvid": bvid,
                        "title": sanitize_filename(media["title"]),
                        "author": detail.get("owner", {}).get("name", ""),
                        "description": detail.get("desc", "")
                        .replace("\n", " ")
                        .strip(),
                        "tags": tags,
                    }

                    video_info_list.append(video_info)
                    print(
                        f"✓ 已获取: {video_info['bvid']} - {video_info['title']} - 作者: {video_info['author']}"
                    )
                else:
                    # 详情失败时，tags留空
                    video_info = {
                        "bvid": bvid,
                        "title": sanitize_filename(media["title"]),
                        "author": "",
                        "description": "",
                        "tags": [],
                    }

                    video_info_list.append(video_info)
                    print(
                        f"⚠ 已保存基本信息: {video_info['bvid']} - {video_info['title']}"
                    )

                collected_count += 1
                time.sleep(delay)  # 使用配置的延迟时间

        # 检查是否还有下一页
        if max_videos and collected_count >= max_videos:
            break

        has_more = data.get("has_more", False)
        page += 1
        if has_more:
            print(f"准备获取下一页...")
            time.sleep(delay)  # 使用配置的延迟时间

    # 保存结果
    if video_info_list:
        save_video_list_json(video_info_list, filename=args.output)

        # 同时保存一个精简的文本版本（仅BV号）
        bvid_filename = args.output.replace("list.json", "only.txt")
        with open(bvid_filename, "w", encoding="utf-8") as f:
            for info in video_info_list:
                f.write(f"{info['bvid']}\n")
        print(f"已保存 {len(video_info_list)} 个BV号到 {bvid_filename}")

        # 显示统计信息
        print(f"\n======= 爬取完成 =======")
        print(f"总爬取视频数: {len(video_info_list)}")
        if max_videos:
            print(f"目标数量: {max_videos}")
        print(f"输出文件: {os.path.abspath(args.output)}")
    else:
        print("未找到任何视频")


if __name__ == "__main__":
    main()

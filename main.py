#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import dowload
import utils
import config


def parse_arguments():
    """解析命令行参数"""
    default_input = config.FILE_CONFIG.get("default_input_json", "bvid.json")
    default_output = config.DOWNLOAD_CONFIG.get("default_output_dir", "./music")

    parser = argparse.ArgumentParser(
        description="B站收藏夹音频批量下载工具 - 主程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                          # 使用默认配置下载
  %(prog)s -i bvid_list.json         # 从指定文件加载视频列表
  %(prog)s -r                         # 重试失败的下载
  %(prog)s -s 5                        # 设置下载间隔为5秒
  %(prog)s -o ./my_music               # 指定输出目录
  %(prog)s --start 10 --end 20          # 下载第10到第20个视频
  %(prog)s -i custom.json -s 2 -o ./downloads  # 组合使用
单个下载示例:
  %(prog)s --bvid BV1xx...               # 通过BVID下载单个视频
  %(prog)s --bvid BV1xx... --title "标题" --artist "作者"  # 提供完整信息
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=default_input,
        help=f"输入的视频信息文件 (默认: {default_input})",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=default_output,
        help=f"音频文件输出目录 (默认: {default_output})",
    )
    parser.add_argument(
        "-r",
        "--retry",
        action="store_true",
        help="重试失败的下载 (从 failed_downloads.json 读取)",
    )
    parser.add_argument(
        "-s", "--sleep", type=int, default=3, help="下载间隔秒数 (默认: 3)"
    )
    parser.add_argument(
        "--start", type=int, default=1, help="从第几个视频开始下载 (默认: 1)"
    )
    parser.add_argument(
        "--end", type=int, default=None, help="下载到第几个视频结束 (默认: 全部)"
    )

    single_group = parser.add_argument_group("单个下载选项")
    single_group.add_argument(
        "-b",
        "--bvid",
        type=str,
        help="下载单个视频，指定BVID",
    )
    single_group.add_argument(
        "-t",
        "--title",
        type=str,
        help="该音频的歌曲名（可选，用于标记歌名，建议添加）",
    )
    single_group.add_argument(
        "-a",
        "--artist",
        type=str,
        help="演唱者或视频作者（可选，用于日志）",
    )
    single_group.add_argument(
        "--album",
        type=str,
        help="该音频出自于的专辑（可选，用于日志）",
    )

    return parser.parse_args()


def main():
    # 解析命令行参数
    args = parse_arguments()

    # 根据命令行参数准备待下载的视频列表
    video_list = utils.prepare_video_list(args)
    if not video_list:
        return

    # 执行批量下载
    all_results, failed_downloads = dowload.batch_download(
        video_list, args.output_dir, args.sleep
    )

    # 保存失败记录、清理临时文件、打印汇总
    utils.save_failed_downloads(failed_downloads)
    utils.cleanup_temp_files()
    utils.print_download_summary(all_results, failed_downloads)


if __name__ == "__main__":
    main()

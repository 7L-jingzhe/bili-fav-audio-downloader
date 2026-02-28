# -*- coding: utf-8 -*-
import requests
import os
import time
import sys
import io
import re
import json

# 修改系统标准输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    # 移除Windows系统非法字符
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
    filename = re.sub(illegal_chars, "", filename)
    # 替换连续空格为单个下划线
    filename = re.sub(r"\s+", " ", filename).strip()
    # 截断过长文件名（保留前100个字符）
    return filename[:100]


def get_collection_list(fid, pn=1, ps=20):
    """获取收藏夹内容"""
    api_url = "https://api.bilibili.com/x/v3/fav/resource/list"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Cookie": "buvid3=94DA5EBD-D516-81EF-CA13-0582003C9DD402651infoc; b_nut=1768490002; _uuid=FE9DD3F2-C28F-D9D7-94BA-E1078891691FF02656infoc; buvid_fp=1df040c6c2a287c9be4e4b4c289979d8; buvid4=7B75541A-3B90-E24F-9574-BAC545E5AEEF05029-026011523-ffPaCJUcc4Oq+VMxJ5mtVA%3D%3D; home_feed_column=5; browser_resolution=1707-898; CURRENT_QUALITY=0; rpdid=|(um|kJ)ku)|0J'u~Y))kkk)l; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; SESSDATA=5a037c72%2C1787758471%2C98492%2A21CjCghIWhBlBcvknOnu9wo5RwhIQwUyjqX_wLneLonFvZLiihUXLaVa5QLpYoBh0gpCISVm9LVHZBbU9FenpQdUtOeUlxa3RPbGx1VWRNS0hReHBlYktkOXdQSjdyM2VfZWo2V1p4RnFqRmM1RHlPY0toSnhzUm9yYzhGRC1MMVBPY3hBc0ZCQl9BIIEC; bili_jct=4b03581e5c689ec8859ef05c030b217b; DedeUserID=521470199; DedeUserID__ckMd5=cc363a6c1af92a42; bp_t_offset_521470199=1174106941895475200; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzI0NjU2NzcsImlhdCI6MTc3MjIwNjQxNywicGx0IjotMX0.9NDwdIt0mAXGw1qoFB2YzV8rFox4MrTPhKl0GciEKXU; bili_ticket_expires=1772465617; sid=5pjvufj6; CURRENT_FNVAL=4048; b_lsid=3B605715_19C9FBE100C",
    }

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

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.encoding = "utf-8"
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            print(f"API错误: {data['message']}")
            return None

        return data["data"]

    except Exception as e:
        print(f"请求失败: {str(e)}")
        return None


def get_video_detail(bvid):
    """获取视频详细信息"""
    api_url = "https://api.bilibili.com/x/web-interface/view"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Cookie": "testcookie=1; buvid3=B788C82E-EAFB-C99E-709A-2768B48A6EB386628infoc; b_nut=1741305886; _uuid=816C3A7C-D693-347C-EC910-F134D8D4169986527infoc; buvid_fp=1d9c539346d4d1028695dc8b68404112; enable_web_push=DISABLE; enable_feed_channel=ENABLE; home_feed_column=5; browser_resolution=1536-695; CURRENT_FNVAL=2000; __at_once=15818156040200231743; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTY4Njk1MDAsImlhdCI6MTc1NjYxMDI0MCwicGx0IjotMX0.p-lf7un_ZCCOOrEBKA-IMW3i-KgBRPNaE9D1iJCOvhc; bili_ticket_expires=1756869440; b_lsid=791097E32_198FE220FFB; SESSDATA=7159445d%2C1772162703%2Ce7d4f%2A82CjBLFPDdtSc8GjXGuNyvK7lPPGVeInMjebhH4pdpJ1saUEZOkKckWUYWkGAqM9X-m4QSVm1ia0pjZ3lFWHBydm9ONU1rMGVoczRSTHc1WVg4clFXUHY2NGI5NGE0d0l2SXhTdjlaTk1ieHVYUHBlV2xsY1A2YkFvSTZvWFJhUldjd3dEcG9fRlNnIIEC; bili_jct=bdb4d270e043c38cb69c1b09353dc020; DedeUserID=521470199; DedeUserID__ckMd5=cc363a6c1af92a42; sid=4tnhh4dr; theme-tip-show=SHOWED; buvid4=89C6243F-3AB3-A30C-8D98-A6E4E752BAC187593-025030700-r53TzGzB/7S74vQ4vcm9Cg%3D%3D",
    }

    params = {
        "bvid": bvid,
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.encoding = "utf-8"
        response.raise_for_status()
        data = response.json()

        if data["code"] != 0:
            print(f"获取视频详情失败 {bvid}: {data['message']}")
            return None

        return data["data"]

    except Exception as e:
        print(f"请求视频详情失败 {bvid}: {str(e)}")
        return None


def get_video_tags(bvid):
    """获取视频的真实标签列表"""
    api_url = "https://api.bilibili.com/x/tag/archive/tags"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": "testcookie=1; buvid3=B788C82E-EAFB-C99E-709A-2768B48A6EB386628infoc; b_nut=1741305886; _uuid=816C3A7C-D693-347C-EC910-F134D8D4169986527infoc; buvid_fp=1d9c539346d4d1028695dc8b68404112; enable_web_push=DISABLE; enable_feed_channel=ENABLE; home_feed_column=5; browser_resolution=1536-695; CURRENT_FNVAL=2000; __at_once=15818156040200231743; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTY4Njk1MDAsImlhdCI6MTc1NjYxMDI0MCwicGx0IjotMX0.p-lf7un_ZCCOOrEBKA-IMW3i-KgBRPNaE9D1iJCOvhc; bili_ticket_expires=1756869440; b_lsid=791097E32_198FE220FFB; SESSDATA=7159445d%2C1772162703%2Ce7d4f%2A82CjBLFPDdtSc8GjXGuNyvK7lPPGVeInMjebhH4pdpJ1saUEZOkKckWUYWkGAqM9X-m4QSVm1ia0pjZ3lFWHBydm9ONU1rMGVoczRSTHc1WVg4clFXUHY2NGI5NGE0d0l2SXhTdjlaTk1ieHVYUHBlV2xsY1A2YkFvSTZvWFJhUldjd3dEcG9fRlNnIIEC; bili_jct=bdb4d270e043c38cb69c1b09353dc020; DedeUserID=521470199; DedeUserID__ckMd5=cc363a6c1af92a42; sid=4tnhh4dr; theme-tip-show=SHOWED; buvid4=89C6243F-3AB3-A30C-8D98-A6E4E752BAC187593-025030700-r53TzGzB/7S74vQ4vcm9Cg%3D%3D",
    }
    params = {"bvid": bvid}
    try:
        resp = requests.get(api_url, headers=headers, params=params, timeout=10)
        resp.encoding = "utf-8"
        data = resp.json()
        if data["code"] == 0 and data["data"]:
            # 返回标签名称列表
            return [tag["tag_name"] for tag in data["data"]]
    except Exception as e:
        print(f"获取标签失败 {bvid}: {e}")
    return []  # 失败则返回空列表


def save_video_list_json(video_info_list, filename="bvid_list.json"):
    """保存视频信息为JSON格式"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(video_info_list, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(video_info_list)} 个视频信息到 {os.path.abspath(filename)}")


def main():
    # 获取fid
    fid = "3623731999"

    # 初始化参数
    video_info_list = []
    page = 1
    has_more = True

    # 开始爬取
    while has_more:
        print(f"正在获取第 {page} 页...")
        data = get_collection_list(fid, pn=page)

        if not data or not data.get("medias"):
            break

        # 提取视频信息
        for media in data["medias"]:
            if media["type"] == 2:  # 只处理视频类型
                bvid = media["bv_id"]
                print(f"正在获取视频详情: {bvid}")

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
                        f"已获取: {video_info['bvid']} - {video_info['title']} - 作者: {video_info['author']}"
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
                        f"已保存基本信息: {video_info['bvid']} - {video_info['title']}"
                    )

                time.sleep(3)  # 请求详情页的延迟

        # 检查是否还有下一页
        has_more = data["has_more"]
        page += 1
        time.sleep(3)  # 翻页延迟

    # 保存结果
    if video_info_list:
        save_video_list_json(video_info_list, filename="bvid_list.json")

        # 同时保存一个精简的文本版本（仅BV号，方便其他用途）
        with open("bvid_only.txt", "w", encoding="utf-8") as f:
            for info in video_info_list:
                f.write(f"{info['bvid']}\n")
        print(f"已保存 {len(video_info_list)} 个BV号到 bvid_only.txt")
    else:
        print("未找到任何视频")


if __name__ == "__main__":
    main()

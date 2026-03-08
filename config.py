# -*- coding: utf-8 -*-
"""
配置文件 - 存储需要经常修改的常量
"""

# Cookie配置
COOKIE = "buvid3=94DA5EBD-D516-81EF-CA13-0582003C9DD402651infoc; b_nut=1768490002; _uuid=FE9DD3F2-C28F-D9D7-94BA-E1078891691FF02656infoc; buvid_fp=1df040c6c2a287c9be4e4b4c289979d8; buvid4=7B75541A-3B90-E24F-9574-BAC545E5AEEF05029-026011523-ffPaCJUcc4Oq+VMxJ5mtVA%3D%3D; home_feed_column=5; browser_resolution=1707-898; CURRENT_QUALITY=0; rpdid=|(um|kJ)ku)|0J'u~Y))kkk)l; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; DedeUserID=521470199; DedeUserID__ckMd5=cc363a6c1af92a42; SESSDATA=e1bc7343%2C1788531961%2C3d5a2%2A32CjC8TDndh_m_DTAV-uhv-Ekzl9stzSHXG9lmq1E0nBSjAIjfXbyNiCS_O4_wmdct1HUSVjZMX2NLU0N2eGhDaGtzbU93OUx1ejRfOWFxVHNoNy1MU28yenFlRHR0R2k2NWI5QVRXZFNLcm1uZWxVbmhrMXhUcVB5cGt0TXBMYktOc0pGblY0OS1RIIEC; bili_jct=a951c7d9af801ac10c83b10c3c22401c; sid=6uti0x06; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzMyNDA3NDUsImlhdCI6MTc3Mjk4MTQ4NSwicGx0IjotMX0.BVgTEo0ZIkS0E3Ceun-TxFxSoUH0jZj3EBCAtb_DJ_Y; bili_ticket_expires=1773240685; CURRENT_FNVAL=4048; bp_t_offset_521470199=1177438835789791232; b_lsid=9C24E529_19CCE24A296"

# User-Agent配置
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
# API请求配置
API_CONFIG = {
    "base_delay": 3,  # 基础请求延迟（秒）
    "timeout": 10,  # 请求超时时间（秒）
    "max_retries": 3,  # 最大重试次数
}

# 收藏夹默认ID
DEFAULT_FAVORITE_ID = "3623731999"

# 输出文件配置
OUTPUT_CONFIG = {
    "default_json": "bvid_list.json",
    "default_txt": "bvid_only.txt",
    "max_filename_length": 100,
}


def get_headers():
    """
    获取请求头

    Returns:
        dict: 包含User-Agent和Cookie的请求头字典
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Cookie": COOKIE,
    }
    return headers

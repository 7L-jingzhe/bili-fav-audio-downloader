# B站收藏夹音频批量下载工具

本项目用于从B站收藏夹中批量提取视频信息，并通过 `yt-dlp` 将视频转换为 MP3 音频，同时自动嵌入标题、艺术家、专辑等元数据。适用于备份音乐类收藏、制作个人音乐库等场景。

## 功能特性

- **收藏夹信息爬取**：从指定B站收藏夹获取所有视频的BV号、标题、作者、描述、标签等信息，保存为JSON文件（`get_bvid.py`）。
- **AI辅助元数据清洗**：提供 `提示词.txt` 示例，可利用AI（如ChatGPT）将原始视频标题、描述等自动解析为准确的歌名、歌手和专辑名，生成标准化的下载列表。
- **灵活的下载控制**：支持通过命令行参数指定输入文件、输出目录、下载范围、间隔时间，并可重试失败的下载。
- **音频提取与元数据嵌入**：调用 `yt-dlp` 提取最佳音质的音频，自动嵌入标题、艺术家、专辑信息。
- **自动清理临时文件**：下载完成后自动清理 `.jpg`、`.webp`、`.part` 等临时文件。
- **失败重试机制**：下载失败的视频信息会保存到 `failed_downloads.json`，可随时通过 `-r` 参数重试。
- **详细日志**：错误信息记录到 `download_error.log`，便于排查问题。
- **模块化设计**：代码结构清晰，主程序仅负责流程调度，核心逻辑分别封装在 `core.py` 和 `dowload.py` 中，所有可配置项集中在 `config.py`，易于维护和扩展。

## 依赖

- Python 3.6+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)（用于下载和转换音频）
- [FFmpeg](https://ffmpeg.org/)（yt-dlp 需要它处理音频和嵌入封面）
- Python 包：`requests`

## 安装

### 1. 克隆或下载本项目

```bash
git clone https://github.com/7L-jingzhe/bili-fav-audio-downloader.git
cd bili-fav-audio-downloader
```

### 2. 安装Python依赖

```bash
pip install requests
```

### 3. 安装 yt-dlp

推荐使用 pip 安装：

```bash
pip install yt-dlp
```

或从 [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp/releases) 下载可执行文件并放入系统 PATH。

### 4. 安装 FFmpeg

- **Windows**: 下载 [FFmpeg](https://ffmpeg.org/download.html) 并将 `bin` 目录添加到系统 PATH。
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`（或其他对应包管理器）

安装后确保 `ffmpeg` 命令可在终端中使用。

## 配置文件

所有敏感信息和常用配置都集中在 `config.py` 中，您可以根据需要修改。

```python
# Cookie配置（登录B站后获取）
COOKIE = "你的B站Cookie"

# User-Agent配置
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."

# API请求配置（用于 get_bvid.py）
API_CONFIG = {
    "base_delay": 3,      # 基础请求延迟（秒）
    "timeout": 10,        # 请求超时时间（秒）
    "max_retries": 3,     # 最大重试次数
}

# 收藏夹默认ID
DEFAULT_FAVORITE_ID = "3623731999"

# get_bvid.py 输出文件配置
OUTPUT_CONFIG = {
    "default_json": "bvid_list.json",   # 默认JSON输出文件名
    "default_txt": "bvid_only.txt",     # 仅包含BV号的文本文件
    "max_filename_length": 100,         # 文件名最大长度
}

# 下载相关配置（用于 main.py 和 dowload.py）
DOWNLOAD_CONFIG = {
    "default_output_dir": "./music",        # 默认音频输出目录
    "default_album": "Bilibili音频",         # 默认专辑名
    "default_unknown_artist": "未知作者",     # 默认未知作者
    "temp_file_extensions": [               # 临时文件扩展名（清理用）
        ".jpg", ".jpeg", ".webp", ".png",
        ".part", ".temp", ".ytdl"
    ],
}

# 文件路径配置
FILE_CONFIG = {
    "failed_downloads_file": "failed_downloads.json",  # 失败记录文件
    "error_log_file": "download_error.log",            # 错误日志文件
    "default_input_json": "bvid.json",                 # main.py 默认输入文件
}

# yt-dlp 常见安装路径（可使用通配符 * 和 ~ 家目录）
YTDLP_COMMON_PATHS = [
    "~/.local/bin/yt-dlp",
    "~/AppData/Local/Programs/Python/Python*/Scripts/yt-dlp.exe",
    "C:/Python*/Scripts/yt-dlp.exe",
    "C:/Program Files/Python*/Scripts/yt-dlp.exe",
]
```

### 获取收藏夹ID（fid）

1. 打开B站，进入你想要下载的收藏夹页面。
2. 浏览器地址栏中的 URL 类似：`https://space.bilibili.com/123456789/favlist?fid=3623731999`，`fid=` 后面的数字即为收藏夹ID。

### 获取Cookie

1. 登录B站网页版。
2. 打开浏览器开发者工具（F12），切换到“网络”（Network）标签。
3. 刷新页面，找到任意一个请求（如 `favlist` 相关的），在请求头中找到 `Cookie` 字段，复制其值。
4. 打开 `config.py`，将 `COOKIE` 的值替换为你的Cookie（注意保留引号）。

## 使用方法

本项目由两个核心脚本组成：`get_bvid.py` 负责爬取收藏夹信息，`main.py` 负责下载音频。推荐使用AI辅助处理元数据，以获得更准确的歌名和歌手。

### 第一步：获取收藏夹视频信息

运行 `get_bvid.py` 爬取指定收藏夹的所有视频信息，生成两个文件：
- `bvid_list.json`：包含视频的BV号、标题、作者、描述、标签等原始信息。
- `bvid_only.txt`：仅包含BV号列表，每行一个。

#### 参数说明

```bash
python get_bvid.py [-n NUM] [-f FID] [-o OUTPUT] [-d DELAY]
```

| 参数 | 说明 |
|------|------|
| `-n, --num` | 要爬取的视频数量，不指定则爬取全部 |
| `-f, --fid` | 收藏夹ID，默认使用 `config.py` 中的 `DEFAULT_FAVORITE_ID` |
| `-o, --output` | 输出文件名（JSON），默认为 `bvid_list.json` |
| `-d, --delay` | 请求延迟秒数，默认使用 `config.py` 中的 `base_delay` |

#### 使用示例

```bash
# 爬取全部视频（使用默认收藏夹）
python get_bvid.py

# 爬取前10个视频
python get_bvid.py -n 10

# 爬取指定收藏夹的前5个视频，保存为 my_fav.json
python get_bvid.py -n 5 -f 1234567890 -o my_fav.json
```

> **注意**：请合理设置请求延迟，避免被B站封IP。

### 第二步：（可选）使用AI辅助清洗元数据

`get_bvid.py` 生成的 `bvid_list.json` 中的标题可能包含大量额外文字（如“超燃翻唱”、“片尾曲”等），直接用作歌曲名可能不够准确。本项目提供了 `提示词.txt`，其中包含多个示例，展示如何利用AI（如deepseek）将原始信息转换为包含准确 `title`、`artist`、`album` 的JSON格式。

您可以将 `bvid_list.json` 的内容作为输入，配合 `提示词.txt` 中的指令，让AI自动生成标准化后的下载列表，例如：

```json
[
  {
    "bvid": "BV16H4y1Q7NS",
    "title": "九九八十一",
    "artist": "迷柚mio原宿宿Yado"
  },
  {
    "bvid": "BV1ZR5PzwEok",
    "title": "千秋迭梦",
    "artist": "镜予歌&陈亦洺&尚辰",
    "album": "千秋迭梦 —— 《二哈和他的白猫师尊》燃晚同人歌"
  }
]
```

将AI处理后的JSON保存为 `bvid.json`（或任意名称），供下一步使用。

### 第三步：批量下载音频

`main.py` 是下载主程序，它读取上一步准备好的JSON文件，调用 `yt-dlp` 下载音频。

#### 参数说明

```bash
python main.py [-i INPUT] [-o OUTPUT_DIR] [-r] [-s SLEEP] [--start START] [--end END]
```

| 参数 | 说明 |
|------|------|
| `-i, --input` | 输入的视频信息文件（默认：`bvid.json`） |
| `-o, --output-dir` | 音频文件输出目录（默认：`./music`） |
| `-r, --retry` | 重试失败的下载（从 `failed_downloads.json` 读取） |
| `-s, --sleep` | 下载间隔秒数（默认：3） |
| `--start` | 从第几个视频开始下载（默认：1） |
| `--end` | 下载到第几个视频结束（默认：全部） |

#### 单个视频下载

`main.py` 也支持直接通过BVID下载单个视频，并可手动指定标题、作者和专辑：

```bash
# 通过BVID下载，自动获取标题（但无法获取艺术家，日志中会显示未知作者）
python main.py --bvid BV1xx...

# 提供完整信息（标题、作者、专辑可选）
python main.py --bvid BV1xx... --title "歌曲名" --artist "歌手名" --album "专辑名"
```

#### 使用示例

```bash
# 基本用法：使用默认配置下载（从 bvid.json 读取）
python main.py

# 从指定文件加载视频列表
python main.py -i bvid_list.json

# 重试失败的下载
python main.py -r

# 设置下载间隔为5秒，输出到 ./my_music
python main.py -s 5 -o ./my_music

# 下载第10到第20个视频
python main.py --start 10 --end 20

# 组合使用
python main.py -i custom.json -s 2 -o ./downloads
```

### 第四步：查看结果

- 成功下载的MP3文件位于指定的输出目录（默认 `./music`），**文件名格式为 `BV号.mp3`**（例如 `BV16H4y1Q7NS.mp3`），以避免文件名过长或包含非法字符。
- 下载失败的视频信息会记录在 `download_error.log` 中。
- 所有失败视频的原始信息会被保存到 `failed_downloads.json`，便于后续使用 `-r` 参数重试。

#### 下载完成汇总示例

```
============================================================
 下载完成！结果汇总：
============================================================
 总计: 50 个视频
  成功: 48 个
  失败: 2 个
============================================================

📁 失败的视频信息已保存至: failed_downloads.json
```

## 文件说明

| 文件 | 作用 |
|------|------|
| `config.py` | 配置文件，存储Cookie、User-Agent、API参数、下载路径等所有可调整项 |
| `get_bvid.py` | 从B站收藏夹API获取视频信息，生成包含原始数据的JSON文件 |
| `提示词.txt` | 辅助文件，展示如何利用AI将原始信息转换为标准化的下载列表 |
| `dowload.py` | 封装 `yt-dlp` 下载逻辑，支持单个和批量下载，并处理元数据嵌入 |
| `core.py` | 辅助业务逻辑：加载数据、保存失败记录、清理临时文件、打印汇总、准备视频列表等 |
| `main.py` | 主程序，解析命令行参数并调度下载流程 |
| `bvid_list.json` | （生成文件）由 `get_bvid.py` 生成的原始视频信息 |
| `bvid.json` | （推荐）经过AI清洗后的下载列表，供 `main.py` 默认读取 |
| `failed_downloads.json` | （自动生成）记录所有下载失败的视频信息 |
| `download_error.log` | （自动生成）文本日志，记录每次下载失败的错误详情 |
| `music/` | （自动生成）默认的MP3文件存放目录 |

## 常见问题

### Q: 为什么下载后MP3文件没有封面？
A: `yt-dlp` 默认会尝试嵌入封面（`--embed-thumbnail`），但有时封面提取失败。你可以检查日志是否有相关警告。

### Q: 如何仅下载部分视频？
A: 有两种方式：
1. 使用 `get_bvid.py` 的 `-n` 参数只爬取指定数量的视频。
2. 使用 `main.py` 的 `--start` 和 `--end` 参数指定下载范围。

### Q: 运行 `get_bvid.py` 时报错 `-101` 或 `-400`？
A: 这通常表示Cookie失效或未正确设置。请重新获取最新Cookie并更新 `config.py` 中的 `COOKIE` 值。

### Q: 下载过程中断后如何继续？
A: 有两种方式：
1. 再次运行 `main.py`，已下载成功的文件不会被覆盖（yt-dlp默认行为）。
2. 使用 `python main.py -r` 重试之前失败的下载。

### Q: `main.py` 支持哪些输入文件格式？
A: `main.py` 需要JSON格式的文件，每个对象应包含 `bvid`、`title`、`artist` 字段，可选的 `album` 字段。`get_bvid.py` 生成的原始文件使用 `author` 字段，建议通过AI清洗或手动转换为 `artist` 字段后使用。

### Q: 如何自定义专辑名称？
A: 在输入JSON中为每个视频添加 `album` 字段，程序会自动将其嵌入音频元数据。如果不提供，默认使用配置中的 `default_album`（“Bilibili音频”）。

### Q: 为什么下载的文件名只有BV号，不包含标题？
A: 为避免文件名过长或包含非法字符导致保存失败，程序统一使用 `BV号.mp3` 作为文件名。标题信息仍会嵌入到音频文件的元数据中，音乐播放器通常会显示正确的标题。

### Q: 如何获取更准确的歌名和歌手？
A: 利用 `提示词.txt` 中的示例，将原始视频信息输入AI（如ChatGPT），AI可以自动解析出准确的歌曲名、歌手和专辑名，生成标准化的JSON文件供 `main.py` 使用。这是本项目的推荐工作流。

## 许可证

[MIT License](LICENSE)

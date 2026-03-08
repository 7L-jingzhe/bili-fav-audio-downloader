# B站收藏夹音频批量下载工具

本项目用于从B站收藏夹中批量提取视频信息，并使用 `yt-dlp` 下载音频（MP3格式），同时自动嵌入标题、艺术家、专辑等元数据。适用于备份音乐类收藏、制作个人音乐库等场景。

## 功能特性

- 从指定B站收藏夹获取所有视频的BV号、标题、作者、描述、标签等信息，保存为JSON文件。
- **支持命令行参数**：可指定爬取数量、收藏夹ID、输出文件、请求延迟等。
- **配置分离**：Cookie、User-Agent等敏感信息独立存储在 `config.py` 中，便于管理和更新。
- **自动重试机制**：API请求失败时自动重试，提高爬取成功率。
- 支持断点续传：下载失败的视频信息会自动保存，方便重试。
- **灵活的主程序参数**：可指定输入文件、输出目录、下载范围、重试失败任务等。
- 调用 `yt-dlp` 提取音频，质量设为最佳，并嵌入元数据（标题、艺术家、专辑）。
- 自动清理下载过程中产生的临时文件（.jpg, .webp, .part等）。
- 详细的日志记录，便于排查失败原因。

## 依赖

- Python 3.6 或更高版本
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

或使用系统包管理器（如 `brew`、`apt`），或从 [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp/releases) 下载可执行文件并放入系统 PATH。

### 4. 安装 FFmpeg

- **Windows**: 下载 [FFmpeg](https://ffmpeg.org/download.html) 并将 `bin` 目录添加到系统 PATH。
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`（或其他对应包管理器）

安装后确保 `ffmpeg` 命令可在终端中使用。

## 配置文件说明

### config.py

所有需要经常修改的配置都集中在 `config.py` 文件中：

```python
# Cookie配置（登录B站后获取）
COOKIE = "你的B站Cookie"

# User-Agent配置
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."

# API请求配置
API_CONFIG = {
    "base_delay": 3,      # 基础请求延迟（秒）
    "timeout": 10,        # 请求超时时间（秒）
    "max_retries": 3,     # 最大重试次数
}

# 收藏夹默认ID
DEFAULT_FAVORITE_ID = "3623731999"

# 输出文件配置
OUTPUT_CONFIG = {
    "default_json": "bvid_list.json",
    "default_txt": "bvid_only.txt",
    "max_filename_length": 100,
}
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

### 第一步：获取收藏夹视频信息

运行 `get_bvid.py`，它会爬取收藏夹所有视频的详细信息，并生成两个文件：

- `bvid_list.json`：包含视频的BV号、标题、作者、描述、标签等完整信息。
- `bvid_list_bvid_only.txt`：仅包含BV号列表，每行一个。

#### 命令行参数说明

```bash
python get_bvid.py [-n NUM] [-f FID] [-o OUTPUT] [-d DELAY]
```

| 参数 | 说明 |
|------|------|
| `-n, --num` | 要爬取的视频数量，不指定则爬取全部 |
| `-f, --fid` | 收藏夹ID，默认使用config.py中的DEFAULT_FAVORITE_ID |
| `-o, --output` | 输出文件名，默认为bvid_list.json |
| `-d, --delay` | 请求延迟秒数，默认为config.py中的base_delay |

#### 使用示例

```bash
# 爬取全部视频（使用默认配置）
python get_bvid.py

# 爬取前10个视频
python get_bvid.py -n 10

# 爬取前20个视频，延迟5秒
python get_bvid.py -n 20 -d 5

# 爬取指定收藏夹的前5个视频
python get_bvid.py -n 5 -f 1234567890 -o my_fav.json
```

> **注意**：由于B站API限制，请合理设置请求延迟，避免被封IP。

### 第二步：批量下载音频

`main.py` 是下载主程序，支持多种灵活的下载方式。

#### 命令行参数说明

```bash
python main.py [-i INPUT] [-o OUTPUT_DIR] [-r] [-s SLEEP] [--start START] [--end END]
```

| 参数 | 说明 |
|------|------|
| `-i, --input` | 输入的视频信息文件（默认：bvid.json） |
| `-o, --output-dir` | 音频文件输出目录（默认：./music） |
| `-r, --retry` | 重试失败的下载（从 failed_downloads.json 读取） |
| `-s, --sleep` | 下载间隔秒数（默认：3） |
| `--start` | 从第几个视频开始下载（默认：1） |
| `--end` | 下载到第几个视频结束（默认：全部） |

#### 使用示例

```bash
# 基本用法 - 使用默认配置下载（从bvid.json读取）
python main.py

# 从指定文件加载视频列表
python main.py -i bvid_list.json

# 重试失败的下载
python main.py -r

# 设置下载间隔为5秒
python main.py -s 5

# 指定输出目录
python main.py -o ./my_music

# 下载第10到第20个视频
python main.py --start 10 --end 20

# 组合使用多个参数
python main.py -i custom.json -s 2 -o ./downloads
```

#### 下载过程输出示例

```
🎵 开始批量下载音频...
📁 输入文件: bvid.json
💾 输出目录: ./music
⏱️  下载间隔: 3秒
📊 总共 50 个视频
============================================================

📌 处理进度: 1/50
🎬 当前视频: 九九八十一 - 迷柚mio原宿宿Yado
✅ 下载完成
⏳ 等待 3秒后继续下一个...

📌 处理进度: 2/50
🎬 当前视频: 权御天下 - 某主播
✅ 下载完成
⏳ 等待 3秒后继续下一个...
```

### 第三步：查看结果

- 成功下载的MP3文件位于指定的输出目录（默认为 `./music`），文件名格式为 `标题-BV号.mp3`。
- 下载失败的视频信息会记录在 `download_error.log` 文件中。
- 所有失败视频的原始信息会被保存到 `failed_downloads.json`，便于后续使用 `-r` 参数重试。

#### 下载完成汇总示例

```
============================================================
📊 下载完成！结果汇总：
============================================================
 总计: 50 个视频
 ✅ 成功: 48 个
 ❌ 失败: 2 个
============================================================

📁 失败的视频信息已保存至: failed_downloads.json
🧹 已清理 3 个临时文件
```

## 文件说明

| 文件 | 作用 |
|------|------|
| `config.py` | 配置文件，存储Cookie、User-Agent、API请求参数等 |
| `get_bvid.py` | 从B站收藏夹API获取视频信息，支持命令行参数 |
| `dowload.py` | 封装 `yt-dlp` 下载逻辑，处理元数据嵌入 |
| `main.py` | 主程序，读取视频列表并调用下载模块，支持命令行参数 |
| `提示词.txt` | 辅助文件，展示了如何利用AI提取更准确的歌名和歌手（非必需） |
| `bvid_list.json` | 由 `get_bvid.py` 生成，包含所有视频的原始信息 |
| `bvid_list_bvid_only.txt` | 仅包含BV号的文本文件 |
| `bvid.json` | `main.py` 默认读取的下载列表，建议从 `bvid_list.json` 复制或重命名 |
| `failed_downloads.json` | 自动生成，记录所有下载失败的视频原始信息，便于使用 `-r` 重试 |
| `download_error.log` | 文本日志，记录每次下载失败的错误详情 |
| `music/` | 默认的MP3文件存放目录 |

## 注意事项

1. **Cookie有效期**：B站Cookie会过期，如果出现API返回错误（如`-101`或`-400`），请重新获取Cookie并更新 `config.py`。
2. **请求频率**：代码已设置延迟和重试机制，避免被B站封IP。如果收藏夹很大，下载过程可能持续较长时间。
3. **yt-dlp和FFmpeg**：确保两者正确安装且可在命令行调用。如果 `yt-dlp` 不在PATH中，`dowload.py` 会尝试在常见路径查找，但仍建议将其加入PATH。
4. **专辑元数据**：如果从描述中能提取出专辑信息（如示例所示），可以手动补充到 `bvid.json` 中，程序会自动嵌入。否则默认使用“Bilibili音频”。
5. **标题清理**：文件名中的非法字符（如 `\ / : * ? " < > |`）会被自动移除，避免保存失败。

## 常见问题

### Q: 为什么下载后MP3文件没有封面？
A: `yt-dlp` 默认会尝试嵌入封面（`--embed-thumbnail`），但有时封面提取失败。你可以检查日志是否有相关警告。

### Q: 如何仅下载部分视频？
A: 有两种方式：
1. 使用 `get_bvid.py` 的 `-n` 参数只爬取指定数量的视频
2. 使用 `main.py` 的 `--start` 和 `--end` 参数指定下载范围

### Q: 运行 `get_bvid.py` 时报错 `-101` 或 `-400`？
A: 这通常表示Cookie失效或未正确设置。请重新获取最新Cookie并更新 `config.py` 中的 `COOKIE` 值。

### Q: 下载过程中断后如何继续？
A: 有两种方式：
1. 再次运行 `main.py`，已下载成功的视频会被跳过（因为yt-dlp默认不会覆盖已存在的文件）
2. 使用 `python main.py -r` 重试之前失败的下载

### Q: 如何调整API请求的延迟和重试次数？
A: 在 `config.py` 的 `API_CONFIG` 中修改 `base_delay` 和 `max_retries` 的值即可。

### Q: `main.py` 支持哪些输入文件格式？
A: `main.py` 需要JSON格式的文件，包含bvid、title、artist等字段。`get_bvid.py` 生成的 `bvid_list.json` 符合这个格式要求。

## 贡献

欢迎提交Issue和Pull Request。如果你有更好的元数据提取方法（如利用AI分析标题和描述），也欢迎分享。

## 许可证

[MIT License](LICENSE)
```

## 主要更新内容：

1. **更新了主程序命令行参数**：精简为6个核心参数（`-i`, `-o`, `-r`, `-s`, `--start`, `--end`）
2. **添加了更详细的使用示例**：每个参数都有对应的示例
3. **更新了下载过程的输出示例**：使用新的带emoji的输出格式
4. **添加了下载完成汇总示例**：展示结果统计和临时文件清理
5. **更新了常见问题**：增加了关于主程序参数和重试机制的问题
6. **优化了文件说明**：更清晰地说明了各文件的作用

现在README与最新的代码完全保持一致！

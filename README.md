# B站收藏夹音频批量下载工具

本项目用于从B站收藏夹中批量提取视频信息，并使用 `yt-dlp` 下载音频（MP3格式），同时自动嵌入标题、艺术家、专辑等元数据。适用于备份音乐类收藏、制作个人音乐库等场景。

## 功能特性

- 从指定B站收藏夹获取所有视频的BV号、标题、作者、描述、标签等信息，保存为JSON文件。
- 支持断点续传：下载失败的视频信息会自动保存，方便重试。
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

## 配置

### 获取收藏夹ID（fid）

1. 打开B站，进入你想要下载的收藏夹页面。
2. 浏览器地址栏中的 URL 类似：`https://space.bilibili.com/123456789/favlist?fid=3623731999`，`fid=` 后面的数字即为收藏夹ID。

### 修改Cookie

本项目需要携带B站的登录Cookie才能访问收藏夹API。请按以下步骤获取并更新代码中的Cookie：

1. 登录B站网页版。
2. 打开浏览器开发者工具（F12），切换到“网络”（Network）标签。
3. 刷新页面，找到任意一个请求（如 `favlist` 相关的），在请求头中找到 `Cookie` 字段，复制其值。
4. 打开 `get_bvid.py`，找到 `headers` 中的 `Cookie` 字段，替换为你的Cookie（注意保留引号）。

### 修改收藏夹ID

在 `get_bvid.py` 中找到变量 `fid`，将其值改为你的收藏夹ID。

```python
fid = "你的收藏夹ID"   # 例如 "3623731999"
```

### （可选）调整请求间隔

为避免触发B站反爬机制，代码中已加入 `time.sleep(3)` 延迟。如需要可自行修改。

## 使用方法

### 第一步：获取收藏夹视频信息

运行 `get_bvid.py`，它会爬取收藏夹所有视频的详细信息，并生成两个文件：

- `bvid_list.json`：包含视频的BV号、标题、作者、描述、标签等完整信息。
- `bvid_only.txt`：仅包含BV号列表，每行一个。

```bash
python get_bvid.py
```

> **注意**：由于B站API限制，如果收藏夹视频较多，可能需要较长时间。请耐心等待。

### 第二步：准备下载列表

`main.py` 默认读取 `bvid.json` 文件。你可以将 `bvid_list.json` 重命名为 `bvid.json`，或修改 `main.py` 中的文件名：

```python
# 修改 main.py 中的 load_bvid_data() 函数
with open("bvid.json", "r", encoding="utf-8") as f:   # 改为 "bvid_list.json"
```

### 第三步：批量下载音频

运行 `main.py`，程序会逐个下载并转换音频，保存在 `./music` 目录下。

```bash
python main.py
```

下载过程中的输出示例：

```
开始批量下载音频...
总共 50 个视频
==================================================

处理进度: 1/50
当前视频: 九九八十一 - 迷柚mio原宿宿Yado
--------------------------------------------------
开始下载: BV16H4y1Q7NS
标题: 九九八十一
歌手: 迷柚mio原宿宿Yado
正在下载并转换...
 下载成功！
文件已保存: ./music/九九八十一-BV16H4y1Q7NS.mp3
✅ 下载完成
间隔3秒后继续下一个...
...
```

### 第四步：查看结果

- 成功下载的MP3文件位于 `./music` 目录，文件名格式为 `标题-BV号.mp3`。
- 下载失败的视频信息会记录在 `download_error.log` 文件中。
- 所有失败视频的原始信息会被保存到 `failed_downloads.json`，便于后续重试。

## 文件说明

| 文件 | 作用 |
|------|------|
| `get_bvid.py` | 从B站收藏夹API获取视频信息，生成JSON列表。 |
| `dowload.py` | 封装 `yt-dlp` 下载逻辑，处理元数据嵌入。 |
| `main.py` | 主程序，读取视频列表并调用下载模块，管理失败重试和日志。 |
| `提示词.txt` | 辅助文件，展示了如何利用AI提取更准确的歌名和歌手（非必需）。 |
| `bvid_list.json` | 由 `get_bvid.py` 生成，包含所有视频的原始信息。 |
| `bvid.json` | `main.py` 默认读取的下载列表，建议从 `bvid_list.json` 复制或重命名。 |
| `failed_downloads.json` | 自动生成，记录所有下载失败的视频原始信息，便于重试。 |
| `download_error.log` | 文本日志，记录每次下载失败的错误详情。 |
| `music/` | 下载的MP3文件存放目录。 |

## 注意事项

1. **Cookie有效期**：B站Cookie会过期，如果出现API返回错误（如`-101`或`-400`），请重新获取Cookie并更新。
2. **请求频率**：代码已设置3秒延迟，避免被B站封IP。如果收藏夹很大，下载过程可能持续较长时间。
3. **yt-dlp和FFmpeg**：确保两者正确安装且可在命令行调用。如果 `yt-dlp` 不在PATH中，`dowload.py` 会尝试在常见路径查找，但仍建议将其加入PATH。
4. **专辑元数据**：如果从描述中能提取出专辑信息（如示例所示），可以手动补充到 `bvid.json` 中，程序会自动嵌入。否则默认使用“Bilibili音频”。
5. **标题清理**：文件名中的非法字符（如 `\ / : * ? " < > |`）会被自动移除，避免保存失败。

## 常见问题

### Q: 为什么下载后MP3文件没有封面？
A: `yt-dlp` 默认会尝试嵌入封面（`--embed-thumbnail`），但有时封面提取失败。你可以检查日志是否有相关警告。

### Q: 如何仅下载部分视频？
A: 可以手动编辑 `bvid.json`，只保留想下载的视频条目，或使用 `bvid_only.txt` 配合其他工具。

### Q: 运行 `get_bvid.py` 时报错 `-101` 或 `-400`？
A: 这通常表示Cookie失效或未正确设置。请重新获取最新Cookie并替换。

### Q: 下载过程中断后如何继续？
A: 再次运行 `main.py` 即可，已经下载成功的视频会被跳过（因为yt-dlp默认不会覆盖已存在的文件）。如果希望重新下载，请先删除 `music` 目录下对应的文件。

## 贡献

欢迎提交Issue和Pull Request。如果你有更好的元数据提取方法（如利用AI分析标题和描述），也欢迎分享。

## 许可证

[MIT License](LICENSE)

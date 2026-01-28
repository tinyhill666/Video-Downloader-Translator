---
description: 使用 yt-dlp 下载视频和字幕
argument-hint: <URL> [选项]
allowed-tools: [Bash, Read, Write]
---

# yt-dlp 视频下载命令

帮助用户使用 yt-dlp 下载视频和字幕。

## 参数

- `$ARGUMENTS`: 视频 URL 和选项

## 常用命令

### 下载最佳质量视频（带字幕，自动重命名）
使用 `-o` 参数自动添加 Season 和 Episode 信息（如果可用）：
```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --write-subs --write-auto-subs \
  --sub-langs "zh.*,en.*,ja.*" \
  --embed-subs \
  -o "%(series)s S%(season_number)02dE%(episode_number)02d %(title)s.%(ext)s" \
  "URL"
```
注意：如果视频源不提供 series/season/episode 元数据，yt-dlp 会报错或输出 NA。这种情况下，应回退到使用 `%(title)s.%(ext)s`，或者让用户手动指定。

### 仅下载字幕（带 SxxExx）
```bash
yt-dlp --write-subs --write-auto-subs \
  --sub-langs "zh.*,en.*,ja.*" \
  --skip-download \
  -o "%(series)s S%(season_number)02dE%(episode_number)02d %(title)s.%(ext)s" \
  "URL"
```

### 智能命名逻辑
在执行下载前，应先检查元数据或尝试构建文件名：
1. 优先尝试：`%(series)s S%(season_number)02dE%(episode_number)02d %(title)s.%(ext)s`
   - 适用于：Netflix, Disney+, BBC iPlayer 等剧集。
2. 回退方案：`%(title)s.%(ext)s`
   - 适用于：YouTube 单个视频，或元数据缺失的视频。

### 下载指定分辨率
```bash
yt-dlp -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]" \
  -o "%(title)s.%(ext)s" "URL"
```

### 列出可用格式
```bash
yt-dlp -F "URL"
```

## 执行流程

1. 确认用户需求（视频/字幕/分辨率）
2. 如果只提供 URL，默认下载最佳质量并嵌入字幕
3. 执行下载命令
4. 如果下载了字幕且用户需要翻译，使用 **subtitle-translation** skill 进行翻译

## 字幕翻译集成

下载字幕后，如果用户需要中英双语字幕：
1. 应用 subtitle-translation skill 的规则
2. 生成双语字幕，后缀使用 `.ZH&EN.srt`（例如：`VideoName.ZH&EN.srt`）
3. **保留** 原始英文字幕文件（后缀 `.en.srt`）
4. 优化中文布局（尽量单行）

## 注意事项

- 确保 yt-dlp 已安装：`brew install yt-dlp`
- 某些视频需要 cookies：`--cookies-from-browser safari/chrome`
- 更新 yt-dlp：`yt-dlp -U`

## 示例

```
/yt-dlp https://www.youtube.com/watch?v=xxx
/yt-dlp https://www.youtube.com/watch?v=xxx 仅字幕
/yt-dlp https://www.youtube.com/watch?v=xxx 1080p
```
---
description: 使用 yt-dlp 下载视频和字幕
argument-hint: <URL> [选项]
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# yt-dlp 视频下载命令

帮助用户使用 yt-dlp 下载视频和字幕。

## 参数

- `$ARGUMENTS`: 视频 URL 和选项

## 常用命令

### 下载最佳质量视频（带字幕）
```bash
# 有元数据的平台（Netflix, Disney+）
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --write-subs --write-auto-subs \
  --sub-langs "en.*" \
  -o "%(series)s.S%(season_number)02dE%(episode_number)02d.%(ext)s" \
  "URL"

# YouTube 等单视频
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --write-subs --write-auto-subs \
  --sub-langs "en.*" \
  -o "%(title)s.%(ext)s" \
  "URL"
```

### 仅下载字幕
```bash
yt-dlp --write-subs --write-auto-subs \
  --sub-langs "en.*" \
  --skip-download \
  -o "%(title)s.%(ext)s" \
  "URL"
```

### 智能命名逻辑

**目标格式**：`Show.Name.S01E01.ext`（点分隔，无剧集标题）

根据平台选择命名策略：

1. **Netflix, Disney+ 等**（元数据完整）：
   ```
   -o "%(series)s.S%(season_number)02dE%(episode_number)02d.%(ext)s"
   ```

2. **BBC iPlayer**（元数据缺失）：
   - `series`, `season_number`, `episode_number` 均为空
   - 需要逐集下载并手动指定文件名，见 "BBC iPlayer 整季下载" 部分

3. **YouTube 等单视频**：
   ```
   -o "%(title)s.%(ext)s"
   ```

### 下载指定分辨率
```bash
yt-dlp -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]" \
  --write-subs --write-auto-subs --sub-langs "en.*" \
  -o "%(title)s.%(ext)s" "URL"
```

### 列出可用格式
```bash
yt-dlp -F "URL"
```

## 执行流程

1. **解析参数**：检查 `$ARGUMENTS` 是否包含选项关键词（字幕、整季、1080p 等）

2. **如果只提供 URL 没有选项，使用 AskUserQuestion 询问用户**：

   **问题1**（仅BBC iPlayer单集链接时询问）：
   - header: "下载范围"
   - question: "要下载单集还是整季？"
   - options:
     - "单集" - 只下载这一集
     - "整季" - 下载该系列所有剧集

   **问题2**：
   - header: "下载内容"
   - question: "需要下载什么？"
   - options:
     - "视频+字幕" - 下载视频并嵌入字幕
     - "仅字幕" - 只下载字幕文件，不下载视频

   **问题3**：
   - header: "字幕翻译"
   - question: "是否需要翻译字幕为中英双语？"
   - options:
     - "需要翻译" - 下载后自动翻译为中英双语字幕
     - "不需要" - 只保留原始字幕

3. **检查 cookies**：
   - 如果 `.tmp/cookies.txt` 不存在，从 Chrome 导出
   - 需要登录的网站（BBC、Netflix 等）必须使用 cookies

4. **执行下载命令**（使用 `--cookies .tmp/cookies.txt`）

5. **如果用户选择翻译字幕**，使用 **subtitle-translation** skill 进行翻译

## 字幕翻译集成

下载字幕后，自动触发进行字幕翻译的逻辑：
1. 应用 subtitle-translation skill 的规则
2. 生成双语字幕，后缀使用 `.ZH&EN.srt`（例如：`VideoName.ZH&EN.srt`）
3. **保留** 原始英文字幕文件（后缀 `.en.srt`）
4. 优化中文布局（尽量单行）

## Cookies 管理

某些网站（BBC iPlayer、Netflix 等）需要登录 cookies。使用缓存机制避免重复读取浏览器：

### 执行逻辑

1. 检查 `.tmp/cookies.txt` 是否存在
2. 如果不存在，从 Chrome 导出：
   ```bash
   mkdir -p .tmp
   yt-dlp --cookies-from-browser chrome --cookies .tmp/cookies.txt --skip-download "about:blank" 2>/dev/null || true
   ```
3. 使用缓存的 cookies 文件：
   ```bash
   yt-dlp --cookies .tmp/cookies.txt ...
   ```

### Cookies 参数

- 有缓存时：`--cookies .tmp/cookies.txt`
- 无缓存时：先导出再使用
- 强制刷新：删除 `.tmp/cookies.txt` 后重新执行

## 注意事项

- 确保 yt-dlp 已安装：`brew install yt-dlp`
- 更新 yt-dlp：`yt-dlp -U`
- Cookies 过期时删除 `.tmp/cookies.txt` 重新导出

## BBC iPlayer 整季下载

BBC iPlayer 的 URL 结构：
- 单集：`/iplayer/episode/{episode_id}/{slug}` （episode 单数）
- 系列：`/iplayer/episodes/{series_id}/{slug}` （episodes 复数）

### BBC 命名格式

**目标格式**：`Show.Name.S01E01.ext`

BBC 元数据特点：
- `series`, `season_number`, `episode_number` 均为空
- `title` 格式：`Show Name, Series X, Episode Title`
- 需要用 `%(playlist_index)s` 获取集数

**命名方案**：先下载，再批量重命名
```bash
# 1. 先用临时格式下载（使用playlist_index作为集数）
yt-dlp ... -o "%(title)s.%(ext)s" "系列URL"

# 2. 下载后用脚本重命名
# 从 "Show Name, Series X, Title.ext" 转换为 "Show.Name.S0XE0Y.ext"
```

### 执行逻辑

1. **检测 BBC iPlayer 链接**：URL 包含 `bbc.co.uk/iplayer/`

2. **判断链接类型**：
   - 如果是 `/iplayer/episodes/`（复数）→ 直接作为系列链接使用
   - 如果是 `/iplayer/episode/`（单数）→ 需要获取系列链接

3. **从单集链接获取系列链接**（自动）：
   ```bash
   SERIES_PATH=$(curl -s "单集URL" | grep -o '/iplayer/episodes/[^"]*' | head -1)
   SERIES_URL="https://www.bbc.co.uk${SERIES_PATH}"
   ```

4. **获取剧集列表并确定集数**：
   ```bash
   # 获取剧集ID列表（按播出顺序）
   yt-dlp --flat-playlist --print "%(id)s" "系列URL"
   ```

5. **逐集下载并命名**（推荐方式）：
   ```bash
   # 获取剧名和季号
   SHOW_NAME="Show.Name"  # 从URL或首集title解析
   SEASON="01"            # 从title中的"Series X"解析

   # 逐集下载，使用正确的集数
   EP=1
   for ID in $(yt-dlp --flat-playlist --print "%(id)s" "系列URL"); do
     yt-dlp --cookies .tmp/cookies.txt \
       -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
       --write-subs --write-auto-subs --sub-langs "en.*" \
       -o "${SHOW_NAME}.S${SEASON}E$(printf '%02d' $EP).%(ext)s" \
       "https://www.bbc.co.uk/iplayer/episode/${ID}"
     ((EP++))
   done
   ```

6. **或批量下载后重命名**：
   ```bash
   # 先下载所有（用原始title）
   yt-dlp --cookies .tmp/cookies.txt \
     -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
     --write-subs --write-auto-subs --sub-langs "en.*" \
     -o "%(title)s.%(ext)s" \
     "系列URL"

   # 然后根据剧集列表顺序重命名文件
   ```

### 选项

- `整季` / `全部` - 下载整季所有剧集
- `字幕` - 仅下载整季字幕
- `列表` - 仅列出剧集，不下载

### BBC 示例

```bash
# 从单集链接下载整季
/yt-dlp https://www.bbc.co.uk/iplayer/episode/m002hzgh/can-you-keep-a-secret-series-1-episode-1 整季

# 直接用系列链接下载整季
/yt-dlp https://www.bbc.co.uk/iplayer/episodes/m002hzgb/can-you-keep-a-secret

# 仅下载整季字幕
/yt-dlp https://www.bbc.co.uk/iplayer/episodes/m002hzgb/can-you-keep-a-secret 字幕

# 列出所有剧集
/yt-dlp https://www.bbc.co.uk/iplayer/episode/m002hzgh/xxx 列表
```

## 示例

```
/yt-dlp https://www.youtube.com/watch?v=xxx
/yt-dlp https://www.youtube.com/watch?v=xxx 仅字幕
/yt-dlp https://www.youtube.com/watch?v=xxx 1080p
/yt-dlp https://www.bbc.co.uk/iplayer/episode/m002hzgh/xxx 整季
/yt-dlp https://www.bbc.co.uk/iplayer/episodes/m002hzgb/xxx
```
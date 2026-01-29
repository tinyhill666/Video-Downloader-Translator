# Claude Code 项目指南

## 可用命令

### /yt-dlp
下载视频和字幕。

```
/yt-dlp <URL> [选项]
```

**选项：**
- `字幕` - 仅下载字幕
- `1080p` - 指定分辨率
- `整季` - BBC iPlayer 下载整季（自动获取系列链接）
- `列表` - 仅列出剧集，不下载
- 无选项 - **交互式询问**（下载范围/内容/是否翻译）

**交互式模式：**
只提供 URL 不带选项时，会询问：
1. BBC链接：下载单集还是整季？
2. 下载视频+字幕还是仅字幕？
3. 是否需要翻译为中英双语字幕？

**示例：**
```
/yt-dlp https://www.youtube.com/watch?v=xxx           # 交互式
/yt-dlp https://www.youtube.com/watch?v=xxx 字幕      # 直接执行
/yt-dlp https://www.bbc.co.uk/iplayer/episode/xxx 整季
```

**Cookies：**
- 自动使用 `.tmp/cookies.txt`
- 不存在时从 Chrome 导出

## 字幕翻译流程

当用户要求翻译字幕时：

### 1. 准备
```bash
python .claude/skills/subtitle-translation/scripts/prepare_translation.py video.en.srt
```

### 2. 翻译
用户说「翻译 video.en.batches/」时：
1. 读取全部批次：`cat video.en.batches/batch_*.txt`
2. 全文一次性翻译（保持上下文连贯）
3. 写入 `video.en.batches/translations.txt`

**翻译要求：**
- 口语化、自然
- 保持语气、情感、幽默
- 俚语意译，不直译
- 人名一致（Chi=小琪）
- 【大写】= 场景描述 → 【中文描述】
- 每行对应一行，不合并不拆分

### 3. 完成
```bash
python .claude/skills/subtitle-translation/scripts/finalize_translation.py video.en.batches/
```

生成 `video.ZH&EN.srt`（中文在上，英文黄色在下，生僻词绿色高亮）

## 目录结构

```
.claude/
├── commands/yt-dlp.md        # 下载命令
└── skills/subtitle-translation/
    ├── SKILL.md              # 翻译规则
    └── scripts/
        ├── utils.py
        ├── prepare_translation.py
        ├── finalize_translation.py
        └── translate_srt.py   # API用户可用
.tmp/
└── cookies.txt               # 缓存的浏览器cookies
```

# Video Downloader & Translator

Claude Code Skills 展示目录，包含视频下载和字幕翻译相关的自定义技能。

## 包含的 Skills

### 1. yt-dlp (Command)
使用 yt-dlp 下载视频和字幕，支持 YouTube、BBC iPlayer 等平台。

```
/yt-dlp <URL> [选项]
```

### 2. subtitle-translation (Skill)
字幕翻译技能，将英文字幕翻译成中英双语字幕：
- 支持 SRT/VTT/ASS 格式
- 分批翻译，上下文感知
- 生僻词绿色高亮
- 英文黄色显示

## 快速开始

```bash
# 1. 下载字幕
/yt-dlp https://example.com/video 字幕

# 2. 准备翻译
python .claude/skills/subtitle-translation/scripts/prepare_translation.py video.en.srt

# 3. 在对话中翻译
翻译 video.en.batches/

# 4. 生成双语字幕
python .claude/skills/subtitle-translation/scripts/finalize_translation.py video.en.batches/
```

## 目录结构

```
.claude/
├── commands/
│   └── yt-dlp.md              # 视频下载命令
├── skills/
│   └── subtitle-translation/
│       ├── SKILL.md           # 技能说明
│       └── scripts/
│           ├── utils.py                 # 公共模块
│           ├── prepare_translation.py   # 准备翻译批次
│           ├── finalize_translation.py  # 合并双语字幕
│           └── translate_srt.py         # 一键翻译(需API)
└── settings.local.json
```

## 依赖

```bash
# 必需
brew install yt-dlp

# 可选（生僻词高亮）
pip install wordfreq
```

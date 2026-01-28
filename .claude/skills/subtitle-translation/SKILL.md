---
name: subtitle-translation
description: This skill should be used when translating subtitles, processing SRT/VTT/ASS files, creating bilingual subtitles, or reformatting subtitle layout. Provides translation principles, layout rules, and width calculation methods.
version: 1.0.0
---

# 字幕翻译技能

## 概述

本技能提供字幕翻译的核心规则和布局优化方法，用于将英文字幕翻译成中英双语字幕，并智能处理字幕布局。

## 支持的格式

- **SRT**: SubRip 字幕格式（最常用）
- **VTT**: WebVTT 格式
- **ASS/SSA**: Advanced SubStation Alpha 格式

## 翻译原则

### 基本原则
1. **保持时间轴**：绝对不修改时间码
2. **保持格式标签**：保留 `<i>`, `<b>`, `{\an8}`, `{\pos()}` 等格式标签
3. **上下文连贯**：结合前后字幕理解对话含义
4. **自然表达**：使用地道的中文，避免翻译腔
5. **专有名词一致性**：人名、地名、术语保持全篇一致
6. **语气还原**：保持原文的情感和语气

### 翻译技巧
- 口语化表达优于书面语
- 适当省略不影响理解的连接词
- 保持字幕简洁，便于观看时阅读
- 如果直译过长，可适当意译

## 布局重排规则

### 字符宽度计算

```
中文字符、全角标点：宽度 = 2
英文字符、数字、半角标点：宽度 = 1
```

### 宽度限制

| 分辨率 | 建议最大宽度 | 约等于 |
|--------|-------------|--------|
| 720p   | 36          | 18个中文字 |
| 1080p  | 42          | 21个中文字 |
| 1440p  | 48          | 24个中文字 |
| 4K     | 56          | 28个中文字 |

**默认使用 42（适合 1080p）**

### 中文布局原则

1. **优先单行显示**
   - 计算译文宽度
   - 如果宽度 <= 最大宽度，保持单行
   - 大多数日常对话翻译后都应该是单行

2. **智能合并**
   - 原文多行但内容连贯时，翻译可合并为单行
   - 自动识别的碎片化文本应合并

3. **必要时换行**
   - 超出宽度时需要换行
   - 换行位置优先级：
     1. 句号、问号、感叹号后
     2. 逗号、分号后
     3. "的、地、得"后
     4. "了、着、过"后
     5. 动词和宾语之间
   - 避免在词语中间换行

4. **每条字幕最多两行**
   - 双语字幕：英文一行 + 中文一行
   - 如果中文必须换行：英文一行 + 中文两行（最多三行总计）

### 英文原文布局

1. 保持原有换行结构（除非明显不合理）
2. 碎片化的自动识别文本可合并
3. 过长的单句可在逗号或连词处换行

## 双语字幕格式

### 双语样式规则
- **结构**：中文在上（第一行），英文在下（第二行）。
- **英文样式**：使用黄色字体 `<font color="#ffff00">英文内容</font>`。
- **生僻词高亮**：英文中的生僻词使用绿色字体 `<font color="#00ff00">difficult</font>` 标注。
- **中文样式**：无颜色配置（默认白色），单行宽度放宽至 60 字符（约 30 汉字）。
- **清理**：在处理前清除原有的所有颜色和字体标签。
- **布局**：确保长句合理换行。

### 标准格式示例

```srt
1
00:00:01,000 --> 00:00:03,500
这是一个非常复杂的局面。
<font color="#ffff00">This is a very <font color="#00ff00">complicated</font> situation.</font>

2
00:00:04,000 --> 00:00:07,200
我很好，谢谢关心！
<font color="#ffff00">I'm doing great, thanks for asking!</font>
```

### 长句处理示例

原文（碎片化）：
```
I think we should
go there tomorrow.
```

输出（合并优化）：
```
I think we should go there tomorrow.
我觉得我们明天应该去那里。
```

### 超长句处理

原文：
```
This is a very important message that everyone needs to understand clearly.
```

输出（中文需换行）：
```
This is a very important message that everyone needs to understand clearly.
这是一条非常重要的信息，
每个人都需要清楚理解。
```

## 宽度计算函数

计算字符串显示宽度的逻辑：

```
对于字符串中的每个字符:
  如果是中文字符或全角标点: 宽度 += 2
  否则: 宽度 += 1
返回总宽度
```

中文字符范围：
- CJK统一汉字: U+4E00-U+9FFF
- 全角标点: U+3000-U+303F, U+FF00-U+FFEF

## 特殊情况处理

### 歌词字幕
- 保持诗意和韵律
- 可以适当调整换行以配合节奏

### 技术术语
- 专业术语可保留英文或加注
- 例如: "API (应用程序接口)"

### 俚语和习语
- 找到对应的中文表达
- 不要直译，要意译

### 对话标识
- 保留对话者标识符（如 "- "）
- 多人对话时确保区分清晰

## 输出文件命名

| 类型 | 文件名格式 |
|------|-----------|
| 双语字幕 | `原文件名.ZH&EN.srt` |
| 仅中文 | `原文件名.zh.srt` |
| 仅英文 | `原文件名.en.srt` |

## 批量翻译策略

1. 每次处理 20-50 条字幕
2. 保持上下文连贯性
3. 记录专有名词映射
4. 翻译后复核时间轴对齐
5. 最后进行全局布局优化

## 翻译流程

### Claude Code 用户（推荐）

使用分步脚本，在对话中完成翻译：

```bash
# 步骤1: 准备翻译批次
python prepare_translation.py video.en.srt

# 步骤2: 在 Claude Code 对话中翻译
# 对话中会自动读取批次文件，逐批翻译并写入 translations.txt

# 步骤3: 合并生成双语字幕
python finalize_translation.py video.en.batches/
```

**流程说明：**

1. `prepare_translation.py` 自动完成：
   - 解析 SRT，清理标签
   - 分批保存（默认每批 50 行）
   - 生成 `video.en.batches/` 目录

2. 在对话中告诉 Claude：`翻译 video.en.batches/`
   - Claude 会逐批读取、翻译、写入结果
   - 上下文感知，保持角色名一致

3. `finalize_translation.py` 自动完成：
   - 合并翻译结果
   - 生僻词绿色高亮
   - 生成 `video.ZH&EN.srt`

### API 用户

如果有 `ANTHROPIC_API_KEY`，可使用一键脚本：

```bash
export ANTHROPIC_API_KEY='your-key'
python translate_srt.py video.en.srt video.ZH&EN.srt --model sonnet
```

支持 `--model haiku/sonnet/opus` 和 `--workers N` 并行数。

## 脚本列表

| 脚本 | 用途 |
|-----|------|
| `utils.py` | 公共模块（SRT解析、生僻词高亮）|
| `prepare_translation.py` | 准备翻译批次 |
| `finalize_translation.py` | 合并生成双语字幕 |
| `translate_srt.py` | 一键翻译（需 API Key）|
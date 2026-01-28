"""
字幕处理公共模块
"""

import re

# ============ SRT 解析 ============
def parse_srt(file_path):
    """解析 SRT 文件，返回字幕列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('\r\n', '\n').replace('\r', '\n')
    blocks = re.split(r'\n\n+', content.strip())

    subtitles = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2:
            try:
                index = int(lines[0])
                timecode_idx = 1
            except ValueError:
                index = len(subtitles) + 1
                timecode_idx = 0

            if timecode_idx < len(lines) and '-->' in lines[timecode_idx]:
                parts = lines[timecode_idx].split(' --> ')
                start, end = parts[0].strip(), parts[1].strip()
                text = '\n'.join(lines[timecode_idx + 1:])
                # 清理 font 标签
                text = re.sub(r'<font[^>]*>', '', text)
                text = re.sub(r'</font>', '', text)

                subtitles.append({
                    'index': index,
                    'start': start,
                    'end': end,
                    'text': text.strip()
                })

    return subtitles


# ============ 生僻词高亮 ============
try:
    from wordfreq import zipf_frequency
    HAS_WORDFREQ = True
except ImportError:
    HAS_WORDFREQ = False

WORD_FREQ_CACHE = {}
RARE_THRESHOLD = 3.0
MIN_WORD_LENGTH = 5


def get_word_frequency(word):
    """获取词频（带缓存）"""
    if word in WORD_FREQ_CACHE:
        return WORD_FREQ_CACHE[word]
    freq = zipf_frequency(word, 'en') if HAS_WORDFREQ else 8.0
    WORD_FREQ_CACHE[word] = freq
    return freq


def highlight_rare_words(text):
    """高亮生僻词（绿色），返回带标签的文本"""
    if not HAS_WORDFREQ:
        return text

    tokens = re.split(r'(\W+)', text)
    result = []
    is_sentence_start = True

    for token in tokens:
        if not token:
            continue

        if not token[0].isalpha():
            result.append(token)
            if re.search(r'[.!?]', token):
                is_sentence_start = True
            continue

        # 跳过短词
        if len(token) < MIN_WORD_LENGTH:
            result.append(token)
            is_sentence_start = False
            continue

        # 跳过专有名词（非句首大写）
        if token[0].isupper() and not is_sentence_start:
            result.append(token)
            is_sentence_start = False
            continue

        freq = get_word_frequency(token.lower())

        if 0 < freq < RARE_THRESHOLD:
            result.append(f'<font color="#00ff00">{token}</font>')
        else:
            result.append(token)

        is_sentence_start = False

    return "".join(result)


# ============ 双语字幕生成 ============
def generate_bilingual_srt(subtitles, translations, output_path):
    """生成双语 SRT 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles):
            zh = translations[i] if i < len(translations) else ""
            en = sub['text'].replace('\n', ' ')

            # 高亮英文生僻词
            en_highlighted = highlight_rare_words(en)

            f.write(f"{sub['index']}\n")
            f.write(f"{sub['start']} --> {sub['end']}\n")
            f.write(f"{zh}\n")
            f.write(f'<font color="#ffff00">{en_highlighted}</font>\n')
            f.write("\n")

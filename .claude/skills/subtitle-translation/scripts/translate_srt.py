#!/usr/bin/env python3
"""
一键字幕翻译脚本（需要 ANTHROPIC_API_KEY）

用法: python translate_srt.py input.srt output.srt [--model sonnet]
"""

import re
import sys
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import parse_srt, generate_bilingual_srt

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# 配置
MODELS = {
    'haiku': 'claude-3-5-haiku-20241022',
    'sonnet': 'claude-sonnet-4-5-20250929',
    'opus': 'claude-opus-4-5-20251101',
}
BATCH_SIZE = 40
MAX_WORKERS = 5


def translate_batch(client, model, lines, context_before=None, context_after=None):
    """翻译一批文本"""
    prompt = """你是专业的影视字幕翻译。将以下英文字幕翻译成中文。

要求：
1. 口语化、自然，符合中文表达习惯
2. 保持原文语气、情感和幽默感
3. 俚语和习语要意译
4. 【大写文字】是场景描述，翻译成【中文描述】
5. 每行对应一行输出，只输出中文

"""
    if context_before:
        prompt += f"前文参考：\n{context_before}\n\n"

    prompt += "翻译内容：\n" + '\n'.join(lines)

    if context_after:
        prompt += f"\n\n后文参考：\n{context_after}"

    try:
        message = client.messages.create(
            model=model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        translations = [l.strip() for l in message.content[0].text.strip().split('\n') if l.strip()]
        while len(translations) < len(lines):
            translations.append("")
        return translations[:len(lines)]
    except Exception as e:
        print(f"  错误: {e}")
        return [""] * len(lines)


def translate_all(subtitles, model_name='sonnet', max_workers=MAX_WORKERS):
    """并行翻译所有字幕"""
    client = Anthropic()
    model = MODELS.get(model_name, MODELS['sonnet'])

    all_lines = [sub['text'].replace('\n', ' ') for sub in subtitles]
    total = len(all_lines)

    print(f"共 {total} 条，模型: {model_name}，并行: {max_workers}")

    # 准备批次
    batches = []
    for i in range(0, total, BATCH_SIZE):
        batches.append({
            'index': i,
            'lines': all_lines[i:i + BATCH_SIZE],
            'context_before': '\n'.join(all_lines[max(0, i-3):i]) if i > 0 else None,
            'context_after': '\n'.join(all_lines[i + BATCH_SIZE:i + BATCH_SIZE + 3]) if i + BATCH_SIZE < total else None,
        })

    print(f"共 {len(batches)} 批")

    # 并行翻译
    translations = [""] * total
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(translate_batch, client, model, b['lines'], b['context_before'], b['context_after']): b['index']
            for b in batches
        }

        for future in as_completed(futures):
            idx = futures[future]
            for j, t in enumerate(future.result()):
                if idx + j < total:
                    translations[idx + j] = t
            completed += 1
            print(f"  {completed}/{len(batches)}")

    return translations


def main():
    parser = argparse.ArgumentParser(description='一键字幕翻译（需要API Key）')
    parser.add_argument('input', help='输入 SRT')
    parser.add_argument('output', help='输出 SRT')
    parser.add_argument('--model', '-m', choices=['haiku', 'sonnet', 'opus'], default='sonnet')
    parser.add_argument('--workers', '-w', type=int, default=MAX_WORKERS)

    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("错误: 请安装 anthropic (pip install anthropic)")
        sys.exit(1)

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("错误: 请设置 ANTHROPIC_API_KEY")
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    print(f"解析: {args.input}")
    subtitles = parse_srt(args.input)

    translations = translate_all(subtitles, args.model, args.workers)

    generate_bilingual_srt(subtitles, translations, args.output)
    print(f"完成: {args.output}")


if __name__ == "__main__":
    main()

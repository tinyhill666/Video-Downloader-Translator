#!/usr/bin/env python3
"""
翻译完成脚本 - 合并翻译结果生成双语字幕

用法: python finalize_translation.py input.batches/ [--output output.ZH&EN.srt]
"""

import re
import os
import sys
import json
import argparse

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import generate_bilingual_srt


def main():
    parser = argparse.ArgumentParser(description='合并翻译生成双语字幕')
    parser.add_argument('batches_dir', help='批次目录')
    parser.add_argument('--output', '-o', help='输出文件 (默认: 原文件名.ZH&EN.srt)')

    args = parser.parse_args()

    if not os.path.isdir(args.batches_dir):
        print(f"错误: 目录不存在 - {args.batches_dir}")
        sys.exit(1)

    # 读取元数据
    metadata_file = os.path.join(args.batches_dir, 'metadata.json')
    if not os.path.exists(metadata_file):
        print(f"错误: 找不到 metadata.json")
        sys.exit(1)

    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    subtitles = metadata['subtitles']
    total = metadata['total_lines']

    # 读取翻译结果
    translations_file = os.path.join(args.batches_dir, 'translations.txt')
    if not os.path.exists(translations_file):
        print(f"错误: 找不到 translations.txt")
        sys.exit(1)

    with open(translations_file, 'r', encoding='utf-8') as f:
        translations = [line.strip() for line in f.readlines()]

    # 检查行数
    if len(translations) < total:
        print(f"警告: 翻译 {len(translations)} 行，字幕 {total} 行，缺少 {total - len(translations)} 行")
        translations.extend([''] * (total - len(translations)))
    elif len(translations) > total:
        print(f"警告: 翻译行数多于字幕，截取前 {total} 行")
        translations = translations[:total]

    # 确定输出文件名
    if args.output:
        output_file = args.output
    else:
        source = metadata['source_file']
        base = os.path.splitext(source)[0]
        base = re.sub(r'\.(en|eng|english)$', '', base, flags=re.IGNORECASE)
        output_file = f"{base}.ZH&EN.srt"

    # 生成双语字幕
    print(f"生成: {output_file}")
    generate_bilingual_srt(subtitles, translations, output_file)
    print(f"完成! {total} 条双语字幕")


if __name__ == "__main__":
    main()

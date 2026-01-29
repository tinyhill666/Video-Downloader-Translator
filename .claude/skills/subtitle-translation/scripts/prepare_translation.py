#!/usr/bin/env python3
"""
翻译准备脚本 - 从 SRT 提取文本并分批保存

用法: python prepare_translation.py input.srt [--batch-size 50]
输出: input.batches/ 目录（含批次文件和元数据）
"""

import os
import sys
import json
import argparse

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import parse_srt


def main():
    parser = argparse.ArgumentParser(description='准备字幕翻译批次')
    parser.add_argument('input', help='输入 SRT 文件')
    parser.add_argument('--batch-size', '-b', type=int, default=50, help='每批行数 (默认: 50)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    # 解析字幕
    print(f"解析字幕: {args.input}")
    subtitles = parse_srt(args.input)
    total = len(subtitles)
    print(f"共 {total} 条字幕")

    # 创建输出目录
    base_name = os.path.splitext(args.input)[0]
    output_dir = f"{base_name}.batches"
    os.makedirs(output_dir, exist_ok=True)

    # 提取文本（单行化）
    all_lines = [sub['text'].replace('\n', ' ') for sub in subtitles]
    batch_count = (total + args.batch_size - 1) // args.batch_size

    print(f"分成 {batch_count} 批，每批 {args.batch_size} 行")

    # 分批保存（带全局行号前缀）
    for i in range(0, total, args.batch_size):
        batch_num = i // args.batch_size + 1
        batch_lines = all_lines[i:i + args.batch_size]

        batch_file = os.path.join(output_dir, f"batch_{batch_num:03d}.txt")
        with open(batch_file, 'w', encoding='utf-8') as f:
            # 每行添加全局行号前缀: "001→原文"
            for j, line in enumerate(batch_lines):
                global_line_num = i + j + 1  # 1-based
                f.write(f"{global_line_num:03d}→{line}\n")

        print(f"  batch_{batch_num:03d}.txt ({len(batch_lines)} 行)")

    # 保存元数据
    metadata = {
        'source_file': os.path.basename(args.input),
        'total_lines': total,
        'batch_size': args.batch_size,
        'batch_count': batch_count,
        'subtitles': subtitles
    }

    with open(os.path.join(output_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # 创建空的翻译结果文件
    open(os.path.join(output_dir, 'translations.txt'), 'w').close()

    print(f"\n完成! 批次目录: {output_dir}/")
    print(f"下一步: 在对话中说「翻译 {output_dir}」")


if __name__ == "__main__":
    main()

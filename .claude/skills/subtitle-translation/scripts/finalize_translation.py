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
import shutil

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import generate_bilingual_srt


def cleanup_and_fail(batches_dir, message):
    """删除批次目录并报错退出"""
    print(f"\n❌ 错误: {message}")
    print("正在删除临时文件，请重新开始...")
    try:
        shutil.rmtree(batches_dir)
        print(f"已删除: {batches_dir}")
    except Exception as e:
        print(f"删除失败: {e}")

    print("\n请重新运行 prepare_translation.py 开始新的翻译流程。")
    sys.exit(1)


def is_translation_valid(zh_lines, en_subtitles, check_last_n=5):
    """
    简单的翻译质量检查
    1. 检查最后N行是否为空
    2. 检查最后N行是否包含基本的中文字符（防止英文复制）
    3. 检查场景标记【】是否在对应行（增强内容对应检查）
    """
    total = len(en_subtitles)
    start_idx = max(0, total - check_last_n)

    for i in range(start_idx, total):
        zh = zh_lines[i].strip()
        en = en_subtitles[i]['text'].strip()

        # 允许原文和译文都为空的情况
        if not en and not zh:
            continue

        # 如果原文不为空但译文为空
        if en and not zh:
            return False, f"第 {i+1} 行翻译为空 (原文: {en[:20]}...)"

        # 简单检查中文包含度 (汉字范围)
        # 排除纯标点或纯数字的情况
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', zh))
        if en and not has_chinese and len(zh) > 0:
            # 允许一些特殊情况，如 "OK.", "No." 等可能不包含汉字
            # 但如果是长句子且没有汉字，可能是未翻译
            if len(en) > 10 and len(zh) > 5:
                return False, f"第 {i+1} 行疑似未翻译 (原文: {en[:20]}... 译文: {zh})"

        # 检查特殊标记是否匹配（增强内容对应检查）
        # 场景描述标记检查
        en_has_caps = bool(re.search(r'^[A-Z][A-Z\s]+[A-Z]$', en))  # 全大写行如 "KNOCK ON DOOR"
        zh_has_brackets = bool(re.search(r'【[^】]+】', zh))  # 【场景描述】
        if en_has_caps and not zh_has_brackets:
            return False, f"第 {i+1} 行场景标记不匹配 (原文: {en} 译文: {zh[:30]}...)"

        # 检查简单关键词匹配（针对短句）
        if len(en) < 15 and len(zh) < 15:
            # 对于非常短的句子，检查一些明显的不匹配
            # 如果英文是问号结尾，中文也应该有问号
            if en.endswith('?') and '？' not in zh and '吗' not in zh:
                return False, f"第 {i+1} 行疑似内容不匹配 (原文问句: {en} 译文: {zh})"

    return True, "OK"


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
        cleanup_and_fail(args.batches_dir, "找不到 metadata.json")

    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    subtitles = metadata['subtitles']
    total_lines = metadata['total_lines']

    # 读取翻译结果
    translations_file = os.path.join(args.batches_dir, 'translations.txt')
    if not os.path.exists(translations_file):
        cleanup_and_fail(args.batches_dir, "找不到 translations.txt - 翻译可能未完成")

    with open(translations_file, 'r', encoding='utf-8') as f:
        raw_lines = [line.rstrip('\n') for line in f.readlines()]

    # 解析带行号的翻译（格式: "001→翻译内容" 或纯文本）
    translations = []
    line_numbers = []
    has_line_numbers = raw_lines and '→' in raw_lines[0][:10] if raw_lines else False

    for idx, line in enumerate(raw_lines):
        if has_line_numbers:
            # 尝试解析行号前缀
            if '→' in line[:10]:
                parts = line.split('→', 1)
                try:
                    line_num = int(parts[0])
                    line_numbers.append(line_num)
                    translations.append(parts[1] if len(parts) > 1 else '')
                except ValueError:
                    # 无法解析行号，当作普通行处理
                    translations.append(line)
                    line_numbers.append(idx + 1)
            else:
                translations.append(line)
                line_numbers.append(idx + 1)
        else:
            translations.append(line)

    # 1. 严格检查行数
    if len(translations) != total_lines:
        msg = f"行数不匹配! 字幕有 {total_lines} 行，但翻译了 {len(translations)} 行。"
        cleanup_and_fail(args.batches_dir, msg)

    # 2. 如果有行号，检查行号连续性
    if has_line_numbers and line_numbers:
        missing = []
        duplicate = []
        expected = set(range(1, total_lines + 1))
        seen = set()
        for ln in line_numbers:
            if ln in seen:
                duplicate.append(ln)
            seen.add(ln)
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)

        if missing:
            msg = f"缺少行号: {missing[:10]}{'...' if len(missing) > 10 else ''}"
            cleanup_and_fail(args.batches_dir, msg)
        if duplicate:
            msg = f"重复行号: {duplicate[:10]}{'...' if len(duplicate) > 10 else ''}"
            cleanup_and_fail(args.batches_dir, msg)
        if extra:
            msg = f"多余行号: {extra[:10]}{'...' if len(extra) > 10 else ''}"
            cleanup_and_fail(args.batches_dir, msg)

    # 2. 检查最后几行的质量
    valid, reason = is_translation_valid(translations, subtitles, check_last_n=5)
    if not valid:
        cleanup_and_fail(args.batches_dir, f"翻译质量校验失败: {reason}")

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
    print(f"完成! {total_lines} 条双语字幕")

    # 成功后清理
    try:
        shutil.rmtree(args.batches_dir)
        print(f"已清理临时目录: {args.batches_dir}")
    except:
        pass


if __name__ == "__main__":
    main()

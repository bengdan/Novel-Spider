"""
把爬下来的小说 CSV 转成 EPUB。

用法:
    python epub-converter.py 冰火魔厨.csv
    python epub-converter.py *.csv -o epub
    python epub-converter.py data.csv --title 斗罗大陆 --author 唐家三少 --cover cover.jpg

CSV 需要 chapter、content 两列。有 index 列（scrapy 直接导出的 data.csv）就按 index 排序，
没有（txt-converter.py 输出的 sorted-data.csv）就按行序。书名默认取文件名。

依赖: pip install ebooklib
"""
import argparse
import csv
import glob
import html
import os
import re
import sys
import uuid
from datetime import datetime, timezone

from ebooklib import epub

LANGUAGE = 'zh-CN'

CSS = '''
body { line-height: 1.8; }
h2 { margin: 1em 0 1.5em; font-size: 1.3em; line-height: 1.4; text-align: center; }
p { margin: 0 0 0.6em; text-indent: 2em; text-align: justify; }
'''

COVER_TYPES = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

TAG = re.compile(r'</?[a-zA-Z][^<>]*>')
LINE_BREAK = re.compile(r'<br\s*/?>|</p\s*>', re.IGNORECASE)
# characters XML 1.0 does not allow; one of them makes the whole chapter unreadable
INVALID_XML = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f￾￿]')
CHAPTER_NO = re.compile(r'第\s*([0-9０-９零〇一二三四五六七八九十百千万]+)\s*([章节回卷集部篇幕])')

# chapters can be far larger than csv's default 128 KB field limit
csv.field_size_limit(2**31 - 1)


def clean_text(text):
    # some spiders cut content out of raw HTML, so tags and entities can be left over
    text = LINE_BREAK.sub('\n', text)
    text = TAG.sub('', text)
    text = html.unescape(text)
    return INVALID_XML.sub('', text)


def clean_title(title):
    title = ' '.join(clean_text(title).split())
    title = re.sub(r'^正文\s+', '', title)
    # "第 445章" / "第675 章" -> "第445章"
    return CHAPTER_NO.sub(r'第\1\2', title)


def split_paragraphs(content, title):
    paragraphs = [line.strip() for line in clean_text(content).splitlines()]
    paragraphs = [p for p in paragraphs if p]
    # some sites repeat the chapter title as the first line
    if paragraphs and clean_title(paragraphs[0]) == title:
        paragraphs = paragraphs[1:]
    return paragraphs


def index_key(row):
    try:
        return 0, int(float(row['index']))
    except (TypeError, ValueError):
        return 1, 0


def read_chapters(csv_path):
    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        missing = {'chapter', 'content'} - set(columns)
        if missing:
            raise ValueError(f'缺少 {"、".join(sorted(missing))} 列（现有列: {columns}）')
        rows = list(reader)
    if 'index' in columns:
        # scrapy writes items in the order requests finish, not in TOC order
        rows.sort(key=index_key)
    return rows


def build_book(rows, title, author=None, cover=None):
    book = epub.EpubBook()
    # stable id, so re-converting the same book doesn't show up as a new book in readers
    book.set_identifier('urn:uuid:%s' % uuid.uuid5(uuid.NAMESPACE_URL, 'novel-spider/%s/%s' % (title, author or '')))
    book.set_title(title)
    book.set_language(LANGUAGE)
    if author:
        book.add_author(author)

    style = epub.EpubItem(uid='style', file_name='style.css', media_type='text/css', content=CSS.encode('utf-8'))
    book.add_item(style)

    spine = []
    if cover:
        with open(cover, 'rb') as f:
            book.set_cover('cover' + os.path.splitext(cover)[1].lower(), f.read())
        cover_page = book.get_item_with_id('cover')
        cover_page.title = '封面'
        cover_page.is_linear = True
        spine.append(cover_page)

    chapters, empty = [], []
    width = max(4, len(str(len(rows))))
    for i, row in enumerate(rows, 1):
        chapter_title = clean_title(row.get('chapter') or '') or f'第 {i} 节'
        paragraphs = split_paragraphs(row.get('content') or '', chapter_title)
        if not paragraphs:
            # ebooklib silently writes an empty file for an empty body, so always keep some text
            empty.append(chapter_title)
            paragraphs = ['（本章内容缺失）']

        body = f'<h2>{html.escape(chapter_title)}</h2>\n'
        body += '\n'.join(f'<p>{html.escape(p)}</p>' for p in paragraphs)

        name = f'chapter_{i:0{width}d}'
        chapter = epub.EpubHtml(uid=name, file_name=name + '.xhtml', title=chapter_title,
                                lang=LANGUAGE, media_type='application/xhtml+xml')
        chapter.content = body.encode('utf-8')
        chapter.add_item(style)
        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = chapters
    book.add_item(epub.EpubNcx())
    nav = epub.EpubNav(title='目录')
    nav.add_item(style)
    book.add_item(nav)
    # readers build their own TOC from nav/ncx; keeping a several-hundred-entry
    # contents page out of the spine means the book opens on the first chapter
    book.spine = spine + chapters
    return book, empty


def safe_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip().rstrip('.')


def convert(csv_path, output_dir=None, title=None, author=None, cover=None):
    title = title or os.path.splitext(os.path.basename(csv_path))[0].strip()
    rows = read_chapters(csv_path)
    if not rows:
        raise ValueError('CSV 里没有章节')

    book, empty = build_book(rows, title, author, cover)

    output_dir = output_dir or os.path.dirname(os.path.abspath(csv_path))
    os.makedirs(output_dir, exist_ok=True)
    epub_path = os.path.join(output_dir, safe_filename(title) + '.epub')
    epub.write_epub(epub_path, book, {
        # ebooklib only returns False on write errors unless told to raise
        'raise_exceptions': True,
        # page-list scan re-parses every chapter and we have no page markers
        'epub3_pages': False,
        'mtime': datetime.now(timezone.utc),
    })
    return epub_path, len(rows), empty


def expand_paths(patterns):
    # PowerShell and cmd pass wildcards through as-is, so expand them here
    paths = []
    for pattern in patterns:
        if os.path.exists(pattern):
            paths.append(pattern)
            continue
        matches = sorted(glob.glob(pattern))
        if not matches:
            sys.exit(f'找不到文件: {pattern}')
        paths.extend(matches)
    return paths


def main():
    # the Windows console is GBK by default; don't crash on titles it can't show
    sys.stdout.reconfigure(errors='replace')

    parser = argparse.ArgumentParser(description='把爬下来的小说 CSV 转成 EPUB')
    parser.add_argument('csv_files', nargs='+', help='CSV 文件，支持通配符，比如 *.csv')
    parser.add_argument('-o', '--output-dir', help='输出目录，默认和 CSV 放在一起')
    parser.add_argument('--title', help='书名，默认取文件名（只能配合单个 CSV 用）')
    parser.add_argument('--author', help='作者')
    parser.add_argument('--cover', help='封面图片（jpg / png / gif / webp）')
    args = parser.parse_args()

    paths = expand_paths(args.csv_files)
    if args.title and len(paths) > 1:
        parser.error('--title 只能配合单个 CSV 使用')
    if args.cover and os.path.splitext(args.cover)[1].lower() not in COVER_TYPES:
        parser.error('封面只支持 ' + ' / '.join(COVER_TYPES))

    failed = 0
    for path in paths:
        try:
            epub_path, count, empty = convert(path, args.output_dir, args.title, args.author, args.cover)
        except Exception as e:
            failed += 1
            print(f'[失败] {path}: {e}')
            continue

        size = os.path.getsize(epub_path) / 1024 / 1024
        print(f'[完成] {path} -> {epub_path}（{count} 章，{size:.1f} MB）')
        if empty:
            more = ' 等' if len(empty) > 5 else ''
            print(f'  有 {len(empty)} 章正文为空，已用占位文字代替: {"、".join(empty[:5])}{more}')

    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()

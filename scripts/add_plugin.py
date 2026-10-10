#!/usr/bin/env python3
"""Interactively add a TrollFools dylib and optionally commit/push it."""
import json
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'trollpackages.json'
DOWNLOADS = ROOT / 'downloads'

def ask(prompt, default=''):
    suffix = f' [{default}]' if default else ''
    value = input(f'{prompt}{suffix}: ').strip()
    return value or default

def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)

def main():
    if len(sys.argv) != 2:
        raise SystemExit('用法: python3 scripts/add_plugin.py /path/to/plugin.dylib')
    source = pathlib.Path(sys.argv[1]).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != '.dylib':
        raise SystemExit('错误：请输入存在的 .dylib 文件。')
    default_name = re.sub(r'[_-](?:v?\d[\w.~-]*)$', '', source.stem, flags=re.I).replace('_', ' ')
    name = ask('插件名称', default_name)
    version = ask('版本号', '1.0')
    description = ask('请输入这个 dylib 的功能/描述')
    while not description:
        print('描述不能为空，请说明它实现什么功能。')
        description = ask('请输入这个 dylib 的功能/描述')
    bundle = ask('目标 App Bundle ID（可选，没有或不确定直接回车）')
    if not name or not version or any(c in name + version for c in '/\\\x00'):
        raise SystemExit('名称/版本不能为空，且不能包含路径分隔符。')
    filename = f'{name}_{version}.dylib'
    target = DOWNLOADS / filename
    if target.exists():
        raise SystemExit(f'错误：目标文件已存在：{target.name}')
    DOWNLOADS.mkdir(exist_ok=True)
    shutil.copy2(source, target)
    data = json.loads(MANIFEST.read_text())
    item = {
        'name': name,
        'version': version,
        'description': description,
        'dylib': f'https://wm0104.github.io/trollfools-repo/downloads/{urllib.parse.quote(filename)}',
        'section': 'App 插件',
        'size': f'{target.stat().st_size / 1024:.2f} KB'
    }
    if bundle:
        item['bundle'] = bundle
    data.setdefault('packages', []).append(item)
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(f'\n已准备：{target.relative_to(ROOT)}')
    print(f'名称：{name}\n版本：{version}\n描述：{description}')
    if bundle:
        print(f'Bundle ID：{bundle}')
    if input('\n确认提交并推送到 GitHub？[y/N]: ').strip().lower() != 'y':
        print('已取消提交；文件仍保留在本地，请检查后再处理。')
        return
    run('git', 'add', 'downloads', 'trollpackages.json')
    run('git', 'commit', '-m', f'Add TrollFools plugin {name} {version}')
    run('git', 'push', 'origin', 'main')
    if source.parent == (ROOT / 'inbox').resolve():
        backup = ROOT / 'uploaded'
        backup.mkdir(exist_ok=True)
        archived = backup / source.name
        counter = 1
        while archived.exists():
            archived = backup / f'{source.stem}_{counter}{source.suffix}'
            counter += 1
        shutil.move(str(source), str(archived))
        print(f'原件已自动备份到：{archived}')
    print('已推送。GitHub Actions 将自动校验并发布。')

if __name__ == '__main__':
    main()

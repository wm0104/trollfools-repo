#!/usr/bin/env python3
"""Scan inbox and interactively publish dylibs with the tj command."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    inbox = ROOT / 'inbox'
    inbox.mkdir(exist_ok=True)
    files = sorted(p for p in inbox.iterdir() if p.is_file() and p.suffix.lower() == '.dylib')
    if not files:
        print(f'没有待上传的 dylib。请将文件放到：{inbox}')
        return
    print(f'找到 {len(files)} 个插件。逐个填写说明并确认提交；不会自动拉取或覆盖你的修改。')
    for file in files:
        print(f'\n=== {file.name} ===')
        subprocess.run([sys.executable, str(ROOT / 'scripts/add_plugin.py'), str(file)], cwd=ROOT, check=True)
        if file.exists():
            print('未完成上传，原件仍保留在 inbox。')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('\n已中止。')
    except subprocess.CalledProcessError:
        sys.exit('提交/推送未完成，请检查提示；本地文件未删除。')

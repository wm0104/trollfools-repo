#!/usr/bin/env python3
"""Synchronize recursive downloads/**/*.dylib; standard library only."""
import argparse
import copy
import json
import os
from pathlib import Path
import posixpath
import re
import tempfile
from urllib.parse import quote, unquote, urlsplit

BASE = 'https://wm0104.github.io/trollfools-repo/'
PREFIX = '/trollfools-repo/downloads/'


def local_path(url):
    """Return normalized repo path only for this repository's Pages downloads."""
    parsed = urlsplit(url)
    if (parsed.scheme.lower() not in ('http', 'https') or
            parsed.netloc.lower() != 'wm0104.github.io'):
        return None
    if re.search(r'%(?![0-9a-fA-F]{2})', parsed.path):
        raise ValueError('Invalid percent escape in local URL: ' + url)
    decoded = unquote(parsed.path, encoding='utf-8', errors='strict')
    # Normalize once (not twice), so filenames containing literal % remain valid.
    normalized = posixpath.normpath(decoded)
    if not normalized.startswith(PREFIX):
        return None
    return normalized[len('/trollfools-repo/'):]


def filename_defaults(stem):
    """Only a complete trailing dotted numeric version is unambiguous.

    Accept Name_1.2.0, Name-v2.0 and Name-2.0; do not guess from embedded
    digits, dates, build annotations or a lone trailing number.
    """
    match = re.fullmatch(r'(.+)[_-][vV]?(\d+(?:\.\d+)+)', stem)
    return (match.group(1), match.group(2)) if match else (stem, '1.0')


def format_size(size):
    return f'{size / 1024:.2f} KB'


def synchronize(root, data):
    if not isinstance(data, dict):
        raise ValueError('Manifest must be an object')
    if not isinstance(data.get('repository_name'), str) or not data['repository_name'].strip():
        raise ValueError('repository_name must be a nonempty string')
    if not isinstance(data.get('packages'), list):
        raise ValueError('packages must be an array')
    downloads = root / 'downloads'
    if not downloads.is_dir() or downloads.is_symlink():
        raise ValueError('downloads must be a real directory; refusing destructive cleanup')
    files = {}
    for file in sorted(downloads.rglob('*')):
        if file.suffix.lower() != '.dylib':
            continue
        if file.is_symlink() or any(p.is_symlink() for p in file.parents if p != root):
            raise ValueError('Symlink downloads are unsupported: ' + str(file))
        if file.is_file():
            files[file.relative_to(root).as_posix()] = file
    local = {}
    external = []
    for package in data['packages']:
        if not isinstance(package, dict) or not isinstance(package.get('dylib'), str) or not package['dylib'].strip():
            raise ValueError('Every package must be an object with a nonempty dylib URL')
        path = local_path(package['dylib'])
        if path is None:
            external.append(copy.deepcopy(package))
        elif path in files:
            if path not in local:
                local[path] = copy.deepcopy(package)
            else:
                # First entry wins conflicts; retain non-conflicting fields from duplicates.
                for key, value in package.items():
                    local[path].setdefault(key, copy.deepcopy(value))
        # Missing local downloads are deliberately removed; external URLs are untouched.
    packages = []
    for path, file in sorted(files.items()):
        package = local.get(path, {})
        name, version = filename_defaults(file.stem)
        defaults = {'name': name, 'version': version, 'section': 'App 插件'}
        for key, value in defaults.items():
            if key not in package or package[key] is None or package[key] == '':
                package[key] = value
        if 'description' not in package or package['description'] is None or package['description'] == '':
            package['description'] = package['name']
        # Temporary SLP filename compatibility test; keep original binary filename.
        package['dylib'] = BASE + (path if path == 'downloads/中国广电.dylib' else quote(path, safe='/'))
        package['size'] = format_size(file.stat().st_size)
        packages.append(package)
    result = copy.deepcopy(data)
    result['packages'] = packages + external
    return result


def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_manifest(path):
    if not path.exists():
        return {'repository_name': 'wm0104 TrollFools 源', 'packages': []}
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=reject_duplicates,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Invalid JSON constant: ' + value)))


def sync_file(root, dry_run=False):
    path = root / 'trollpackages.json'
    data = synchronize(root, load_manifest(path))
    text = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    changed = not path.exists() or path.read_text(encoding='utf-8') != text
    if changed and not dry_run:
        fd, temp = tempfile.mkstemp(prefix='.trollpackages-', dir=root)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                stream.write(text)
            os.chmod(temp, 0o644)
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    print(f'{"Would update" if dry_run and changed else "Updated" if changed else "Unchanged"}: {len(data["packages"])} packages')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--dry-run', action='store_true', help='Validate and report without writing')
    args = parser.parse_args()
    try:
        sync_file(args.root.resolve(), args.dry_run)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Sync failed: {error}\n')


if __name__ == '__main__':
    main()

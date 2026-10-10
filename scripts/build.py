import json
import pathlib
import re
import shutil
import urllib.parse

root = pathlib.Path(__file__).resolve().parents[1]
manifest_path = root / 'trollpackages.json'
data = json.loads(manifest_path.read_text())
assert isinstance(data.get('repository_name'), str) and data['repository_name'].strip()
assert isinstance(data.get('packages'), list)

# Keep manually curated entries, then discover new packages from downloads/.
existing = {p.get('dylib'): p for p in data['packages']}
base = 'https://wm0104.github.io/trollfools-repo/'
for file in sorted((root / 'downloads').iterdir()):
    if file.suffix.lower() not in ('.dylib', '.zip', '.deb'):
        continue
    url = base + 'downloads/' + urllib.parse.quote(file.name)
    if url in existing:
        continue
    stem = file.stem
    match = re.match(r'^(?P<name>.+?)[_-](?P<version>v?\d[\w.~-]*)$', stem, re.I)
    name = match.group('name').replace('_', ' ') if match else stem
    version = match.group('version').lstrip('v') if match else '1.0'
    existing[url] = {
        'name': name,
        'version': version,
        'description': '自动收录插件，尚未补充详细说明；实际兼容性请先测试。',
        'dylib': url,
        'section': 'App 插件',
        'size': f'{file.stat().st_size / 1024:.2f} KB'
    }
data['packages'] = list(existing.values())
manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

for p in data['packages']:
    for field in ('name', 'version', 'description', 'dylib'):
        assert isinstance(p.get(field), str) and p[field].strip(), f'Missing {field}'
    url = urllib.parse.urlparse(p['dylib'])
    assert url.scheme == 'https', 'Download must use HTTPS'
    prefix = '/trollfools-repo/'
    if url.netloc == 'wm0104.github.io' and url.path.startswith(prefix):
        file = (root / urllib.parse.unquote(url.path[len(prefix):])).resolve()
        assert root in file.parents and file.is_file(), f'Missing download: {url.path}'
        assert file.suffix.lower() in ('.dylib', '.zip', '.deb'), 'Unsupported package type'

out = root / '_site'
if out.exists():
    shutil.rmtree(out)
out.mkdir()
for name in ('index.html', 'trollpackages.json', '.nojekyll'):
    shutil.copyfile(root / name, out / name)
for name in ('downloads', 'icons', 'screenshots'):
    if (root / name).is_dir():
        shutil.copytree(root / name, out / name)
print(f'Validated {len(data["packages"])} packages')

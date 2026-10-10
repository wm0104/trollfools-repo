import json,pathlib,shutil,urllib.parse
root=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((root/'trollpackages.json').read_text())
assert isinstance(data.get('repository_name'),str) and data['repository_name'].strip()
assert isinstance(data.get('packages'),list)
for p in data['packages']:
    for field in ('name','version','description','dylib'):
        assert isinstance(p.get(field),str) and p[field].strip(), f'Missing {field}'
    url=urllib.parse.urlparse(p['dylib'])
    assert url.scheme=='https', 'Download must use HTTPS'
    prefix='/trollfools-repo/'
    if url.netloc=='wm0104.github.io' and url.path.startswith(prefix):
        file=(root/urllib.parse.unquote(url.path[len(prefix):])).resolve()
        assert root in file.parents and file.is_file(), f'Missing download: {url.path}'
        assert file.suffix.lower() in ('.dylib','.zip','.deb'), 'Unsupported package type'
out=root/'_site'
if out.exists(): shutil.rmtree(out)
out.mkdir()
for name in ('index.html','trollpackages.json','.nojekyll'):
    shutil.copyfile(root/name,out/name)
for name in ('downloads','icons','screenshots'):
    if (root/name).is_dir(): shutil.copytree(root/name,out/name)
print(f'Validated {len(data["packages"])} packages')

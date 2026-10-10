import pathlib
import shutil
from sync_index import sync_file

root = pathlib.Path(__file__).resolve().parents[1]
# Pages and the committed manifest use exactly the same normalization/defaults.
data = sync_file(root)

out = root / '_site'
if out.exists():
    shutil.rmtree(out)
out.mkdir()
for name in ('index.html', 'trollpackages.json', '.nojekyll'):
    shutil.copyfile(root / name, out / name)
for name in ('downloads', 'icons', 'screenshots'):
    if (root / name).is_dir():
        shutil.copytree(root / name, out / name)
# Isolated filename compatibility test; production index is unchanged.
if (root / 'filename-test').is_dir():
    shutil.copytree(root / 'filename-test', out / 'filename-test')
print(f'Validated {len(data["packages"])} packages')

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sync_index import BASE, load_manifest, local_path, sync_file, synchronize


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'downloads').mkdir()
        self.data = {'repository_name': 'Fixture', 'custom_repository_field': 42, 'packages': []}

    def file(self, name='new.dylib', content=b'x' * 1024):
        file = self.root / 'downloads' / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content)
        return file

    def test_add_defaults_and_bytes_unchanged(self):
        file = self.file('new_9.9.dylib')
        digest = hashlib.sha256(file.read_bytes()).digest()
        result = synchronize(self.root, self.data)
        self.assertEqual(result['packages'], [{'name': 'new_9.9', 'version': '1.0',
            'description': 'new_9.9', 'section': 'App 插件',
            'dylib': BASE + 'downloads/new_9.9.dylib', 'size': '1.00 KB'}])
        self.assertEqual(result['custom_repository_field'], 42)
        self.assertEqual(hashlib.sha256(file.read_bytes()).digest(), digest)
        self.assertEqual(self.data['packages'], [])

    def test_delete_local_keep_external_even_same_name(self):
        external = {'dylib': 'https://example.org/downloads/missing.dylib', 'name': 'missing', 'extra': 1}
        other_repo = {'dylib': 'https://wm0104.github.io/other/downloads/missing.dylib'}
        self.data['packages'] = [{'dylib': BASE + 'downloads/missing.dylib'}, external, other_repo]
        self.assertEqual(synchronize(self.root, self.data)['packages'], [external, other_repo])

    def test_custom_fields_and_path_matching(self):
        self.file()
        original = {'dylib': BASE + 'downloads/./new.dylib?download=1', 'name': 'Custom',
            'version': '7.2', 'description': 'Curated', 'bundle': 'com.test', 'author': 'A',
            'icon': 'i.png', 'screenshots': ['s.png'], 'app_url': 'https://example.org',
            'section': 'Custom section', 'other': {'a': 1}, 'size': 'wrong'}
        self.data['packages'] = [copy.deepcopy(original)]
        item = synchronize(self.root, self.data)['packages'][0]
        for key in original.keys() - {'dylib', 'size'}:
            self.assertEqual(item[key], original[key])
        self.assertEqual(item['dylib'], BASE + 'downloads/new.dylib')
        self.assertEqual(item['size'], '1.00 KB')

    def test_chinese_spaces_literal_percent_hash_and_recursive(self):
        self.file('子目录/中文 空格%20#?.dylib')
        url = BASE + 'downloads/%E5%AD%90%E7%9B%AE%E5%BD%95/%E4%B8%AD%E6%96%87%20%E7%A9%BA%E6%A0%BC%2520%23%3F.dylib'
        self.data['packages'] = [{'dylib': url, 'version': '3'}]
        result = synchronize(self.root, self.data)
        self.assertEqual(len(result['packages']), 1)
        self.assertEqual(result['packages'][0]['dylib'], url)
        self.assertEqual(result['packages'][0]['version'], '3')
        self.assertEqual(local_path(url), 'downloads/子目录/中文 空格%20#?.dylib')

    def test_duplicates_first_wins_merge_nonconflicting_fields(self):
        self.file('中文 空.dylib')
        self.data['packages'] = [
            {'dylib': BASE + 'downloads/中文 空.dylib', 'version': '2', 'description': 'first'},
            {'dylib': BASE + 'downloads/%E4%B8%AD%E6%96%87%20%E7%A9%BA.dylib', 'version': '3', 'bundle': 'com.test'}]
        items = synchronize(self.root, self.data)['packages']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['version'], '2')
        self.assertEqual(items[0]['bundle'], 'com.test')

    def test_dry_run_idempotence_and_json(self):
        self.file()
        path = self.root / 'trollpackages.json'
        path.write_text(json.dumps(self.data), encoding='utf-8')
        before = path.read_bytes()
        sync_file(self.root, dry_run=True)
        self.assertEqual(path.read_bytes(), before)
        sync_file(self.root)
        after = path.read_bytes()
        sync_file(self.root)
        self.assertEqual(path.read_bytes(), after)
        self.assertEqual(len(load_manifest(path)['packages']), 1)

    def test_missing_index_created(self):
        self.file()
        self.assertEqual(len(sync_file(self.root)['packages']), 1)

    def test_bad_json_rejected_without_write(self):
        path = self.root / 'trollpackages.json'
        for text in ['{', '{"packages": [], "packages": []}', '{"n": NaN}']:
            path.write_text(text)
            with self.assertRaises(ValueError):
                sync_file(self.root)
            self.assertEqual(path.read_text(), text)

    def test_bad_schema_missing_directory_and_symlink(self):
        with self.assertRaises(ValueError):
            synchronize(self.root, {'repository_name': 'A', 'packages': [42]})
        (self.root / 'downloads').rmdir()
        with self.assertRaises(ValueError):
            synchronize(self.root, self.data)
        (self.root / 'downloads').mkdir()
        target = self.root / 'outside'
        target.write_bytes(b'payload')
        (self.root / 'downloads' / 'link.dylib').symlink_to(target)
        with self.assertRaises(ValueError):
            synchronize(self.root, self.data)

    def test_non_dylib_not_discovered(self):
        self.file('ignore.deb')
        self.file('ignore.zip')
        self.assertEqual(synchronize(self.root, self.data)['packages'], [])


if __name__ == '__main__':
    unittest.main()

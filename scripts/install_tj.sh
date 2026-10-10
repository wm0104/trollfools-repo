#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
mkdir -p "$HOME/.local/bin" inbox
python3 -c 'import pathlib,shlex; root=pathlib.Path.cwd(); p=pathlib.Path.home()/".local/bin/tj"; p.write_text("#!/bin/sh\nexec python3 " + shlex.quote(str(root/"scripts/tj.py")) + " \"$@\"\n"); p.chmod(0o755)'
if ! grep -q '.local/bin' "$HOME/.profile" 2>/dev/null; then
    printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.profile"
fi
printf '安装完成。将 dylib 放到 %s/inbox/，然后输入 tj。\n当前终端请先执行：export PATH="$HOME/.local/bin:$PATH"\n' "$PWD"

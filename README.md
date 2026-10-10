# wm0104 TrollFools 源

适用于文档所述的 TrollFools SLP 版，与 APT/Sileo 源独立。

## 添加源

在 TrollFools 的 + 按钮中输入：

https://wm0104.github.io/trollfools-repo/

不要在添加地址末尾写 trollpackages.json。

## 维护

1. 将插件上传到 `downloads/`，文件名建议为 `插件名称_版本.dylib`，例如 `淘宝去广告_1.0.dylib`。
2. 提交到 `main` 后，Actions 会自动扫描新文件并生成 `trollpackages.json`。
3. 名称和版本从文件名识别；无法识别时默认使用文件名和版本 `1.0`。
4. 自动生成的描述是占位说明；如需详细描述、`bundle`、图标或截图，再手动编辑 `trollpackages.json`。
5. 提交到 main 后自动发布。构建会保留已有手动条目，不会重复添加同一个下载链接。

构建会验证必需字段、JSON 和本仓库下载链接。此检查不证明插件安全或运行兼容性。只上传拥有分发权的插件，不执行来源不明的文件。

## tf-tj 快捷提交（推荐）

首次在 iSH 中进入仓库执行：

```sh
git pull --ff-only
sh scripts/install_tj.sh
export PATH="$HOME/.local/bin:$PATH"
```

将 dylib 放进仓库的 `inbox/` 文件夹，在终端输入 `tf-tj` 即可逐个填写名称、版本、功能说明和可选 Bundle ID，然后确认提交推送。`inbox/` 不会被 Git 提交；原件保留，成功上传后请移出该目录。命令不自动拉取或覆盖修改，推送失败请先检查 Git 提示。

## 在 iSH 中上传新插件

推荐使用交互式脚本，提交前会要求填写功能描述并确认：

```sh
cd /path/to/trollfools-repo
git pull
python3 scripts/add_plugin.py /path/to/你的插件.dylib
```

它会询问插件名称、版本、**功能/描述**和可选的目标 App Bundle ID；描述不能为空，最后还会再次询问是否提交并推送。确认后，脚本自动复制文件、更新 `trollpackages.json`、提交并推送，Actions 再自动发布。

如果取消最后确认，文件和索引只保留在本地，不会推送。


拼多多去广告 1.1：按用户提供文件收录，未运行或验证注入兼容性；未核实作者及目标 Bundle ID，故省略相关字段。不将文件名作为兼容性证明。

开发文档：https://trollfools.slpmods.net/dev-docs/?lang=zh

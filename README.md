# wm0104 TrollFools 源

适用于文档所述的 TrollFools SLP 版，与 APT/Sileo 源独立。

## 添加源

在 TrollFools 的 + 按钮中输入：

https://wm0104.github.io/trollfools-repo/

不要在添加地址末尾写 trollpackages.json。

## 维护

1. 将插件上传到 downloads/（建议使用英文文件名）。
2. 在根目录 trollpackages.json 的 packages 中新增条目。
3. 必需字段：name、version、description、dylib（HTTPS 下载地址）。
4. 可选：bundle（核实后的目标 App Bundle ID）、app_url、icon_url、section、size、author、screenshots。
5. 提交到 main 后自动发布。仅上传文件不会自动新增列表，需同时编辑 JSON。

构建会验证必需字段、JSON 和本仓库下载链接。此检查不证明插件安全或运行兼容性。只上传拥有分发权的插件，不执行来源不明的文件。

## 当前插件

拼多多去广告 1.1：按用户提供文件收录，未运行或验证注入兼容性；未核实作者及目标 Bundle ID，故省略相关字段。不将文件名作为兼容性证明。

开发文档：https://trollfools.slpmods.net/dev-docs/?lang=zh

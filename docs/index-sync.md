# 自动索引同步

`Sync TrollFools index` 在 main 的 downloads 下 dylib 或 trollpackages.json 变化时运行，也可从 Actions 手动运行。工作流/脚本/测试变化也触发回归验证。支持递归子目录，文件后缀大小写不敏感（push 路径匹配为 `.dylib` / `.DYLIB`）；推荐统一 `.dylib` 后缀。工作流只提交 trollpackages.json，不更改二进制。

- 新条目：仅识别完整末尾的明确点分数字版本，如 `Plugin_1.2.0`、`Plugin-v2.0`、`Plugin-2.0`；name 去掉该版本后缀，version 去掉可选 v。无法识别（如单个数字、嵌入数字或构建注释）时 name 为完整文件名去扩展名，version=1.0。description=name，section=App 插件；已有手动 version/description 不被覆盖。
- size 按实际字节/1024，保留两位小数，沿用客户端的 KB 格式；dylib 为本源 Pages URL，UTF-8 percent-encode。
- 用解码一次、规范化后的本仓库相对路径匹配；名称不参与匹配。URL query/fragment 不影响路径匹配，同步后使用标准 URL。
- 已有 name/version/description/section/bundle/author/icon/screenshots/app_url 及未知字段保留；本地条目的 URL/size 由脚本更新，缺失或空的基本字段补默认值。
- 仅删除本仓库 Pages downloads 内已不存在文件的条目；其他域名或本域其他仓库 URL 原样保留。
- 同路径重复项：第一条的冲突字段优先，后续条目补充未出现字段；同名不同路径不会合并。外链不去重。
- JSON 必须有效，拒绝重复对象键/NaN/坏 schema/无 downloads 目录/下载符号链接，失败时不写入。索引使用临时文件原子替换。
- GitHub Token 提交不再次触发 Actions，另有自动提交消息 guard 与无 diff 不提交保护。并发 push 时最多基于最新 main 重试三次，不强推；分支保护必须允许 GitHub Actions 写 main。
- Pages build 使用同一个同步算法。即使 Token 的后续提交不触发 Pages，原始用户 push 的 Pages build 仍产出同步后的索引。
- 只发现 dylib，不扫描 zip/deb；只从明确文件名后缀提取版本，不推断兼容性，不进行签名检查或真机注入验证；外链不联网验证。

本地只读预览：

```sh
python3 scripts/sync_index.py --dry-run
```

同步与离线回归（测试在临时目录创建 fixtures，不修改下载文件）：

```sh
python3 scripts/sync_index.py
python3 -m unittest discover -s scripts/tests -v
```

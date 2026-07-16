# 图书馆需求变化前后对比答辩版

这是一个独立汇报交付物，不修改图书馆业务源码、既有 `验收.md`、旧 PPT、HTML、tools 或需求文档。

## 生成

脚本只使用 Python 标准库、`python-pptx` 与 Pillow：

```bash
python3 presentation/build_ppt.py
```

如果默认 Python 环境没有加载依赖，可使用本机已有的、包含 `python-pptx` 与 Pillow 的虚拟环境：

```bash
/home/nianjiu/下载/710/ppt/.venv/bin/python presentation/build_ppt.py
```

输出文件：`presentation/图书馆需求变化前后对比答辩版.pptx`。

## 图片来源

- 改造前真实截图：`images/login.png`、`images/dashboard.png`、`images/book.png`、`images/reader.png`
- 改造后真实截图：`acceptance/screenshots/after-login.png`、`after-dashboard.png`、`after-book.png`、`after-user.png`
- 改造后截图来自 Playwright + Chromium 真实运行页面；采集视口为 1280×800。Dashboard 与图书页为 full-page 截图，文件高度分别为 862、988。
- 改造前仓库截图没有可靠的视口记录，PPT 仅标注原图分辨率，不把分辨率冒充视口。
- 未生成、合成或伪造任何运行截图。

## 内容证据

PPT 使用仓库中的真实提交与验收记录：

- T1–T5：`1745b11`、`eca083e`、`23401f3`、`322e1ce`、`48c645d`
- `./dev.sh verify`：11/11 PASS
- 借还续：6/6；库存：9/9；逾期：6/6；用户：7/7
- Playwright 两档视口（1280×800、1024×768）页面级无横向溢出、无 console error；关键 API 返回 200
- `verify-full`：PASS、0 失败，但保留既有“读者查看所有读者列表”权限 WARN

## 文件验证

```bash
/home/nianjiu/下载/710/ppt/.venv/bin/python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
from pptx import Presentation

p = Path('presentation/图书馆需求变化前后对比答辩版.pptx')
prs = Presentation(p)
print('slides:', len(prs.slides))
with ZipFile(p) as z:
    bad = z.testzip()
    print('zip_test:', bad or 'PASS')
PY
```

预期：`slides: 14`、`zip_test: PASS`。LibreOffice 在本机对任意 PPTX 的加载不稳定，因此文件有效性以 Python-PPTX 重开与 ZIP 无损条目检查为准；不伪造 LibreOffice/WPS 结果。

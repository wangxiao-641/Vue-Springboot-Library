# 图书馆管理系统最终汇报 PPT

这是 T4 独立汇报交付物，不修改业务源码、既有验收文档、锁文件、根目录旧 PPT、HTML 或 `tools/`。

## 生成

使用项目已有虚拟环境，无新增网络依赖：

```bash
/home/nianjiu/下载/710/ppt/.venv/bin/python presentation/build_ppt.py
```

输出：`presentation/图书馆需求变化前后对比答辩版.pptx`。

脚本固定生成 16:9、16 页 PPT，并在生成前检查所有图片路径。页脚页码会自动使用总页数 `16`。

## 内容结构

1. 封面与答辩主线
2. 五项需求总览
3. 库存数量、逾期管理、借还续后端化、用户管理
4. 原始截图 vs 最新 academy 默认风格的真实前后对比
5. 三风格总览与三风格 Login / Dashboard / Book / User 并排对比
6. 一键后端验收演示
7. 原五项需求提交链与第二版视觉增强提交 `aef9188`
8. 验收边界与结论

需求 5 的文字明确说明：

- `atlas` = 完整左栏馆藏运营台
- `academy` = 顶部导航书院阅读风、居中纸张分栏
- `command` = 窄图标轨道数字指挥舱、深色网格面板
- 首次默认 `academy`
- 登录前后均可切换，`localStorage` 持久化，切换无需刷新

## 图片来源

原始前后对比使用仓库历史真实截图：

- `images/login.png`
- `images/dashboard.png`
- `images/book.png`
- `images/reader.png`

最新三风格页面全部使用真实 Chromium 截图：

```text
acceptance/screenshots/theme-v2/
├── atlas-login.png       academy-login.png       command-login.png
├── atlas-dashboard.png   academy-dashboard.png   command-dashboard.png
├── atlas-book.png        academy-book.png        command-book.png
└── atlas-user.png        academy-user.png        command-user.png
```

User 三张截图使用临时中文读者按姓名筛选后的干净真实页面；创建、筛选、删除和 `total=0` 复核记录在 `acceptance/需求5-T2多主题浏览器验收记录.md` 与 `browser-check.json` 中。

## 一键后端验收页

PPT 展示以下现场命令与结果：

```bash
/home/nianjiu/下载/617/library/demo_backend_verification.sh
```

预期总表：

```text
circulation       6/6 PASS
inventory         9/9 PASS
overdue           6/6 PASS
user management   7/7 PASS
TOTAL PASS
```

脚本只编排既有 Python 黑盒；四个黑盒通过正式 HTTP API 创建和清理临时读者、图书、借阅与历史数据，不直连数据库。T3 的实际输出、失败继续分支和空 `ADMIN_PASSWORD` fallback 验证见 `acceptance/需求5-T3后端一键演示验收记录.md`。

## 验证

使用指定 Python 环境重开 PPT、检查 16:9、页数、所有图片引用、形状边界和 ZIP 完整性：

```bash
/home/nianjiu/下载/710/ppt/.venv/bin/python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
from pptx import Presentation

p = Path('presentation/图书馆需求变化前后对比答辩版.pptx')
prs = Presentation(p)
print('slides:', len(prs.slides))
print('aspect:', round(prs.slide_width / prs.slide_height, 4))
with ZipFile(p) as z:
    print('zip_test:', z.testzip() or 'PASS')
PY
```

另外建议执行：

```bash
git diff --check
/home/nianjiu/下载/710/ppt/.venv/bin/python presentation/build_ppt.py
```

本机实际尝试 LibreOffice 转 PDF时，中文原路径与 `/tmp/t4-library-final.pptx` ASCII 副本均返回 `Error: source file could not be loaded`，未生成 PDF；不伪造 LibreOffice 成功结果。Python-PPTX 重开、ZIP `testzip()`、图片存在性与边界检查是本交付的确定性验证依据。

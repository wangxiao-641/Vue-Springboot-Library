from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "图书馆需求变化前后对比答辩版.pptx"
W, H = 13.333, 7.5

NAVY = "142B3A"
INK = "23333D"
MUTED = "6A7A83"
TEAL = "16A394"
TEAL_DARK = "0D716A"
ORANGE = "E47B45"
RED = "D95D5D"
CREAM = "F7F4EE"
WHITE = "FFFFFF"
LINE = "DCE4E2"
PALE_TEAL = "E5F4F1"
PALE_ORANGE = "FFF0E7"
PALE_RED = "FCE9E7"

def rgb(h):
    return RGBColor.from_string(h)

def font_name():
    return "Microsoft YaHei"

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
blank = prs.slide_layouts[6]

def rect(slide, x, y, w, h, fill, radius=False, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                   Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = rgb(fill)
    shape.line.color.rgb = rgb(line or fill)
    if radius:
        shape.adjustments[0] = 0.08
    return shape

def line(slide, x1, y1, x2, y2, color=LINE, width=1.4, dash=None):
    l = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    l.line.color.rgb = rgb(color); l.line.width = Pt(width)
    if dash: l.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return l

def text(slide, s, x, y, w, h, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT,
         valign=MSO_ANCHOR.TOP, font=None, margin=0.04):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = Inches(margin); tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin); tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = s; r.font.name = font or font_name(); r.font.size = Pt(size)
    r.font.bold = bold; r.font.color.rgb = rgb(color)
    return tb

def title(slide, kicker, heading, sub=None, dark=False):
    c = WHITE if dark else NAVY
    text(slide, kicker.upper(), 0.62, 0.36, 4.2, 0.25, 10, TEAL if not dark else "8FE4D7", True)
    text(slide, heading, 0.62, 0.70, 12.0, 0.55, 26, c, True)
    if sub: text(slide, sub, 0.64, 1.30, 11.8, 0.38, 12, "B8C7CA" if dark else MUTED)

def footer(slide, n, dark=False):
    line(slide, 0.62, 7.12, 12.70, 7.12, "46606B" if dark else LINE, 0.8)
    text(slide, "图书馆管理系统 · 五项需求变化", 0.64, 7.18, 5.0, 0.16, 8, "A9BDC1" if dark else MUTED)
    text(slide, f"{n:02d} / 14", 11.85, 7.17, 0.85, 0.16, 8, "A9BDC1" if dark else MUTED, align=PP_ALIGN.RIGHT)

def add_bg(slide, dark=False):
    rect(slide, 0, 0, W, H, NAVY if dark else CREAM)

def card(slide, x, y, w, h, fill=WHITE, radius=True, line_color=LINE):
    return rect(slide, x, y, w, h, fill, radius, line_color)

def bullet_list(slide, items, x, y, w, size=16, color=INK, gap=0.34):
    for i, item in enumerate(items):
        cy = y + i * gap
        rect(slide, x, cy + 0.09, 0.08, 0.08, TEAL, True)
        text(slide, item, x + 0.20, cy, w - 0.20, gap, size, color)

def image_contain(slide, path, x, y, w, h, border=True):
    im = Image.open(path); iw, ih = im.size
    scale = min(w/iw, h/ih); nw, nh = iw*scale, ih*scale
    xx, yy = x + (w-nw)/2, y + (h-nh)/2
    if border: card(slide, x-0.03, y-0.03, w+0.06, h+0.06, WHITE, True, LINE)
    slide.shapes.add_picture(str(path), Inches(xx), Inches(yy), width=Inches(nw), height=Inches(nh))

def image_crop(slide, path, x, y, w, h):
    # crop to fill while retaining the real screenshot pixels
    im = Image.open(path); iw, ih = im.size
    scale = max(w/iw, h/ih); nw, nh = iw*scale, ih*scale
    xx, yy = x + (w-nw)/2, y + (h-nh)/2
    slide.shapes.add_picture(str(path), Inches(xx), Inches(yy), width=Inches(nw), height=Inches(nh))

def pill(slide, label, x, y, w, fill, color=WHITE):
    rect(slide, x, y, w, 0.30, fill, True, fill)
    text(slide, label, x, y+0.03, w, 0.22, 10, color, True, PP_ALIGN.CENTER)

def metric(slide, x, y, w, value, label, accent=TEAL):
    card(slide, x, y, w, 1.05, WHITE, True)
    rect(slide, x, y, 0.08, 1.05, accent, True, accent)
    text(slide, value, x+0.22, y+0.17, w-0.3, 0.38, 25, NAVY, True)
    text(slide, label, x+0.22, y+0.67, w-0.3, 0.22, 11, MUTED)

def compare_slide(kicker, heading, before, after, before_path, after_path, conclusion, n):
    s = prs.slides.add_slide(blank); add_bg(s); title(s, kicker, heading, "真实运行截图 · 改造前 / 改造后", False)
    card(s, 0.62, 1.83, 5.86, 4.72, WHITE, True)
    card(s, 6.86, 1.83, 5.86, 4.72, WHITE, True)
    pill(s, "改造前", 0.90, 2.08, 0.95, "8B9AA0")
    pill(s, "改造后", 7.14, 2.08, 0.95, TEAL)
    text(s, before, 1.98, 2.09, 3.95, 0.24, 11, MUTED, align=PP_ALIGN.RIGHT)
    text(s, after, 8.22, 2.09, 3.95, 0.24, 11, MUTED, align=PP_ALIGN.RIGHT)
    image_contain(s, before_path, 0.88, 2.50, 5.34, 3.33)
    image_contain(s, after_path, 7.12, 2.50, 5.34, 3.33)
    rect(s, 0.88, 6.06, 11.58, 0.32, PALE_TEAL, True, PALE_TEAL)
    text(s, "结论  ·  " + conclusion, 1.08, 6.11, 11.15, 0.20, 12, TEAL_DARK, True)
    footer(s, n)
    return s

# 1 cover
s = prs.slides.add_slide(blank); add_bg(s, True)
rect(s, 0, 0, 0.20, H, TEAL)
text(s, "LIBRARY ATLAS  /  DELIVERY REVIEW", 0.72, 0.62, 6.5, 0.25, 11, "8FE4D7", True)
text(s, "图书馆管理系统\n五项需求变化", 0.72, 1.43, 8.3, 1.32, 32, WHITE, True)
text(s, "实现成果与前后对比", 0.75, 2.95, 7.0, 0.45, 22, "D4E1E2", False)
line(s, 0.76, 3.66, 5.22, 3.66, TEAL, 2)
text(s, "真实截图 · 黑盒验收 · 提交证据 · 边界说明", 0.76, 3.88, 7.0, 0.28, 14, "B8C7CA")
card(s, 8.85, 1.22, 3.44, 4.56, "1E3B4A", True, "35616C")
text(s, "5", 9.32, 1.70, 2.5, 1.15, 76, "8FE4D7", True, PP_ALIGN.CENTER)
text(s, "项需求\n连续交付", 9.35, 3.02, 2.45, 0.75, 23, WHITE, True, PP_ALIGN.CENTER)
pill(s, "T1 → T5", 9.70, 4.39, 1.78, TEAL)
text(s, "2026.07  ·  答辩版", 9.40, 5.18, 2.35, 0.22, 11, "B8C7CA", align=PP_ALIGN.CENTER)
footer(s, 1, True)

# 2 project/problem
s = prs.slides.add_slide(blank); add_bg(s); title(s, "01 / CONTEXT", "项目与问题：从“能用”走向“可验证”", "五项变化共同指向同一个目标：把关键业务从页面行为，收敛为可追踪的系统能力")
card(s, 0.62, 1.90, 4.02, 4.65, NAVY, True, NAVY)
text(s, "改造前的典型断点", 0.94, 2.25, 3.2, 0.34, 20, WHITE, True)
bullet_list(s, ["库存只有可借 / 不可借，无法表达馆藏规模", "前端连续写多个接口，失败时容易留下半成品状态", "逾期、续借、删除约束分散在页面和旧接口", "视觉页面不统一，核心信息层级不稳定"], 0.96, 2.90, 3.25, 15, "D4E1E2", 0.68)
card(s, 4.96, 1.90, 7.75, 4.65, WHITE, True)
text(s, "本次交付的验证闭环", 5.32, 2.25, 4.3, 0.34, 20, NAVY, True)
steps = [("需求", "5 个变化"), ("实现", "T1–T5"), ("验证", "HTTP 黑盒"), ("呈现", "真实截图")]
for i, (a,b) in enumerate(steps):
    x = 5.32 + i*1.75
    rect(s, x, 3.10, 1.28, 1.06, PALE_TEAL if i<3 else PALE_ORANGE, True, LINE)
    text(s, a, x, 3.29, 1.28, 0.22, 14, TEAL_DARK if i<3 else ORANGE, True, PP_ALIGN.CENTER)
    text(s, b, x, 3.66, 1.28, 0.22, 12, INK, True, PP_ALIGN.CENTER)
    if i<3: line(s, x+1.30, 3.63, x+1.63, 3.63, TEAL, 1.5)
text(s, "交付口径", 5.32, 4.75, 1.2, 0.25, 12, MUTED, True)
text(s, "不把“代码已写”当作“能力已完成”——以验收记录、黑盒结果和运行截图共同作证。", 5.32, 5.10, 6.65, 0.55, 18, INK, True)
footer(s, 2)

# 3 overview
s = prs.slides.add_slide(blank); add_bg(s); title(s, "02 / FIVE CHANGES", "五项需求总览：业务规则、数据约束与体验同时收口")
items = [
    ("01", "库存数量", "totalCount / availableCount", TEAL, "库存从状态升级为可核对数量"),
    ("02", "逾期管理", "dueStatus / overdueDays", ORANGE, "应还日期与借阅限制后端判定"),
    ("03", "流程后端化", "/circulation/*", NAVY, "借还续一次业务写请求"),
    ("04", "用户管理", "POST /user · DELETE /user/{id}", RED, "新增 / 删除有权限与借阅边界"),
    ("05", "视觉改造", "Library Atlas", "6C6DE5", "统一导航、卡片、表格与反馈"),
]
for i,(num,name,code,accent,desc) in enumerate(items):
    x = 0.62 + (i%3)*4.20; y = 1.92 + (i//3)*2.05
    card(s, x, y, 3.82, 1.62, WHITE, True)
    rect(s, x, y, 0.12, 1.62, accent, True, accent)
    text(s, num, x+0.30, y+0.24, 0.55, 0.30, 17, accent, True)
    text(s, name, x+0.93, y+0.20, 2.55, 0.30, 19, NAVY, True)
    text(s, code, x+0.93, y+0.63, 2.55, 0.24, 10, MUTED)
    text(s, desc, x+0.30, y+1.16, 3.15, 0.24, 12, INK)
text(s, "五项需求不是五个孤岛：库存、逾期、用户约束最终都通过统一流程与页面呈现被验证。", 0.72, 6.30, 11.9, 0.30, 17, TEAL_DARK, True, PP_ALIGN.CENTER)
footer(s, 3)

# 4 backend flow
s = prs.slides.add_slide(blank); add_bg(s); title(s, "03 / REQUIREMENT 3", "需求 3：借书、还书、续借流程后端化", "前端只提交读者与图书标识；后端在一个事务内完成校验、日期、库存与三表更新")
card(s, 0.62, 1.90, 12.10, 3.80, WHITE, True)
nodes = [("页面点击", "readerId + isbn", 1.02, PALE_ORANGE, ORANGE), ("Controller", "/circulation/*", 3.65, PALE_TEAL, TEAL), ("CirculationService", "@Transactional", 6.30, "E8ECF7", "5864C7"), ("三张表一致", "book · current · history", 9.12, PALE_TEAL, TEAL)]
for i,(a,b,x,fill,accent) in enumerate(nodes):
    card(s, x, 2.75, 2.18, 1.45, fill, True, LINE)
    text(s, a, x+0.10, 3.02, 1.98, 0.24, 15, accent, True, PP_ALIGN.CENTER)
    text(s, b, x+0.10, 3.45, 1.98, 0.26, 11, INK, align=PP_ALIGN.CENTER)
    if i<3: line(s, x+2.20, 3.47, x+2.60, 3.47, accent, 2)
text(s, "借书", 1.34, 4.76, 1.2, 0.24, 12, MUTED, True, PP_ALIGN.CENTER)
text(s, "库存不足 / 逾期限制 / 重复借阅 → 失败时数据不变化", 2.50, 4.72, 5.05, 0.28, 13, INK)
text(s, "还书", 7.86, 4.76, 1.2, 0.24, 12, MUTED, True, PP_ALIGN.CENTER)
text(s, "恢复库存 · 删除当前借阅 · 更新历史记录", 9.02, 4.72, 3.0, 0.28, 13, INK)
metric(s, 0.72, 6.00, 2.45, "3", "业务接口", TEAL)
metric(s, 3.37, 6.00, 2.45, "1", "页面一次写请求", ORANGE)
metric(s, 6.02, 6.00, 2.45, "6/6", "借还续黑盒", NAVY)
metric(s, 8.67, 6.00, 3.50, "PASS", "失败路径数据不变", RED)
footer(s, 4)

# 5 inventory
s = prs.slides.add_slide(blank); add_bg(s); title(s, "04 / REQUIREMENT 1", "需求 1：库存从“状态”升级为“数量链路”", "页面展示与数据库约束共用同一套口径：馆藏总数、可借数量、已借出数")
card(s, 0.62, 1.88, 7.20, 4.70, WHITE, True)
text(s, "一次借书如何改变数据", 0.96, 2.20, 3.4, 0.30, 19, NAVY, True)
flow = [("借前", "总数 1", "可借 1", PALE_TEAL), ("借书成功", "库存 -1", "当前借阅 +1", PALE_ORANGE), ("借后", "总数 1", "可借 0", PALE_RED)]
for i,(a,b,c,fill) in enumerate(flow):
    x=1.00+i*2.12
    card(s,x,2.92,1.72,1.42,fill,True,LINE)
    text(s,a,x,3.13,1.72,0.22,13,TEAL_DARK if i==0 else ORANGE if i==1 else RED,True,PP_ALIGN.CENTER)
    text(s,b,x,3.53,1.72,0.22,14,INK,True,PP_ALIGN.CENTER)
    text(s,c,x,3.86,1.72,0.20,11,MUTED,align=PP_ALIGN.CENTER)
    if i<2: line(s,x+1.74,3.62,x+2.00,3.62,TEAL,1.6)
text(s, "后端约束", 1.00, 4.86, 1.2, 0.24, 12, MUTED, True)
bullet_list(s,["新增：totalCount 必须为正整数，availableCount 由后端初始化","编辑：总数不得小于当前已借出数，行锁串行化","并发：同一读者重复借阅一成一败，库存不穿透"],1.00,5.20,6.25,14,INK,0.38)
card(s, 8.10, 1.88, 4.62, 4.70, NAVY, True, NAVY)
text(s, "真实验收", 8.48, 2.22, 2.0, 0.26, 13, "8FE4D7", True)
text(s, "9/9", 8.48, 2.68, 2.20, 0.70, 44, WHITE, True)
text(s, "库存黑盒全部通过", 8.52, 3.48, 3.2, 0.25, 15, "D4E1E2", True)
pill(s,"库存为 0 拒绝借阅",8.48,4.17,2.45,ORANGE)
pill(s,"刷新后仍正确",8.48,4.63,1.85,TEAL)
text(s, "证据：acceptance/需求1-库存数量验收.md\n与 verify_inventory_http.py", 8.48, 5.36, 3.45, 0.55, 11, "B8C7CA")
footer(s, 5)

# 6 overdue
s = prs.slides.add_slide(blank); add_bg(s); title(s, "05 / REQUIREMENT 2", "需求 2：逾期状态成为可执行的借阅规则", "后端以 Asia/Shanghai 计算自然日边界；状态、天数与限制提示同时返回")
card(s, 0.62, 1.92, 7.20, 4.58, WHITE, True)
text(s, "状态机", 0.96, 2.20, 1.2, 0.28, 19, NAVY, True)
states=[("NORMAL","距应还日 > 3 天",TEAL,PALE_TEAL),("DUE_SOON","0–3 天内",ORANGE,PALE_ORANGE),("OVERDUE","早于今天",RED,PALE_RED)]
for i,(a,b,ac,fill) in enumerate(states):
    x=1.02+i*2.13
    card(s,x,2.95,1.78,1.18,fill,True,LINE)
    text(s,a,x,3.18,1.78,0.23,14,ac,True,PP_ALIGN.CENTER)
    text(s,b,x,3.57,1.78,0.22,11,INK,align=PP_ALIGN.CENTER)
    if i<2: line(s,x+1.80,3.54,x+2.02,3.54,ac,1.8)
text(s,"逾期后",1.02,4.73,1.1,0.22,12,MUTED,True)
text(s,"借新书 ✕   续借逾期图书 ✕   归还后自动解除限制 ✓",2.10,4.69,5.35,0.28,15,INK,True)
text(s,"规则可被筛选、纠正、复验，而不是只在页面上显示颜色。",1.02,5.43,6.20,0.36,15,TEAL_DARK,True)
card(s,8.10,1.92,4.62,4.58,NAVY,True,NAVY)
text(s,"黑盒结果",8.48,2.25,2.0,0.25,13,"8FE4D7",True)
text(s,"6/6",8.48,2.70,2.3,0.70,44,WHITE,True)
text(s,"日期生成 / 状态边界 / 借阅限制\n/ 筛选 / 归还解除",8.52,3.52,3.35,0.58,15,"D4E1E2",True)
pill(s,"昨天 = 1 天逾期",8.48,4.42,2.15,RED)
pill(s,"+3 天 = DUE_SOON",8.48,4.88,2.20,ORANGE)
text(s,"证据：acceptance/需求2-逾期管理验收.md\nverify_overdue_http.py",8.48,5.55,3.45,0.50,11,"B8C7CA")
footer(s, 6)

# 7 user
s = prs.slides.add_slide(blank); add_bg(s); title(s, "06 / REQUIREMENT 4", "需求 4：用户管理补上“新增—约束—删除”闭环", "管理员可新增普通读者；有未归还图书时禁止删除，归还后才可完成清理")
card(s,0.62,1.90,7.30,4.68,WHITE,True)
text(s,"管理员操作链路",0.96,2.22,2.6,0.28,19,NAVY,True)
chain=[("新增读者","role=2",TEAL,PALE_TEAL),("重复名","明确拒绝",ORANGE,PALE_ORANGE),("有借阅","禁止删除",RED,PALE_RED),("归还后","删除成功",TEAL_DARK,PALE_TEAL)]
for i,(a,b,ac,fill) in enumerate(chain):
    x=0.98+i*1.68
    card(s,x,3.02,1.40,1.36,fill,True,LINE)
    text(s,a,x,3.27,1.40,0.24,13,ac,True,PP_ALIGN.CENTER)
    text(s,b,x,3.68,1.40,0.20,11,INK,align=PP_ALIGN.CENTER)
    if i<3: line(s,x+1.42,3.70,x+1.60,3.70,ac,1.5)
text(s,"权限边界",0.98,4.86,1.2,0.24,12,MUTED,True)
bullet_list(s,["operatorId 对应管理员才可新增 / 删除","管理员目标与批量删除路径明确拒绝","删除前二次确认，失败原因保留在弹窗"],0.98,5.18,6.3,14,INK,0.38)
card(s,8.20,1.90,4.52,4.68,NAVY,True,NAVY)
text(s,"用户黑盒",8.54,2.22,2.0,0.25,13,"8FE4D7",True)
text(s,"7/7",8.54,2.69,2.3,0.70,44,WHITE,True)
text(s,"新增可登录 · 重复名拒绝\n有借阅禁止删 · 归还后可删",8.58,3.50,3.35,0.60,15,"D4E1E2",True)
pill(s,"唯一索引 uk_user_username",8.54,4.49,2.78,TEAL)
text(s,"证据：acceptance/需求4-用户管理验收.md\nverify_user_management_http.py",8.54,5.55,3.45,0.50,11,"B8C7CA")
footer(s, 7)

# 8 visual overview
s = prs.slides.add_slide(blank); add_bg(s); title(s, "07 / REQUIREMENT 5", "需求 5：视觉改造不是换色，而是建立一套工作台语言", "Library Atlas：导航、页面头、卡片、表格、弹窗、反馈与窄屏策略统一")
card(s,0.62,1.90,4.30,4.70,NAVY,True,NAVY)
text(s,"Library Atlas",0.98,2.28,3.0,0.35,24,WHITE,True)
text(s,"深墨蓝导航\n青绿业务强调\n暖灰工作区\n低饱和状态色",0.98,3.10,3.1,1.40,20,"D4E1E2",True)
pill(s,"统一 tokens",0.98,5.42,1.45,TEAL)
card(s,5.22,1.90,7.50,4.70,WHITE,True)
text(s,"四个真实页面作为视觉验收锚点",5.58,2.24,4.8,0.28,19,NAVY,True)
thumbs=[("登录",ROOT/"acceptance/screenshots/after-login.png"),("Dashboard",ROOT/"acceptance/screenshots/after-dashboard.png"),("图书",ROOT/"acceptance/screenshots/after-book.png"),("用户",ROOT/"acceptance/screenshots/after-user.png")]
for i,(label,p) in enumerate(thumbs):
    x=5.58+(i%2)*3.42; y=2.90+(i//2)*1.62
    card(s,x,y,3.02,1.32,"F9FBFA",True,LINE); image_contain(s,p,x+0.10,y+0.12,2.82,0.90,False); text(s,label,x+0.12,y+1.08,2.6,0.18,10,MUTED,True)
text(s,"两档视口：页面级无横向溢出；console error = 0；表格横向滚动被限制在业务区域。",5.60,6.10,6.5,0.30,13,TEAL_DARK,True)
footer(s, 8)

# comparison pages
compare_slide("08 / BEFORE → AFTER", "登录页：从单栏表单到品牌与操作边界", "旧图：视口未记录 · 349×382", "新图：采集视口 1280×800", ROOT/"images/login.png", ROOT/"acceptance/screenshots/after-login.png", "登录动作、品牌信息和表单边界同时可见，投影阅读层级更清楚。", 9)
compare_slide("09 / BEFORE → AFTER", "Dashboard：从统计堆叠到运营工作台", "旧图：视口未记录 · 1614×626", "新图：采集视口 1280×800 · full-page 1280×862", ROOT/"images/dashboard.png", ROOT/"acceptance/screenshots/after-dashboard.png", "指标卡、日期信息与图表形成稳定层级，页面级无横向溢出。", 10)
compare_slide("10 / BEFORE → AFTER", "图书页：库存字段进入主视线", "旧图：视口未记录 · 1821×526", "新图：采集视口 1280×800 · full-page 1280×988", ROOT/"images/book.png", ROOT/"acceptance/screenshots/after-book.png", "馆藏总数与可借数量可直接核对，操作列在窄屏下仍可见。", 11)
compare_slide("11 / BEFORE → AFTER", "用户页：新增读者与删除边界可见", "旧图：视口未记录 · 1584×381", "新图：采集视口 1280×800", ROOT/"images/reader.png", ROOT/"acceptance/screenshots/after-user.png", "新增入口、筛选、表格和操作反馈被收进同一页面语义。", 12)

# 13 evidence
s = prs.slides.add_slide(blank); add_bg(s); title(s, "12 / EVIDENCE", "验收数据与提交记录：每项变化都有可复查证据", "数据来自仓库验收记录与最终提交历史；截图来自真实运行页面")
metrics=[("11/11","核心冒烟","./dev.sh verify",TEAL),("6/6","借还续","verify_circulation_http.py",NAVY),("9/9","库存","verify_inventory_http.py",ORANGE),("6/6","逾期","verify_overdue_http.py",RED),("7/7","用户","verify_user_management_http.py","6C6DE5")]
for i,(v,l,c,ac) in enumerate(metrics): metric(s,0.62+i*2.48,1.86,2.22,v,l,ac); text(s,c,0.74+i*2.48,3.00,1.98,0.28,9,MUTED,align=PP_ALIGN.CENTER)
card(s,0.62,3.62,12.10,2.78,WHITE,True)
text(s,"T1 → T5  提交链",0.96,3.95,2.3,0.28,19,NAVY,True)
commits=[("T1","1745b11","后端化借还续"),("T2","eca083e","库存数量与约束"),("T3","23401f3","逾期管理与限制"),("T4","322e1ce","管理员用户管理"),("T5","48c645d","前端视觉与交互")]
for i,(t,c,d) in enumerate(commits):
    x=0.98+i*2.28
    text(s,t,x,4.52,0.42,0.22,12,TEAL,True)
    text(s,c,x+0.46,4.52,1.25,0.22,11,NAVY,True)
    text(s,d,x,4.91,1.86,0.36,12,INK)
    if i<4: line(s,x+1.90,4.68,x+2.12,4.68,LINE,1.2)
text(s,"Playwright 1280×800 / 1024×768：页面级 scrollWidth = viewport；无 console error。",0.98,5.83,10.7,0.26,13,TEAL_DARK,True)
footer(s, 13)

# 14 conclusion
s = prs.slides.add_slide(blank); add_bg(s, True); title(s, "13 / CLOSING", "边界与总结：完成的是可验证交付，不是无限扩张", "五项需求已分别完成并 push；本 PPT 是独立汇报交付物，不修改业务源码", True)
card(s,0.62,1.94,5.88,4.64,"1E3B4A",True,"35616C")
text(s,"已完成",0.98,2.30,1.5,0.28,18,"8FE4D7",True)
bullet_list(s,["业务规则落到后端事务与数据库约束", "四组真实截图证明视觉变化", "黑盒脚本覆盖成功、失败与数据不变", "两档视口页面级无横向溢出"],0.98,2.86,4.85,16,"D4E1E2",0.72)
card(s,6.82,1.94,5.88,4.64,"1E3B4A",True,"35616C")
text(s,"明确边界",7.18,2.30,1.5,0.28,18,"F4B187",True)
bullet_list(s,["项目仍无统一 token 鉴权拦截器", "旧直写接口保留，正式页面走新流程", "人工浏览器视觉复核仍建议在交付环境补做", "本次不把未完成能力写成完成"],7.18,2.86,4.85,16,"D4E1E2",0.72)
text(s,"结论  ·  五项变化形成一条从规则、数据到体验的证据链。",0.82,6.86,11.65,0.28,18,"8FE4D7",True,PP_ALIGN.CENTER)
footer(s, 14, True)

prs.save(OUT)
print(f"saved {OUT} ({len(prs.slides)} slides)")

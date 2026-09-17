"""learning-materials 资料库自检脚本。

对 learning-materials/ 下的所有 HTML 学习资料，按 concept-learner 技能
第五节「自检要求」逐条做结构化核查，输出一张总表与问题清单。

用法：
    python scripts/audit_materials.py                  # 核查全部页面
    python scripts/audit_materials.py --page xxx.html  # 只查一页
    python scripts/audit_materials.py --links          # 额外探测外链可达性

纯标准库实现，不改动任何文件。
"""

from __future__ import annotations

import argparse
import html as html_mod
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATERIALS = ROOT / "learning-materials"

# 九个必备板块的识别关键词（按规范第一节顺序）
BOARD_KEYS = [
    ("学习目标", ("学习目标",)),
    ("核心问题", ("核心问题",)),
    ("通俗解释", ("通俗解释", "通俗的解释")),
    ("可视化图解", ("可视化图解", "图解")),
    ("核心机制", ("核心机制", "机制", "组成")),
    ("应用场景", ("应用场景",)),
    ("易混与边界", ("易混", "边界")),
    ("自测问题", ("自测",)),
    ("资料来源", ("资料来源", "来源")),
]

SVG_RE = re.compile(r"<svg\b[^>]*>[\s\S]*?</svg>", re.I)
H2_RE = re.compile(r"<h2[^>]*>([\s\S]*?)</h2>", re.I)
QUIZ_RE = re.compile(r'<div class="quiz" data-ans="([^"]*)"')
HREF_RE = re.compile(r'href="([^"]+)"')
TAG_RE = re.compile(r"<[^>]+>")

# 非「概念页」的特殊页面：不套用 9 板块 / 5 题规范
PAGE_KIND = {
    "index.html": ("目录页", None),
}

# 正文中被引号包住的内容不算叙述人称：书名号（来源标题）、直角/弯引号（引语）
QUOTED_RE = re.compile(r"《[^》]*》|「[^」]*」|“[^”]*”|\"[^\"]{0,80}\"")


def text_of(fragment: str) -> str:
    return html_mod.unescape(TAG_RE.sub("", fragment)).strip()


def unquoted(text: str) -> str:
    """把人称检查不该管的引用文字替换成占位符。"""
    return QUOTED_RE.sub(lambda m: " " * len(m.group(0)), text)


def strip_code_and_scripts(doc: str) -> str:
    """去掉 script / style / pre / code，避免代码与脚本干扰人称检查。"""
    for pat in (
        r"<script\b[\s\S]*?</script>",
        r"<style\b[\s\S]*?</style>",
        r"<pre\b[\s\S]*?</pre>",
        r"<code\b[\s\S]*?</code>",
    ):
        doc = re.sub(pat, " ", doc, flags=re.I)
    return doc


def check_page(path: pathlib.Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    body = strip_code_and_scripts(raw)
    body_text = text_of(body)

    kind, min_figs = PAGE_KIND.get(path.name, ("概念页", 2))

    h2s = [text_of(h) for h in H2_RE.findall(raw)]
    boards = []
    for label, keys in BOARD_KEYS:
        hit = any(any(k in h for k in keys) for h in h2s)
        boards.append((label, hit))

    svgs = SVG_RE.findall(raw)
    figures = []
    for s in svgs:
        # 先剔除命名空间声明：xmlns 里的 http:// 不是外部依赖
        bare = re.sub(r'\sxmlns(?::\w+)?="[^"]*"', " ", s)
        figures.append({
            "role": bool(re.search(r'role="img"', bare, re.I)),
            "title": bool(re.search(r"<title\b", bare, re.I)),
            "desc": bool(re.search(r"<desc\b", bare, re.I)),
            "external": bool(
                re.search(r"<image\b|<use\b", bare, re.I)
                or re.search(r'(?:xlink:)?href="https?://', bare, re.I)
                or re.search(r"url\(['\"]?https?://", bare, re.I)
            ),
        })

    quizzes = QUIZ_RE.findall(raw)
    quiz_detail = []
    for m in re.finditer(r'<div class="quiz" data-ans="([^"]*)">([\s\S]*?)(?=<div class="quiz"|$)', raw):
        ans, blk = m.group(1), m.group(2)
        opts = re.findall(r'data-v="([^"]*)"', blk)
        has_src = bool(re.search(r'class="src"', blk))
        ok = re.search(r'data-ok="([^"]*)"', blk)
        quiz_detail.append({
            "ans": ans,
            "n_opts": len(opts),
            "ans_in_opts": ans in opts,
            "has_src": has_src,
            "has_ok": bool(ok),
            # data-ok 由 fb.textContent 渲染，含标签会原样显示
            "ok_has_tag": bool(ok and re.search(r"<[a-zA-Z/]", ok.group(1))),
        })

    # 人称：先遮掉引用文字，再统计；被遮掉的只作为提示
    clean_text = unquoted(body_text)
    first_person = [m.group(0) for m in re.finditer(r"[我]", clean_text)]
    quoted_person = len(re.findall(r"[我]", body_text)) - len(first_person)

    # 站内断链
    broken = []
    for href in HREF_RE.findall(raw):
        if href.startswith(("http", "#", "mailto:", "javascript:")):
            continue
        target = (path.parent / href.split("#")[0]).resolve()
        if href.split("#")[0] and not target.exists():
            broken.append(href)

    externals = sorted({h for h in HREF_RE.findall(raw) if h.startswith("http")})

    return {
        "file": path.name,
        "kind": kind,
        "min_figs": min_figs,
        "bytes": len(raw.encode("utf-8")),
        "h2": h2s,
        "boards": boards,
        "svgs": figures,
        "quizzes": quizzes,
        "quiz_detail": quiz_detail,
        "first_person": first_person,
        "quoted_person": quoted_person,
        "broken": broken,
        "externals": externals,
        "has_header_note": bool(re.search(r"concept-learner", raw, re.I)),
    }


def probe(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*",
    })
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=timeout) as r:
            return str(r.status)
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}"
    except Exception as e:  # 网络类错误统一归类
        return f"ERR {type(e).__name__}"


def main() -> int:
    ap = argparse.ArgumentParser(description="learning-materials 资料库自检")
    ap.add_argument("--page", help="只核查指定文件名，如 functions.html")
    ap.add_argument("--links", action="store_true", help="探测外链可达性（联网）")
    args = ap.parse_args()

    pages = sorted(MATERIALS.glob("*.html"))
    if args.page:
        pages = [p for p in pages if p.name == args.page]
    if not pages:
        print("没有找到待核查页面")
        return 1

    results = [check_page(p) for p in pages]

    print("=" * 104)
    print("资料库自检 · 页面总表")
    print("=" * 104)
    print(f"{'文件':<34}{'类型':<7}{'大小':>7} {'板块':>5} {'图':>3} {'题':>3} {'断链':>5} {'人称':>5} 页头")
    print("-" * 104)
    problems: list[str] = []
    notes: list[str] = []
    for r in results:
        concept = r["kind"] == "概念页"
        n_boards = sum(1 for _, hit in r["boards"] if hit)
        n_bad_svg = sum(1 for f in r["svgs"] if not (f["role"] and f["title"] and f["desc"]))
        n_bad_quiz = sum(1 for q in r["quiz_detail"] if not (q["ans_in_opts"] and q["has_src"]))
        boards_txt = f"{n_boards}/9" if concept else "—"
        quiz_txt = f"{len(r['quizzes'])}" if concept else "—"
        person_txt = str(len(r["first_person"])) if r["first_person"] else "ok"
        print(f"{r['file']:<34}{r['kind']:<7}{r['bytes']:>7} {boards_txt:>5} "
              f"{len(r['svgs']):>3} {quiz_txt:>3} "
              f"{len(r['broken']):>5} {person_txt:>5} "
              f"{'有' if r['has_header_note'] else '缺'}")

        if concept:
            if n_boards < 9:
                miss = [lbl for lbl, hit in r["boards"] if not hit]
                problems.append(f"[板块] {r['file']} 缺 {9 - n_boards} 项：{'、'.join(miss)}")
            if len(r["quizzes"]) != 5:
                problems.append(f"[自测] {r['file']} 题目数 {len(r['quizzes'])}（规范要求 5）")
            n_no_ok = sum(1 for q in r["quiz_detail"] if not q["has_ok"])
            n_tag_ok = sum(1 for q in r["quiz_detail"] if q["ok_has_tag"])
            if n_no_ok:
                problems.append(f"[自测] {r['file']} 有 {n_no_ok} 题缺 data-ok 反馈文案")
            if n_tag_ok:
                problems.append(f"[自测] {r['file']} 有 {n_tag_ok} 题的 data-ok 含 HTML 标签"
                                f"（textContent 渲染会显示为纯文本）")
            if n_bad_quiz:
                problems.append(f"[自测] {r['file']} 有 {n_bad_quiz} 题答案不在选项中或未标来源")
        elif r["min_figs"] is not None and len(r["svgs"]) < r["min_figs"]:
            problems.append(f"[图解] {r['file']} 仅 {len(r['svgs'])} 张 SVG（该类型要求 ≥{r['min_figs']}）")

        if concept and len(r["svgs"]) < 2:
            problems.append(f"[图解] {r['file']} 仅 {len(r['svgs'])} 张 SVG（规范要求 ≥2）")
        if len(r["svgs"]) > 3:
            problems.append(f"[图解] {r['file']} 有 {len(r['svgs'])} 张 SVG（规范要求 ≤3）")
        if n_bad_svg:
            problems.append(f"[图解] {r['file']} 有 {n_bad_svg} 张图缺 role/title/desc")
        for i, f in enumerate(r["svgs"], 1):
            if f["external"]:
                problems.append(f"[图解] {r['file']} 第 {i} 张图含外部依赖（应自包含）")
        if r["first_person"]:
            problems.append(f"[人称] {r['file']} 叙述中出现 \"我\" × {len(r['first_person'])}")
        if r["quoted_person"]:
            notes.append(f"{r['file']}：{r['quoted_person']} 处「我」在引号/书名号内（引用文字，无需改）")
        if r["broken"]:
            problems.append(f"[断链] {r['file']} → {'、'.join(r['broken'])}")
        if not r["has_header_note"]:
            problems.append(f"[页头] {r['file']} 未见 concept-learner 生成标注")

    print()
    print("=" * 104)
    print(f"问题清单（共 {len(problems)} 条）")
    print("=" * 104)
    if problems:
        for p in problems:
            print(" -", p)
    else:
        print(" 无问题，全部达标。")

    if notes:
        print()
        print("说明（不计为问题）")
        for n in notes:
            print(" ·", n)

    if args.links:
        urls = sorted({u for r in results for u in r["externals"]})
        print()
        print("=" * 96)
        print(f"外链可达性探测（{len(urls)} 条）")
        print("=" * 96)
        for u in urls:
            print(f" {probe(u):<14} {u}")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

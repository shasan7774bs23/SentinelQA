"""report-html.py — build the self-contained HTML QA report from the Markdown report.

Usage:
    python report-html.py <report.md> [--name <TICKET-KEY>-QA-Report] [--title "<title>"]

  <report.md>   the finished, audited Markdown report (e.g. qa/ABC-123/05-report.md)
  --name        output base name. Writes <name>.md (an exact copy of the report) and <name>.html
                next to <report.md>. Default: <TICKET>-QA-Report, with <TICKET> taken from the
                case-file folder name (qa/ABC-123/ -> ABC-123).

Why this exists: every team member's HTML report must come out identical, and the HTML rules in
SKILL.md (charset first, light AND dark colour tokens incl. strong/b, no empty <thead>,
overflow-x boxes, the scroll-root pattern with keyboard and wheel fallbacks, every image embedded
as a base64 data URI) were being re-implemented by hand on every run.

Exit 1 if any referenced image is missing or unreadable, or if a non-data image would remain.
Standard library only.
"""
import argparse
import base64
import html
import io
import os
import re
import sys
import urllib.parse

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
        ".webp": "image/webp", ".svg": "image/svg+xml"}

CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0;height:100%}
:root{--bg:#f6f7f9;--fg:#1c2024;--line:#d5d9de;--mut:#5b6472;--accent:#1f5fc9;--code:#eef2f7;
--strong:#0b0d10;--quote:#fff4e5;--quoteline:#b45309;--imgbg:#ffffff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#13161a;--fg:#e6e9ee;
--line:#2f3540;--mut:#a3acb9;--accent:#8ab4ff;--code:#232932;--strong:#ffffff;--quote:#2a2215;
--quoteline:#f59e0b;--imgbg:#ffffff}}
body{overflow:hidden;font:15px/1.55 -apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--fg)}
.scroll-root{height:100vh;height:100dvh;overflow-y:auto;-webkit-overflow-scrolling:touch;outline:none}
.wrap{max-width:1100px;margin:0 auto;padding:28px 16px 80px}
h1{font-size:26px}h2{font-size:21px;margin-top:34px;border-bottom:1px solid var(--line);padding-bottom:4px}
h3{font-size:17px;margin-top:26px}h4{font-size:15px;margin-top:22px}
strong,b{color:var(--strong)}a{color:var(--accent)}em{color:var(--fg)}
code{background:var(--code);color:var(--fg);padding:1px 5px;border-radius:4px;font-size:13px}
pre{background:var(--code);color:var(--fg);padding:12px;border-radius:6px;font-size:12.5px;margin:0}
pre code{padding:0;background:none}
.x{overflow-x:auto;margin:10px 0}
table{border-collapse:collapse;font-size:13.5px}
th,td{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}
th{background:var(--code)}
blockquote{margin:12px 0;padding:10px 16px;background:var(--quote);border-left:4px solid var(--quoteline)}
hr{border:0;border-top:1px solid var(--line);margin:24px 0}
figure{margin:10px 0}
figure img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;background:var(--imgbg)}
figcaption{font-size:12px;color:var(--mut)}
#end-of-report{color:var(--mut);text-align:center;margin-top:40px}
"""

JS = """
(function(){
  var s=document.querySelector(".scroll-root");if(!s)return;
  function f(){try{s.focus({preventScroll:true})}catch(e){s.focus()}}
  f();window.addEventListener("pointerdown",f);
  window.addEventListener("keydown",function(e){
    if(e.defaultPrevented)return;var t=e.target,g=t&&t.tagName;
    if(g==="INPUT"||g==="TEXTAREA"||(t&&t.isContentEditable))return;
    var h=s.clientHeight,k=e.key,d=null;
    if(k==="PageDown")d=h*0.9;else if(k==="PageUp")d=-h*0.9;
    else if(k===" "||k==="Spacebar")d=e.shiftKey?-h*0.9:h*0.9;
    else if(k==="ArrowDown")d=60;else if(k==="ArrowUp")d=-60;
    else if(k==="Home"){s.scrollTo({top:0});e.preventDefault();return}
    else if(k==="End"){s.scrollTo({top:s.scrollHeight});e.preventDefault();return}
    if(d!==null){s.scrollBy({top:d});e.preventDefault()}
  },true);
  window.addEventListener("wheel",function(e){if(!s.contains(e.target)){s.scrollBy({top:e.deltaY});e.preventDefault()}},{passive:false});
})();
"""

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

problems = []
embedded = []

# ![alt](path)  ![alt](<path with spaces>)  ![alt](path "title")
IMG_MD = re.compile(r'!\[([^\]]*)\]\(\s*(?:<([^>\n]+)>|([^)\s]+))(?:\s+"[^"]*")?\s*\)')
IMG_TAG = re.compile(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>', re.I)
TICK_IMG = re.compile(r"`([^`\n]+\.(?:png|jpe?g|gif|webp|svg))`", re.I)


def img_path(m):
    return urllib.parse.unquote((m.group(2) or m.group(3)).strip())


def resolve(base_dir, name):
    """A backticked screenshot name like `TC-01.png` -> its file, if it exists in the case file."""
    for d in ("", "04-evidence", "evidence"):
        p = os.path.join(base_dir, d, name)
        if os.path.isfile(p):
            return os.path.relpath(p, base_dir)
    return None


def data_uri(base_dir, path):
    p = path if os.path.isabs(path) else os.path.join(base_dir, path)
    ext = os.path.splitext(p)[1].lower()
    if ext not in MIME:
        problems.append("unsupported image type: %s" % path)
        return None
    try:
        data = io.open(p, "rb").read()
    except OSError:
        problems.append("image not found: %s" % path)
        return None
    if not data:
        problems.append("image is empty: %s" % path)
        return None
    embedded.append(path)
    return "data:%s;base64,%s" % (MIME[ext], base64.b64encode(data).decode("ascii"))


def inline(t, base_dir):
    codes = []

    def keep_code(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    t = re.sub(r"`([^`]+)`", keep_code, t)
    imgs = []

    def keep_img_parts(alt, path):
        imgs.append((alt, path))
        return "\x01%d\x01" % (len(imgs) - 1)

    t = IMG_MD.sub(lambda m: keep_img_parts(m.group(1), img_path(m)), t)
    t = IMG_TAG.sub(lambda m: m.group(0) if m.group(1).startswith("data:")
                    else keep_img_parts("", urllib.parse.unquote(m.group(1))), t)
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: '<a href="%s">%s</a>' % (html.escape(m.group(2), quote=True), m.group(1)), t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"<em>\1</em>", t)

    def put_img(m):
        alt, path = imgs[int(m.group(1))]
        uri = data_uri(base_dir, path)
        if not uri:
            return "<em>[missing image: %s]</em>" % html.escape(path)
        return '<img alt="%s" src="%s" style="max-width:100%%">' % (html.escape(alt), uri)

    t = re.sub(r"\x01(\d+)\x01", put_img, t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: "<code>%s</code>" % html.escape(codes[int(m.group(1))]), t)
    return t


def split_row(r):
    r = r.strip()
    if r.startswith("|"):
        r = r[1:]
    if r.endswith("|") and not r.endswith("\\|"):
        r = r[:-1]
    cells = re.split(r"(?<!\\)\|", r)
    return [c.strip().replace("\\|", "|") for c in cells]


BLOCK_START = re.compile(r"^(#{1,6}\s|\||!\[.*\]\(.*\)\s*$|<img\b.*>\s*$|```|>|\s*\d+\.\s|\s*[-*+]\s|---\s*$)")

auto_done = set()


def figure(base_dir, alt, path):
    uri = data_uri(base_dir, path)
    if not uri:
        return "<p><em>[missing image: %s]</em></p>" % html.escape(path)
    return '<figure><img alt="%s" src="%s"><figcaption>%s</figcaption></figure>' % (
        html.escape(alt), uri, html.escape(os.path.basename(path)))


def auto_figures(raw, base_dir, linked):
    """A screenshot cited only as `TC-01.png` (never as an image link) is embedded right after the
    block that cites it, so the HTML always shows what the audit counted."""
    figs = []
    for name in TICK_IMG.findall(raw):
        base = os.path.basename(name)
        if base in linked or base in auto_done:
            continue
        rel = resolve(base_dir, name)
        if rel:
            auto_done.add(base)
            figs.append(figure(base_dir, base, rel))
    return figs


def convert(md, base_dir):
    linked = {os.path.basename(img_path(m)) for m in IMG_MD.finditer(md)}
    linked |= {os.path.basename(urllib.parse.unquote(m.group(1))) for m in IMG_TAG.finditer(md)}
    out, lines, i = [], md.replace("\r\n", "\n").split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j, buf = i + 1, []
            while j < len(lines) and not lines[j].startswith("```"):
                buf.append(lines[j])
                j += 1
            out.append('<div class="x"><pre><code>%s</code></pre></div>' % html.escape("\n".join(buf)))
            i = j + 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            n = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (n, inline(m.group(2).strip(), base_dir), n))
            i += 1
            continue
        m = IMG_MD.fullmatch(ln.strip())
        tag = IMG_TAG.fullmatch(ln.strip())
        if m or (tag and not tag.group(1).startswith("data:")):
            alt, path = (m.group(1), img_path(m)) if m else ("", urllib.parse.unquote(tag.group(1)))
            out.append(figure(base_dir, alt, path))
            i += 1
            continue
        if ln.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            cells = [split_row(r) for r in rows]
            has_head = len(cells) > 1 and cells[1] and all(re.match(r"^:?-{1,}:?$", c) for c in cells[1] if c)
            head, body = "", cells
            if has_head:
                body = cells[2:]
                if any(c for c in cells[0]):
                    head = "<thead><tr>%s</tr></thead>" % "".join(
                        "<th>%s</th>" % inline(c, base_dir) for c in cells[0])
            rows_html = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, base_dir) for c in r)
                                for r in body)
            out.append('<div class="x"><table>%s<tbody>%s</tbody></table></div>' % (head, rows_html))
            out.extend(auto_figures("\n".join(rows), base_dir, linked))
            continue
        for pat, tag in ((r"^\s*\d+\.\s", "ol"), (r"^\s*[-*+]\s", "ul")):
            if re.match(pat, ln):
                items = []
                while i < len(lines) and (re.match(pat, lines[i]) or
                                          (items and lines[i].startswith("   ") and lines[i].strip())):
                    if re.match(pat, lines[i]):
                        items.append(re.sub(pat, "", lines[i], count=1))
                    else:
                        items[-1] += "<br>" + lines[i].strip()
                    i += 1
                out.append("<%s>%s</%s>" % (tag, "".join(
                    "<li>%s</li>" % inline(x, base_dir).replace("&lt;br&gt;", "<br>") for x in items), tag))
                out.extend(auto_figures("\n".join(items), base_dir, linked))
                break
        else:
            if ln.startswith(">"):
                buf = []
                while i < len(lines) and lines[i].startswith(">"):
                    buf.append(re.sub(r"^>\s?", "", lines[i]))
                    i += 1
                out.append("<blockquote>%s</blockquote>" % "<br>".join(
                    inline(x, base_dir) for x in buf if x.strip()))
                continue
            if re.match(r"^---\s*$", ln):
                out.append("<hr>")
                i += 1
                continue
            if not ln.strip():
                i += 1
                continue
            buf = []
            while i < len(lines) and lines[i].strip() and not BLOCK_START.match(lines[i]):
                buf.append(lines[i])
                i += 1
            if not buf:            # a line BLOCK_START claims but no branch handled: keep it as text
                buf, i = [lines[i]], i + 1
            out.append("<p>%s</p>" % "<br>".join(inline(x, base_dir) for x in buf))
            out.extend(auto_figures("\n".join(buf), base_dir, linked))
            continue
        continue
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Build the self-contained HTML QA report.")
    ap.add_argument("report")
    ap.add_argument("--name")
    ap.add_argument("--title")
    a = ap.parse_args()
    src = a.report
    if not os.path.isfile(src):
        print("FAIL: report not found: %s" % src)
        return 1
    base_dir = os.path.dirname(os.path.abspath(src))
    md = io.open(src, encoding="utf-8-sig").read()
    ticket = os.path.basename(base_dir)
    name = a.name or ("%s-QA-Report" % ticket)
    title = a.title or ("%s QA Report" % ticket)
    body = convert(md, base_dir)
    doc = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>%s</title><style>%s</style></head><body>'
           '<div class="scroll-root" tabindex="-1"><div class="wrap">%s'
           '<p id="end-of-report">End of report</p></div></div><script>%s</script></body></html>\n') % (
               html.escape(title), CSS, body, JS)
    non_data = re.findall(r'<img[^>]+src="(?!data:)', doc)
    if non_data:
        problems.append("%d image(s) not embedded" % len(non_data))
    prose = re.sub(r"<pre>.*?</pre>|<code>.*?</code>", "", body, flags=re.S)
    if re.search(r"!\[[^\]]*\]\(", prose):
        problems.append("Markdown image syntax left unconverted - check the image link format")
    md_out = os.path.join(base_dir, name + ".md")
    html_out = os.path.join(base_dir, name + ".html")
    if os.path.abspath(md_out) != os.path.abspath(src):
        io.open(md_out, "w", encoding="utf-8", newline="").write(md)
    io.open(html_out, "w", encoding="utf-8", newline="").write(doc)
    print("report-html  %s" % ticket)
    print("-" * 72)
    print("wrote %s" % md_out)
    print("wrote %s  (%d bytes)" % (html_out, len(doc)))
    print("images embedded: %d (distinct files: %d) | non-data images: %d | empty thead: %d" % (
        len(embedded), len(set(embedded)), len(non_data), doc.count("<thead><tr></tr></thead>")))
    for p in problems:
        print("FAIL %s" % p)
    print("-" * 72)
    print("RESULT: %s" % ("FAIL - fix the report or the evidence folder, then rebuild" if problems else "PASS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

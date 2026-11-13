"""Draws the images for the profile README in the look of nisarworks.com.
Run from the repo root: python3 tools/build.py   (needs: pip install fonttools brotli)
Text is drawn as shapes, so the images look the same on every device without loading fonts.
Product names, taglines, colours and status come from tools/products.json."""
import json, os, re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib.instancer import instantiateVariableFont

F = 'tools/fonts/'
def load(name, wght=None):
    f = TTFont(F + name)
    return instantiateVariableFont(f, {'wght': wght}) if wght else f
FONTS = {
    'serif': load('instrument-serif-latin-400-normal.woff2'),
    'italic': load('instrument-serif-latin-400-italic.woff2'),
    'sans': load('geist-latin-wght-normal.woff2', 400),
    'mono': load('geist-mono-latin-wght-normal.woff2', 500),
}
META = {k: (f.getGlyphSet(), f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm) for k, f in FONTS.items()}

def width(s, font, size, track=0):
    gs, cmap, hmtx, upm = META[font]
    return sum(hmtx[cmap.get(ord(c), '.notdef')][0] for c in s) * size / upm + track * max(len(s) - 1, 0)

def text(s, x, y, font, size, fill, anchor='start', track=0, extra=''):
    """One <path> for a run of text. x, y is the baseline start (or middle / end with anchor)."""
    gs, cmap, hmtx, upm = META[font]
    k = size / upm
    w = width(s, font, size, track)
    if anchor == 'middle': x -= w / 2
    if anchor == 'end': x -= w
    pen = SVGPathPen(gs, ntos=lambda v: ('%.1f' % v).rstrip('0').rstrip('.'))
    cx = x
    for c in s:
        g = cmap.get(ord(c), '.notdef')
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        cx += hmtx[g][0] * k + track
    return f'<path d="{pen.getCommands()}" fill="{fill}"{extra}/>'

def wrap(s, font, size, maxw):
    lines, cur = [], ''
    for word in s.split():
        t = (cur + ' ' + word).strip()
        if width(t, font, size) > maxw and cur: lines.append(cur); cur = word
        else: cur = t
    return lines + [cur]

BG, BG2, LINE, INK, MUTED, DIM, AMBER = '#0d0c0a', '#141210', '#2b2823', '#f2ede3', '#a8a092', '#958e80', '#f0a63a'
STATUS = {'released': '#58d08b', 'live': '#58d08b', 'early': AMBER, 'beta': '#a5b4ff', 'testing': '#8ab4ff'}
P = json.load(open('tools/products.json'))

def mix(a, b, t):
    a, b = [int(a[i:i+2], 16) for i in (1, 3, 5)], [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def tile(p, x, y, s=84, cls=''):
    k = s / 84
    return (f'<g transform="translate({x} {y}) scale({k:.3f})"{cls}><rect width="84" height="84" rx="22" fill="{mix("#12110f", p["accent"], .15)}" stroke="{mix(LINE, p["accent"], .5)}" stroke-width="1.4"/>'
            f'<g transform="translate(18 18)" fill="none" stroke="{p["accent"]}" color="{p["accent"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{p["mark"]}</g></g>')

def svg(w, h, body, label, style=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">'
            f'<title>{label}</title>{"<style>" + style + "</style>" if style else ""}{body}</svg>\n')

def header():
    W, H = 1200, 560
    thread = 'M96 96C170 56 228 66 290 100S426 104 452 172 470 294 402 322 300 230 240 268 128 252 100 332 94 444 172 462 306 502 358 462'
    spots = [[290, 100], [452, 172], [402, 322], [240, 268], [100, 332], [172, 462]]
    b = f'<rect width="{W}" height="{H}" rx="28" fill="{BG}"/>'
    b += f'<defs><pattern id="pegs" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="14" cy="14" r="1.1" fill="#34302a"/></pattern><radialGradient id="lamp" cx="78%" cy="0%" r="70%"><stop offset="0" stop-color="{AMBER}" stop-opacity=".16"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient></defs>'
    b += f'<rect width="{W}" height="{H}" rx="28" fill="url(#lamp)"/>'
    # left: brand and headline
    b += f'<circle cx="67" cy="62" r="6.5" fill="{AMBER}"/>' + text('Nisarworks', 84, 68, 'mono', 19, INK)
    b += f'<circle cx="65" cy="158" r="4.5" fill="{AMBER}"/>' + text('NISARWORKS · SOFTWARE BY NISAR AHMAD', 80, 163, 'mono', 13.5, MUTED, track=1.1)
    b += text('Small annoyances,', 58, 256, 'serif', 74, INK)
    b += text('turned into software.', 58, 330, 'italic', 74, AMBER)
    for i, l in enumerate(['A home for the tools I build because', 'I wanted them to exist.']):
        b += text(l, 60, 398 + i * 30, 'sans', 21, MUTED)
    bw = width('nisarworks.com', 'sans', 19) + 78
    b += f'<rect x="60" y="462" width="{bw:.0f}" height="50" rx="25" fill="{AMBER}"/>' + text('nisarworks.com', 86, 493.5, 'sans', 19, '#12100c')
    b += f'<path d="M{60 + bw - 44:.0f} 487h14m-6-6 6 6-6 6" fill="none" stroke="#12100c" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    # right: the workbench
    g = f'<rect x="6" y="6" width="548" height="536" rx="30" fill="{BG2}" stroke="{LINE}"/><rect x="6" y="6" width="548" height="536" rx="30" fill="url(#pegs)"/>'
    g += f'<path d="M28 84C22 44 84 30 92 66S44 112 38 78 96 40 104 76 60 122 52 92 84 78 96 96" fill="none" stroke="{AMBER}" stroke-width="2.4" stroke-linecap="round"/>'
    g += f'<path class="thread" pathLength="1" d="{thread}" fill="none" stroke="{AMBER}" stroke-width="2.4" stroke-linecap="round"/>'
    for i, p in enumerate(P[:6]):
        x, y = spots[i]
        g += tile(p, x - 42, y - 42, cls=f' class="t t{i}"') + text(p['name'], x, y + 62, 'mono', 11.5, MUTED, 'middle')
    g += f'<rect x="316" y="420" width="84" height="84" rx="22" fill="none" stroke="{DIM}" stroke-width="1.4" stroke-dasharray="5 6"/>' + text('?', 358, 475, 'serif', 36, DIM, 'middle')
    g += text('a small annoyance', 26, 150, 'italic', 15, MUTED) + text('next?', 358, 526, 'italic', 15, MUTED, 'middle')
    b += f'<g transform="translate(684 40) scale(.875)">{g}</g>'
    style = ('.thread{stroke-dasharray:1;animation:draw 2.6s cubic-bezier(.5,0,.2,1) .2s backwards}@keyframes draw{from{stroke-dashoffset:1}}'
             '@media (prefers-reduced-motion:reduce){.thread{animation:none}}')
    return svg(W, H, b, 'Nisarworks. Small annoyances, turned into software. A home for the tools Nisar Ahmad builds. nisarworks.com', style)

def card(p):
    W, H = 600, 236
    a = p['accent']
    b = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(BG2, a, .11)}"/><stop offset=".6" stop-color="{BG2}"/></linearGradient></defs>'
         f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="24" fill="url(#g)" stroke="{mix(LINE, a, .28)}" stroke-width="1.5"/>')
    b += tile(p, 28, 28, 52)
    b += text(p['category'].upper(), 94, 59, 'mono', 12.5, MUTED, track=1)
    st = p['status']
    sw = width(st['label'], 'mono', 12.5) + 38
    sx = W - 28 - sw
    b += f'<rect x="{sx:.1f}" y="40" width="{sw:.1f}" height="27" rx="13.5" fill="none" stroke="{LINE}"/><circle cx="{sx + 15:.1f}" cy="53.5" r="3.6" fill="{STATUS.get(st["kind"], DIM)}"/>'
    b += text(st['label'], sx + 26, 58, 'mono', 12.5, MUTED)
    size = 46 if width(p['name'], 'serif', 46) < W - 60 else 40
    b += text(p['name'], 28, 138, 'serif', size, INK)
    b += text(p['tagline'], 28, 174, 'italic', 23, a)
    b += text(p['platformNote'], 28, 208, 'sans', 14.5, MUTED)
    b += text('Explore', W - 54, 208, 'sans', 15, INK, 'end')
    b += f'<path d="M{W - 46} 203h14m-6-6 6 6-6 6" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    return svg(W, H, b, f'{p["name"]}. {p["tagline"]} {st["label"]}. {p["platformNote"]}.')

def loop():
    W, H = 1200, 250
    steps = ['Notice', 'Wonder', 'Build', 'Share', 'Repeat']
    art = ['<path d="M6 40h22q6 0 6-7t6-7 6 7-3 9 9-2h22"/><path d="M40 12v6M31 15l3 5M49 15l-3 5"/>',
           f'<path d="M26 30c0-10 8-16 16-16s14 6 14 13c0 12-14 10-14 22"/><circle cx="42" cy="62" r="2.6" fill="{AMBER}" stroke="none"/>',
           '<rect x="12" y="40" width="22" height="22" rx="3"/><rect x="38" y="40" width="22" height="22" rx="3"/><rect x="25" y="14" width="22" height="22" rx="3"/>',
           '<path d="M14 34v26h40V44"/><path d="M34 40L62 12M44 12h18v18"/>',
           '<path d="M58 30a22 22 0 1 0 4 16"/><path d="M60 14v16H44"/>']
    b = f'<rect width="{W}" height="{H}" rx="28" fill="{BG}"/>'
    b += f'<path d="M120 96H1080" stroke="{AMBER}" stroke-width="2" stroke-dasharray="2 9" stroke-linecap="round"/>'
    for i, s in enumerate(steps):
        x = 120 + i * 240
        b += f'<circle cx="{x}" cy="96" r="50" fill="{BG}" stroke="{mix(LINE, AMBER, .55)}"{" stroke-dasharray=\"5 6\"" if i == 4 else ""}/>'
        b += f'<g transform="translate({x - 29} 67) scale(.8)" fill="none" stroke="{AMBER}" stroke-width="2.9" stroke-linecap="round" stroke-linejoin="round">{art[i]}</g>'
        b += text('0%d' % (i + 1), x, 180, 'mono', 12, AMBER, 'middle') + text(s, x, 218, 'italic', 36, INK, 'middle')
    return svg(W, H, b, 'How it usually goes: notice, wonder, build, share, repeat.')

def quote():
    W, H = 1200, 300
    b = f'<rect width="{W}" height="{H}" rx="28" fill="{BG}"/>'
    b += text('“', 52, 150, 'serif', 150, mix(BG, AMBER, .5))
    b += text('Not every project needs a business plan.', 120, 128, 'serif', 56, INK)
    b += text('Some just need a good question', 120, 192, 'italic', 56, AMBER)
    b += text('and a free evening.', 120, 252, 'italic', 56, AMBER)
    return svg(W, H, b, 'Not every project needs a business plan. Some just need a good question and a free evening.')

os.makedirs('assets', exist_ok=True)
for f in os.listdir('assets'): os.remove('assets/' + f)
out = {'header.svg': header(), 'loop.svg': loop(), 'quote.svg': quote()}
for p in P: out[p['slug'] + '.svg'] = card(p)
for name, s in out.items():
    open('assets/' + name, 'w').write(s); print(name, len(s) // 1024, 'KB')

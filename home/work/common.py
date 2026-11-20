import json,html
LOGO=open('/home/claude/work/logo.svg').read()
NAMES=json.load(open('/home/claude/rev/names.json'))
NAMES.update({'BQDC':'بنك القاهرة','TYCN':'تايكون القابضة','EALR':'العربية لاستصلاح الأراضي','MBEG':'إم بي للهندسة','ELSH':'الشمس للإسكان','AIFI':'أطلس للاستثمار','ICFC':'الدولية للأسمدة','EEII':'العربية للصناعات الهندسية','ISMA':'الإسماعيلية مصر للدواجن','MOSC':'مصر للزيوت والصابون','ACAP':'إيه كابيتال القابضة','RACC':'راية لخدمات مراكز الاتصالات','CNFN':'كونتكت المالية','ALUM':'العربية للألومنيوم','DOMT':'دومتي','IFAP':'الدولية للمحاصيل الزراعية','SPIN':'الإسكندرية للغزل والنسيج','KZPC':'كفر الزيات للمبيدات','UEFM':'مطاحن مصر العليا','SMFR':'سماد مصر (إيجيفرت)','CPCI':'القاهرة للأدوية','UNIT':'المتحدة للإسكان والتعمير','SCTS':'قناة السويس لتوطين التكنولوجيا','RTVC':'رمكو لإنشاء القرى السياحية','EPCO':'مصر للدواجن'})
F='file:///home/claude/work/fonts/'
FONTS=''.join(f"@font-face{{font-family:P;src:url({F}a{w}.woff2);font-weight:{w};unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF,U+200C-200F}}@font-face{{font-family:P;src:url({F}l{w}.woff2);font-weight:{w}}}" for w in (400,600,700,800))
CSS=FONTS+"""
*{box-sizing:border-box}
body{margin:0;font-family:P;color:#1F3A2C;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.paper{background:#EAF6EC repeating-linear-gradient(180deg,transparent 0 41px,#CFE6D4 41px 43px)}
.n{direction:ltr;unicode-bidi:isolate;display:inline-block}
.up{color:#15803D}.dn{color:#B91C1C}.mu{color:#4B6B58}
.tk{direction:ltr;display:inline-block;font-weight:800;border:2px solid #1f3d2b;border-radius:999px;background:#bbf7d0aa;padding:0 9px;margin:0 4px}
.hl{background:linear-gradient(transparent 50%,#fed7aa 50%);padding:0 8px}
.chips{display:flex;justify-content:center;gap:14px}
.chip{direction:ltr;display:flex;align-items:center;gap:8px;font-weight:800;border:2.5px solid #1F3A2C;border-radius:30px;background:#fff9;padding:4px 16px}
.dot{width:30px;height:30px;border-radius:50%;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:17px}
.wm{position:absolute;opacity:.07;pointer-events:none}
"""
def chips(size=22):
    return f'<div class="chips" style="font-size:{size}px"><span class="chip"><span class="dot" style="background:#1877F2">f</span>RAYL</span><span class="chip"><span class="dot" style="background:#000">X</span>@raylcharts</span><span class="chip"><span class="dot" style="background:#15803D">⌂</span>raylcharts.com</span></div>'
def num(x,d=1,sign=False,cls=True):
    s=f"{abs(x):,.{d}f}"
    if sign: s=('+' if x>0 else '−' if x<0 else '')+s
    elif x<0: s='−'+s
    c=('up' if x>0 else 'dn' if x<0 else 'mu') if cls else ''
    return f'<span class="n {c}">{s}</span>'
def name(sym): return html.escape(NAMES[sym])

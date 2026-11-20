import sys,json,html,statistics,datetime,os
sys.path.insert(0,'/home/claude/work');sys.path.insert(0,'/home/claude/sec1120l')
from common import CSS,LOGO
from info import INFO,ORDER,CFG
E=html.escape
IND=json.load(open('/home/claude/sec1120l/ind.json'));[IND[_t].update({_k:_v for _k,_v in dict(MACD=0,SIG=0,ADX=20,K=50,D=50,RSI=50).items() if IND[_t].get(_k) is None}) for _t in IND];FV=json.load(open('/home/claude/sec1120l/fv.json'))
DAYX=json.load(open('/home/claude/secday1120.json'))
T=json.load(open('/home/claude/sec1120l/data/t.json'))
DATES=[datetime.datetime.utcfromtimestamp(x+3*3600) for x in T]
DAYN={6:'الأحد',0:'الاتنين',1:'التلات',2:'الأربع',3:'الخميس'}
SECT=CFG['SECT']
def NOTE(s):
    import re as _r
    bad=_r.compile('أسبوع|الأسبوع|الخميس|جلسة|باعوا|اشتروا|RSI|الستوكاستك|الحد الأعلى|طلع حوالي|طلع \\d')
    out=[]
    for sen in _r.split(r'(?<=\.)\s+',s):
        parts=[p for p in _r.split('،\\s*',sen.rstrip('.')) if p.strip() and not bad.search(p)]
        if parts:
            t='، '.join(parts).strip()
            if t.startswith('وال') or (t.startswith('و') and not t.startswith('وا')): t=t[1:]
            out.append(t+'.')
    return ' '.join(out)
def load(t):
    d=json.load(open(f'/home/claude/sec1120l/data/{t}.json'))
    n=65;c,h,l,v=d['c'][-n:],d['h'][-n:],d['l'][-n:],d['v'][-n:]
    o=[d.get('o0',c[0])]+c[:-1] if 'o' not in d else d['o'][-n:]
    import statistics as _st
    med=_st.median(c);k=0
    while k<len(c) and c[k]<med*0.2: k+=1
    o,c,h,l,v=o[k:],c[k:],h[k:],l[k:],v[k:]
    dt=[datetime.datetime.utcfromtimestamp(x+3*3600) for x in d['t'][-n:]][k:] if 't' in d else DATES[len(DATES)-len(c):]
    return dict(o=o,c=c,h=h,l=l,v=v,off=len(DATES)-len(c),dt=dt)
def f2(x,d=2):
    if x is None: return '—'
    if abs(x)>=1000: return f'{x:,.0f}'
    return f'{x:,.{d}f}'
def pct(x):
    cls='up' if x>0 else 'dn' if x<0 else 'mu'
    return f'<span class="pill {cls}"><span class="n">{x:+.2f}%</span></span>'
def money(x):
    if x is None: return '—'
    if x>=1e9: return f'{x/1e9:,.2f} مليار'
    if x>=1e6: return f'{x/1e6:,.1f} مليون'
    return f'{x/1e3:,.0f} ألف'
# ---------- analytics
def pivots(D,k=3):
    hs,ls=[],[]
    h,l=D['h'],D['l']
    for i in range(k,len(h)-k):
        if h[i]==max(h[i-k:i+k+1]): hs.append((h[i],i))
        if l[i]==min(l[i-k:i+k+1]): ls.append((l[i],i))
    return hs,ls
def levels(t,D,I):
    c=D['c'][-1];atr=I['ATR'];hs,ls=pivots(D)
    n=len(D['c']);i10h=max(range(n-10,n),key=lambda i:D['h'][i]);i10l=min(range(n-10,n),key=lambda i:D['l'][i])
    hs=hs+[(D['h'][i10h],i10h)];ls=ls+[(D['l'][i10l],i10l)]
    for k,nm in (('S20','متوسط 20'),('S50','متوسط 50')):
        if I[k] is None: continue
        (hs if I[k]>c else ls).append((I[k],nm))
    res=sorted([p for p in hs if p[0]>c*1.004],key=lambda p:p[0])
    sup=sorted([p for p in ls if p[0]<c*0.996],key=lambda p:-p[0])
    def merge(L,up):
        out=[]
        for p in L:
            if not out or abs(p[0]-out[-1][0])>max(0.02*c,1.0*atr): out.append(p)
        return out
    res=merge(res,1);sup=merge(sup,0)
    R=[];S=[]
    lb=lambda i,w: i if isinstance(i,str) else f'{w} يوم {D['dt'][i].strftime("%d/%m")}'
    for p,i in res[:2]: R.append((p,lb(i,'قمة')))
    for p,i in sup[:2]: S.append((p,lb(i,'قاع')))
    hi=max(D['h']);lo=min(D['l'])
    while len(R)<2:
        x=(R[-1][0] if R else c)+1.5*atr; R.append((x,'مستوى محسوب (المدى اليومي)') if hi<=c*1.004 or R else (hi,'أعلى سعر في 65 جلسة'))
    while len(S)<2:
        x=(S[-1][0] if S else c)-1.5*atr; S.append((max(x,0.01),'مستوى محسوب (المدى اليومي)'))
    z=lambda p:(p-0.35*atr,p+0.35*atr)
    return [(p,z(p),s) for p,s in R],[(p,z(p),s) for p,s in S]
def score(D,I):
    c=D['c'][-1];wk=c/D['c'][-6]-1
    s=0;why=[]
    if c>I['S20']: s+=1;why.append('فوق متوسط 20')
    else: why.append('تحت متوسط 20')
    if I['S50'] and c>I['S50']: s+=1;why.append('فوق متوسط 50')
    else: why.append('تحت متوسط 50')
    if I['MACD']>I['SIG']: s+=1
    if I['RSI']>50: s+=1
    if wk>0: s+=1
    if I['RSI']>70 or I['K']>90: s-=0.5
    return s,wk
def scen(p):
    u,r,d=p
    return 'صعود' if u-d>=12 else 'نزول' if d-u>=12 else 'تذبذب'
def probs(s):
    up=round(20+s*7);dn=round(45-s*6);up=max(15,min(55,up));dn=max(15,min(45,dn));return up,100-up-dn,dn
# ---------- chart svg
def chart(t,D,I,R,S,W=1100,H=470):
    n=len(D['c']);pad_l,pad_r,pad_t=20,70,20;vh=70;ph=H-vh-50
    hi=max(max(D['h']),R[0][1][1] if R else 0);lo=min(min(D['l']),S[0][1][0] if S else 1e9)
    hi=max(D['h'])*1.0;lo=min(D['l'])
    for p,(a,b),_ in R+S:
        if a>=lo*0.97 and b<=hi*1.06: hi=max(hi,b);lo=min(lo,a)
    rng=hi-lo;hi+=rng*0.04;lo-=rng*0.04
    X=lambda i:pad_l+(i+0.5)*(W-pad_l-pad_r)/n
    Y=lambda p:pad_t+(hi-p)/(hi-lo)*ph
    bw=(W-pad_l-pad_r)/n*0.62
    g=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" style="font-family:P;direction:ltr">']
    g.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
    for k in range(6):
        p=lo+(hi-lo)*k/5;y=Y(p)
        g.append(f'<line x1="{pad_l}" x2="{W-pad_r}" y1="{y:.1f}" y2="{y:.1f}" stroke="#E5EEE7"/><text x="{W-pad_r+6}" y="{y+5:.1f}" font-size="15" fill="#4B6B58">{f2(p)}</text>')
    for p,(a,b),_ in R:
        if b<lo or a>hi: continue
        g.append(f'<rect x="{pad_l}" width="{W-pad_l-pad_r}" y="{Y(min(b,hi)):.1f}" height="{max(2,Y(max(a,lo))-Y(min(b,hi))):.1f}" fill="#FCA5A5" opacity=".35"/>')
    for p,(a,b),_ in S:
        if b<lo or a>hi: continue
        g.append(f'<rect x="{pad_l}" width="{W-pad_l-pad_r}" y="{Y(min(b,hi)):.1f}" height="{max(2,Y(max(a,lo))-Y(min(b,hi))):.1f}" fill="#86EFAC" opacity=".4"/>')
    c=D['c']
    def sma(k): return [None if i<k-1 else sum(c[i-k+1:i+1])/k for i in range(n)]
    for k,col in ((20,'#2563EB'),(50,'#EA580C')):
        s=sma(k);pts=' '.join(f'{X(i):.1f},{Y(v):.1f}' for i,v in enumerate(s) if v is not None)
        if pts: g.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.4"/>')
    vmax=max(D['v']) or 1
    for i in range(n):
        o,cl,h,l=D['o'][i],c[i],D['h'][i],D['l'][i];col='#16A34A' if cl>=o else '#DC2626'
        g.append(f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{Y(h):.1f}" y2="{Y(l):.1f}" stroke="{col}" stroke-width="1.4"/>')
        y1,y2=Y(max(o,cl)),Y(min(o,cl));g.append(f'<rect x="{X(i)-bw/2:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{max(1.2,y2-y1):.1f}" fill="{col}"/>')
        vh_=D['v'][i]/vmax*vh;g.append(f'<rect x="{X(i)-bw/2:.1f}" y="{pad_t+ph+40+vh-vh_:.1f}" width="{bw:.1f}" height="{vh_:.1f}" fill="{col}" opacity=".55"/>')
    # last 5 sessions shade
    g.append(f'<rect x="{X(n-5)-bw:.1f}" y="{pad_t}" width="{X(n-1)-X(n-5)+2*bw:.1f}" height="{ph}" fill="#FDE68A" opacity=".25"/>')
    for i in range(0,n,13):
        g.append(f'<text x="{X(i):.1f}" y="{pad_t+ph+28}" font-size="15" fill="#4B6B58" text-anchor="middle">{D['dt'][i].strftime("%d/%m")}</text>')
    ih=max(range(n),key=lambda i:D['h'][i]);il=min(range(n),key=lambda i:D['l'][i])
    for i,p,dy,lab in ((ih,D['h'][ih],-12,'قمة'),(il,D['l'][il],24,'قاع')):
        g.append(f'<text x="{min(max(X(i),70),W-pad_r-70):.1f}" y="{Y(p)+dy:.1f}" font-size="16" font-weight="700" fill="#1F3A2C" text-anchor="middle">{f2(p)} ({D['dt'][i].strftime("%d/%m")})</text>')
    g.append(f'<line x1="{pad_l}" x2="{W-pad_r}" y1="{Y(c[-1]):.1f}" y2="{Y(c[-1]):.1f}" stroke="#1F3A2C" stroke-dasharray="5,5"/><rect x="{W-pad_r+2}" y="{Y(c[-1])-13:.1f}" width="{pad_r-4}" height="26" rx="6" fill="#1F3A2C"/><text x="{W-pad_r+pad_r/2}" y="{Y(c[-1])+6:.1f}" font-size="15" fill="#fff" text-anchor="middle" font-weight="700">{f2(c[-1])}</text>')
    g.append('</svg>');return ''.join(g)
# ---------- page shell
PCSS=CSS+"""
html,body{width:1240px;margin:0}
.pg{position:relative;width:1240px;height:1754px;padding:34px 48px 26px;display:flex;flex-direction:column;overflow:hidden;page-break-after:always}
.hd{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #1F3A2C;padding-bottom:10px}
.hd .lg{display:flex;align-items:center;gap:12px}.hd svg{height:54px;width:auto}.hd .hh{font-size:19px;font-weight:700;text-align:left;line-height:1.4;color:#1F3A2C}
.hd .at{font-size:19px;font-weight:800;direction:ltr}
.bd{width:1144px}
.ft{margin-top:auto;display:flex;justify-content:space-between;align-items:center;border-top:2px dashed #9bb5a3;padding-top:10px;font-size:18px;font-weight:700;color:#33503f;direction:ltr}
.ft .pn{border:2px solid #1F3A2C;border-radius:50%;width:38px;height:38px;display:flex;align-items:center;justify-content:center}
.sec{background:#fffc;border:2.5px solid #1F3A2C;border-radius:22px;padding:12px 20px 14px;margin-top:16px}
.st{display:inline-block;font-size:29px;font-weight:800;background:#DCF2E1;border:2px solid #1F3A2C;border-radius:16px;padding:2px 18px;margin-bottom:12px}
table{width:100%;border-collapse:collapse;font-size:21px}
th{background:#DCF2E1;padding:7px 10px;text-align:right;font-weight:800;font-size:19px}
td.n{display:table-cell;direction:ltr;text-align:right}
td{padding:7px 10px;border-bottom:1px solid #D7E6DB;font-weight:600;vertical-align:top}
td b{font-weight:800}
.pill{display:inline-block;border-radius:10px;padding:1px 9px;font-weight:800}
.pill.up{background:#BBF7D0;color:#15803D}.pill.dn{background:#FECACA;color:#B91C1C}.pill.mu{background:#E5E7EB;color:#374151}
.tag{display:inline-block;border:2px solid #1F3A2C;border-radius:12px;padding:0 8px;font-size:16px;font-weight:800;white-space:nowrap}
.tag.g{background:#BBF7D0}.tag.r{background:#FECACA}.tag.y{background:#FEF3C7}
ul.b{margin:6px 0;padding-right:28px;font-size:23px;line-height:1.75;font-weight:600}
.kp{display:flex;gap:14px;margin-top:16px}.kp>div{flex:1;background:#fff;border:2.5px solid #1F3A2C;border-radius:16px;text-align:center;padding:8px}
.kp small{display:block;font-size:17px;font-weight:700;color:#33503f}.kp b{font-size:30px;font-weight:800}
.fvb{display:flex;gap:14px}.fvb>div{flex:1;border:2.5px solid #1F3A2C;border-radius:16px;padding:10px 14px;text-align:center}
.fvb .v{font-size:40px;font-weight:800;display:block;direction:ltr}.fvb small{font-size:17px;font-weight:600;display:block;line-height:1.4}
.g1{background:#D6EFD9}.g2{background:#FCE9A8}.g3{background:#D3E4F8}
.note{background:#FEF3C7;border:2px solid #D97706;border-radius:14px;padding:10px 16px;font-size:20px;font-weight:700;line-height:1.6;margin-top:12px}
.warn{background:#FDE2E2;border:2.5px solid #C0392B;border-radius:16px;color:#B91C1C;font-weight:800;padding:12px 18px;font-size:20px;line-height:1.6;margin-top:16px}
.lgd{font-size:17px;font-weight:700;color:#33503f;margin:4px 0 8px}
h1{font-size:50px;font-weight:800;margin:8px 0;line-height:1.3}
.wmk{position:absolute;left:150px;top:700px;opacity:.06;transform:rotate(-12deg);pointer-events:none}.wmk svg{width:900px;height:auto}
"""
PN=[0]
def page(head,body):
    PN[0]+=1
    return f'''<div class="pg paper"><div class="wmk">{LOGO}</div><div class="hd"><div class="lg">{LOGO}<span class="at">@raylcharts</span></div><div class="hh">{head}<br>تحديث بتاريخ 20/11/2026 • إقفال الخميس 19 نوفمبر 2026</div></div>
<div class="bd">{body}</div>
<div class="ft"><span class="pn">{PN[0]}</span><span>f RAYL</span><span>X @raylcharts</span><span>raylcharts.com</span><span>#بورصة_بجد</span></div></div>'''
WARN='تنويه: تقسيم القطاع والأسهم حسب تطبيق ثندر (Thndr). تحذير مهم: كون السهم أقل من السعر العادل أو المتحفظ، أو قريب منهم، مش معناه إنه مناسب للشراء. الشراء في الوقت الحالي خطر. ادرس السهم من كل الجوانب (الفنية والأساسية والمالية)، وكون مستعد لو السهم نزل.'
# ---------- per stock
ALL={}
for t in ORDER:
    D=load(t);I=IND[t];inf=INFO[t];fv=FV.get(t)
    c=D['c'][-1];R,S=levels(t,D,I);s,wk=score(D,I);pu,pr,pd=probs(s)
    day=DAYX[t]/100 if t in DAYX else c/D['c'][-2]-1;val5=sum(D['c'][i]*D['v'][i] for i in range(-5,0))
    hi65=max(D['h']);fromhi=c/hi65-1
    ALL[t]=dict(D=D,I=I,c=c,R=R,S=S,s=s,wk=wk,p=(pu,pr,pd),day=day,val5=val5,fromhi=fromhi,fv=fv)
def stock_pages(t):
    A=ALL[t];D,I,c,R,S=A['D'],A['I'],A['c'],A['R'],A['S'];inf=INFO[t];fv=A['fv'];usd=I.get('usd')
    cur='دولار' if usd else 'جنيه'
    head=f'تقرير قطاع {SECT} • {E(inf["name"])} ({t})'
    pe=(c/fv['eps']) if fv and fv['eps']>0 else None
    v20=sum(D['v'][-20:])/20;vr=D['v'][-1]/v20 if v20 else 0
    # bullets
    b=[f'السهم قفل <b class="n">{f2(c)}</b> {cur} يوم الخميس 19/11 (<b class="n">{A["day"]*100:+.2f}%</b> في اليوم، و<b class="n">{A["wk"]*100:+.2f}%</b> في أسبوع 15–19 نوفمبر).']
    b.append(f'قيمة التداول في الأسبوع حوالي <b>{money(A["val5"])}</b> {cur}، وحجم آخر جلسة <b class="n">×{vr:.1f}</b> من متوسط 20 جلسة.')
    b.append(f'السعر {"فوق" if c>I["S20"] else "تحت"} متوسط 20 (<span class="n">{f2(I["S20"])}</span>) {("و"+("فوق" if c>I["S50"] else "تحت")+" متوسط 50 (<span class=\"n\">"+f2(I["S50"])+"</span>)") if I["S50"] else " (ملهوش متوسط 50 لسه: سهم جديد)"}، وبعيد <b class="n">{A["fromhi"]*100:.1f}%</b> عن أعلى سعر في آخر 65 جلسة.')
    if fv:
        g=(1-c/fv['fv'])*100 if c<=fv['fv'] else -(c/fv['fv']-1)*100
        b.append((f'مكرر الربحية <b class="n">{pe:.1f}</b>' if pe else 'الشركة خسرانة في آخر 12 شهر (التقييم على القيمة الدفترية)')+f'، والسعر العادل في تقرير القيم العادلة <b class="n">{f2(fv["fv"])}</b> ({"أرخص منه بـ" if g>0 else "أغلى منه بـ"} <b class="n">{abs(g):.0f}%</b>).')
    else: b.append('السهم ما اتقيّمش في تقرير القيم العادلة (البيانات المالية المنشورة مش كفاية'+(' والسهم بالدولار' if usd else '')+').')
    b.append(f'توقعنا للأسبوع الجاي: <b>{scen(A["p"])}</b> هو السيناريو الأقرب ({A["p"][0]}% صعود • {A["p"][1]}% تذبذب • {A["p"][2]}% نزول).')
    kp=f'''<div class="kp"><div><small>الإقفال</small><b class="n">{f2(c)}</b></div><div><small>اليوم</small><b>{pct(A["day"]*100)}</b></div><div><small>الأسبوع</small><b>{pct(A["wk"]*100)}</b></div><div><small>من القمة (65 جلسة)</small><b>{pct(A["fromhi"]*100)}</b></div></div>'''
    p1=f'''<div style="display:flex;justify-content:space-between;align-items:center;margin-top:20px"><div><h1>{E(inf["name"])}</h1><div style="font-size:22px;font-weight:700;color:#33503f">{E(inf["en"])} • قطاع {SECT} • {E(I["ind"])}</div></div>
<div style="width:150px;height:150px;border-radius:50%;background:#FDE68A;border:4px solid #1F3A2C;display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:800;direction:ltr">{t}</div></div>{kp}
<div class="sec"><span class="st">📌 الخلاصة</span><ul class="b">{"".join(f"<li>{x}</li>" for x in b)}</ul></div>
<div class="sec"><span class="st">🏢 الشركة بتعمل إيه؟</span><table><tr><th style="width:28%">البند</th><th>البيان</th></tr>
<tr><td><b>الاسم</b></td><td>{E(inf["name"])} • {t}</td></tr><tr><td><b>النشاط</b></td><td>{E(inf["act"])}</td></tr>
<tr><td><b>القيمة السوقية</b></td><td>{money(I["mcap"])+" جنيه" if I.get("mcap") else "—"}</td></tr><tr><td><b>عدد الأسهم</b></td><td>{(f2(I["sh"]/1e6,1)+" مليون سهم") if I.get("sh") else "—"}</td></tr>
<tr><td><b>عملة التداول</b></td><td>{"دولار أمريكي" if usd else "جنيه مصري"}</td></tr></table></div>'''
    # page2 results + valuation
    rr=''.join(f'<tr><td><b>{E(a)}</b></td><td><b>{E(b_)}</b></td><td>{E(c_)}</td></tr>' for a,b_,c_ in inf['res'])
    vt=[]
    if pe: vt.append(('مكرر الربحية',f'{pe:.1f}','السعر ÷ ربح السهم آخر 12 شهر'))
    if I.get('eq') and I.get('sh'): vt.append(('السعر / القيمة الدفترية',f'{c/(I["eq"]/I["sh"]):.2f}',f'الدفترية للسهم {f2(I["eq"]/I["sh"])} جنيه'))
    if I.get('debt') is not None and I.get('eq'): vt.append(('الديون / حقوق الملكية',f'{I["debt"]/I["eq"]:.2f}',f'ديون {money(I["debt"])} مقابل {money(I["eq"])}'))
    if I.get('cr'): vt.append(('السيولة الجارية',f'{I["cr"]:.2f}','الأصول المتداولة ÷ الالتزامات المتداولة'))
    if fv and fv.get('roe2'): vt.append(('العائد على حقوق الملكية',f'{fv["roe2"]*100:.0f}%','ربح 12 شهر ÷ حقوق الملكية'))
    vtab=''.join(f'<tr><td><b>{a}</b></td><td><span class="n"><b>{b_}</b></span></td><td>{c_}</td></tr>' for a,b_,c_ in vt) or '<tr><td colspan=3>مفيش بيانات كفاية</td></tr>'
    if fv:
        F=fv['f'];ch=''
        if False: ch=f'<div class="note">العادل في تقرير 3/11 كان <b class="n">{f2(fv["oldfv"])}</b>، ودلوقتي <b class="n">{f2(fv["fv"])}</b> (<span class="n">{(fv["fv"]/fv["oldfv"]-1)*100:+.0f}%</span>) بعد تحديث الأرباح.</div>'
        fvh=f'''<div class="sec"><span class="st">💰 القيمة العادلة (تقرير 12/11)</span><div class="fvb"><div class="g1"><b>المتحفظ</b><span class="v">{f2(fv["c"])}</span><small>{E(F[0])}</small></div><div class="g2"><b>العادل</b><span class="v">{f2(fv["fv"])}</span><small>{E(F[1])}</small></div><div class="g3"><b>المتفائل</b><span class="v">{f2(fv["o"])}</span><small>{E(F[2])}</small></div></div>
<div style="font-size:19px;font-weight:700;margin-top:10px">ربح السهم آخر 12 شهر <b class="n">{f2(fv["eps"],3)}</b> • الفترة: {E(fv["per"])} • مكرر القطاع المستخدم <span class="n">{fv["m"][0]} / {fv["m"][1]} / {fv["m"][2]}</span></div>{ch}</div>'''
    else:
        fvh='<div class="sec"><span class="st">💰 القيمة العادلة</span><div style="font-size:22px;font-weight:700;line-height:1.7">السهم ما اتقيّمش في تقرير القيم العادلة لأن البيانات المالية المنشورة مش كفاية'+(' والسهم متداول بالدولار' if usd else '')+'. فهنعتمد في التقرير ده على التحليل الفني بس.</div></div>'
    p2=f'''<div class="sec"><span class="st">📊 النتايج المعلنة</span><table><tr><th>البند</th><th>الرقم</th><th>ملاحظة</th></tr>{rr}</table>{('<div class="note">💡 '+E(NOTE(inf["note"]))+'</div>') if NOTE(inf["note"]) else ""}</div>
<div class="sec"><span class="st">🏦 الديون والتقييم</span><table><tr><th>المؤشر</th><th>القيمة</th><th>الشرح</th></tr>{vtab}</table></div>{fvh}'''
    # page3 chart + week + MAs
    wk=''
    for i in range(-5,0):
        cc=D['c'][i];pc=D['c'][i-1];dt=D['dt'][i]
        dch=(A['day']*100) if i==-1 else (cc/pc-1)*100
        wk+=f'<tr><td><b>{DAYN.get(dt.weekday(),"")} {dt.strftime("%d/%m")}</b></td><td class="n">{f2(D["o"][i])}</td><td class="n">{f2(D["h"][i])}</td><td class="n">{f2(D["l"][i])}</td><td class="n"><b>{f2(cc)}</b></td><td>{pct(dch)}</td><td class="n">{f2(D["v"][i]/1e3,0)} ألف</td></tr>'
    ma=''
    for nm,k,lab in (('SMA 20','S20','قصير (شهر)'),('SMA 50','S50','متوسط (شهرين ونص)'),('SMA 100','S100','طويل (5 شهور)')):
        v=I[k]
        if v is None:
            ma+=f'<tr><td><b class="n">{nm}</b><br><small>{lab}</small></td><td>—</td><td>—</td><td>—</td><td>ملهوش متوسط لسه (سهم جديد)</td></tr>';continue
        d=(c/v-1)*100;up=c>v
        ma+=f'<tr><td><b class="n">{nm}</b><br><small>{lab}</small></td><td class="n">{f2(v)}</td><td>{pct(d)}</td><td><span class="tag {"g" if up else "r"}">{"فوقه" if up else "تحته"}</span></td><td>{"السعر أعلى من المتوسط = الاتجاه ده في صالح الشراء" if up else "السعر أقل من المتوسط = الاتجاه ده لسه ضعيف"}</td></tr>'
    p3=f'''<div class="sec"><span class="st">📈 شارت السهم: آخر 65 جلسة</span><div class="lgd">شموع يومية • <span style="color:#2563EB">━ متوسط 20</span> • <span style="color:#EA580C">━ متوسط 50</span> • <span style="color:#DC2626">■ مقاومة</span> • <span style="color:#16A34A">■ دعم</span> • الأصفر = الأسبوع اللي فات</div>{chart(t,D,I,R,S)}</div>
<div class="sec"><span class="st">🗓️ أداء الأسبوع (15–19 نوفمبر)</span><table><tr><th>اليوم</th><th>فتح</th><th>أعلى</th><th>أقل</th><th>إقفال</th><th>التغير</th><th>الحجم</th></tr>{wk}</table>
<div style="font-size:20px;font-weight:700;margin-top:8px">حصيلة الأسبوع: {pct(A["wk"]*100)} • أعلى سعر في الأسبوع <span class="n">{f2(max(D["h"][-5:]))}</span> وأقل سعر <span class="n">{f2(min(D["l"][-5:]))}</span></div></div>
<div class="sec"><span class="st">📐 المتوسطات المتحركة</span><table><tr><th>المتوسط</th><th>القيمة</th><th>السعر مقارنة بيه</th><th>الإشارة</th><th>يعني إيه</th></tr>{ma}</table></div>'''
    # page4 indicators + SR + scenarios
    rsi=I['RSI'];rs=('تشبع شراء','r') if rsi>70 else ('تشبع بيع','g') if rsi<30 else ('إيجابي','g') if rsi>55 else ('سلبي','r') if rsi<45 else ('محايد','y')
    mc=('إيجابي','g') if I['MACD']>I['SIG'] else ('سلبي','r')
    adx=('اتجاه قوي','g') if I['ADX']>25 else ('مفيش اتجاه واضح','y')
    st=('تشبع شراء','r') if I['K']>80 else ('تشبع بيع','g') if I['K']<20 else ('محايد','y')
    bbp=(c-I['BBL'])/(I['BBU']-I['BBL']) if I['BBU']>I['BBL'] else .5
    bb=('قريب من الحد العلوي','r') if bbp>0.85 else ('قريب من الحد السفلي','g') if bbp<0.15 else ('جوه النطاق','y')
    atrp=I['ATR']/c*100
    ind=[('RSI (14)','مؤشر القوة النسبية',f'{rsi:.1f}',rs,'بيقيس سرعة الصعود والنزول. فوق 70 تشبع شراء، تحت 30 تشبع بيع.'),
         ('MACD','الماكد',f'{I["MACD"]:.3f} / {I["SIG"]:.3f}',mc,'لو خط الماكد فوق خط الإشارة يبقى الزخم بيتحسن.'+(' والاتنين لسه تحت الصفر.' if I['MACD']<0 and I['SIG']<0 else '')),
         ('ADX','قوة الاتجاه',f'{I["ADX"]:.1f}',adx,'فوق 25 يعني فيه اتجاه قوي (صاعد أو نازل)، تحت 20 مفيش اتجاه.'),
         ('Stochastic','ستوكاستك',f'{I["K"]:.0f} / {I["D"]:.0f}',st,'بيقارن الإقفال بمدى آخر 14 جلسة. فوق 80 تشبع شراء.'),
         ('Bollinger Bands','نطاقات بولينجر',f'{f2(I["BBL"])} – {f2(I["BBU"])}',bb,'الخروج من النطاق بيدل على حركة أقوى من العادي.'),
         ('ATR (14)','متوسط المدى الحقيقي',f'{f2(I["ATR"],3)} ({atrp:.1f}%)',('تذبذب عالي','r') if atrp>4 else ('تذبذب عادي','y'),'متوسط حركة السهم اليومية، وبيحدد مسافة وقف الخسارة.')]
    it=''.join(f'<tr><td><b class="n">{a}</b><br><small>{b_}</small></td><td class="n"><b>{v}</b></td><td><span class="tag {cl}">{tx}</span></td><td style="font-size:18px">{w}</td></tr>' for a,b_,v,(tx,cl),w in ind)
    sr=''.join(f'<tr><td><b>مقاومة {k+1}</b></td><td class="n">{f2(z[0])} – {f2(z[1])}</td><td>{E(src)}</td></tr>' for k,(p,z,src) in reversed(list(enumerate(R))))
    sr+=f'<tr style="background:#FEF3C7"><td><b>الإقفال</b></td><td class="n"><b>{f2(c)}</b></td><td></td></tr>'
    sr+=''.join(f'<tr><td><b>دعم {k+1}</b></td><td class="n">{f2(z[0])} – {f2(z[1])}</td><td>{E(src)}</td></tr>' for k,(p,z,src) in enumerate(S))
    pu,pr,pd=A['p'];r1,s1=R[0],S[0];r2,s2=R[1],S[1]
    r2=(max(r2[0],r1[1][1]+I['ATR']),)+r2[1:];s2=(min(s2[0],s1[1][0]-I['ATR']),)+s2[1:]
    sc=f'''<tr><td>🟢 <b>صعود</b></td><td><b>{pu}%</b></td><td class="n">{f2(r1[1][1])} – {f2(r2[0])}</td><td>إقفال فوق <span class="n">{f2(r1[1][1])}</span> بحجم أعلى من المتوسط</td></tr>
<tr><td>⚪ <b>تذبذب</b></td><td><b>{pr}%</b></td><td class="n">{f2(s1[1][0])} – {f2(r1[1][1])}</td><td>حركة بين الدعم الأول والمقاومة الأولى</td></tr>
<tr><td>🔴 <b>نزول</b></td><td><b>{pd}%</b></td><td class="n">{f2(s2[0])} – {f2(s1[1][0])}</td><td>إقفال تحت <span class="n">{f2(s1[1][0])}</span></td></tr>'''
    p4=f'''<div class="sec"><span class="st">🧭 المؤشرات الفنية</span><table><tr><th>المؤشر</th><th>القيمة</th><th>الحالة</th><th>الشرح</th></tr>{it}</table></div>
<div class="sec"><span class="st">🧱 الدعم والمقاومة</span><table><tr><th>المستوى</th><th>المنطقة</th><th>جاية منين</th></tr>{sr}</table></div>
<div class="sec"><span class="st">🔮 توقعاتنا للأسبوع الجاي (22–26 نوفمبر)</span><table><tr><th>السيناريو</th><th>الاحتمال</th><th>النطاق</th><th>اللي يأكده</th></tr>{sc}</table>
<div class="note">⚠️ النسب دي تقدير رايل للأسبوع الجاي بس، مش مضمونة. السيناريو بيتلغي لو السهم قفل برا النطاق بتاعه.</div></div>'''
    return [page(head,p1),page(head,p2),page(head,p3),page(head,p4)]
# ---------- sector pages
def sector_pages():
    head=f'تقرير قطاع: {SECT}'
    rows=[ALL[t] for t in ORDER]
    egp=[t for t in ORDER if not IND[t].get('usd')]
    up=sum(1 for t in ORDER if ALL[t]['wk']>0);dn=sum(1 for t in ORDER if ALL[t]['wk']<0)
    tv=sum(ALL[t]['val5'] for t in egp)
    pes=[ALL[t]['c']/FV[t]['eps'] for t in FV if FV[t]['eps']>0]
    mcap=sum(IND[t]['mcap'] for t in FV);earn=sum(FV[t]['ttm']*1e6 for t in FV)
    capw=[t for t in egp if IND[t].get('mcap')];wavg=sum(ALL[t]['wk']*IND[t]['mcap'] for t in capw)/sum(IND[t]['mcap'] for t in capw)*100
    best=max(egp,key=lambda t:ALL[t]['wk']);worst=min(egp,key=lambda t:ALL[t]['wk'])
    rank=sorted(ORDER,key=lambda t:-(ALL[t]['p'][0]-ALL[t]['p'][2]))
    kp=f'<div class="kp"><div><small>عدد الأسهم</small><b class="n">{len(ORDER)}</b></div><div><small>أداء الأسبوع (مرجّح بالقيمة السوقية)</small><b>{pct(wavg)}</b></div><div><small>طلع / نزل</small><b class="n">{up} / {dn}</b></div><div><small>قيمة تداول الأسبوع</small><b style="font-size:24px">{money(tv)}</b></div></div>'
    bl=[f'القطاع فيه {len(ORDER)} أسهم، {CFG["big"]}، وقيمة تداول الأسبوع (15–19 نوفمبر) حوالي <b>{money(tv)}</b> جنيه.',
        f'في الأسبوع: {("سهم واحد طلع" if up==1 else str(up)+" أسهم طلعت")} و{("سهم واحد نزل" if dn==1 else "مفيش سهم نزل" if dn==0 else str(dn)+" نزلت")}. الأحسن <b>{E(INFO[best]["name"])}</b> (<span class="n">{ALL[best]["wk"]*100:+.1f}%</span>) {"والأقل صعودا" if ALL[worst]["wk"]>0 else "والأضعف"} <b>{E(INFO[worst]["name"])}</b> (<span class="n">{ALL[worst]["wk"]*100:+.1f}%</span>).',
        f'مكرر ربحية القطاع (القيمة السوقية ÷ الأرباح للشركات المتقيّمة) حوالي <b class="n">{mcap/earn:.1f}</b> مرة، والوسيط <b class="n">{statistics.median(pes):.1f}</b>، مقابل حوالي <b class="n">16.4</b> لوسيط السوق كله.',
        CFG['res'],
        
        f'الأقرب للصعود الأسبوع الجاي حسب المؤشرات: <b>{E(INFO[rank[0]]["name"])}</b> و<b>{E(INFO[rank[1]]["name"])}</b>، والأضعف <b>{E(INFO[rank[-1]]["name"])}</b>.']
    capt=[t for t in egp if IND[t].get('mcap')];totc=sum(IND[t]['mcap'] for t in capt) or 1
    topc=max(capt,key=lambda t:IND[t]['mcap']) if capt else ORDER[0]
    ab=sum(1 for t in ORDER if ALL[t]['c']>IND[t]['S20'])
    osd=[t for t in ORDER if (IND[t]['RSI'] or 50)<35];obt=[t for t in ORDER if (IND[t]['RSI'] or 50)>70 or (IND[t]['K'] or 50)>88]
    OUT=[f'{E(INFO[topc]["name"])} بتمثل حوالي <b class="n">{IND[topc]["mcap"]/totc*100:.0f}%</b> من القيمة السوقية للقطاع، فهي اللي بتحدد اتجاهه.',
         f'<b class="n">{ab}</b> من <b class="n">{len(ORDER)}</b> أسهم قافلين فوق متوسط 20 يوم.']
    if osd: OUT.append('أسهم واقعة زيادة (RSI تحت 35) وممكن ترتد: '+'، '.join(f'<b>{E(INFO[t]["name"])}</b>' for t in osd[:5])+'.')
    if obt: OUT.append('أسهم سخنة وممكن تجني أرباح: '+'، '.join(f'<b>{E(INFO[t]["name"])}</b>' for t in obt[:5])+'.')
    s1=f'''<div style="margin-top:40px;text-align:center"><div style="display:inline-block;background:#FED7AA;border-radius:18px;padding:6px 30px"><h1 style="font-size:62px;margin:0">تقرير قطاع {SECT}</h1></div>
<div style="font-size:26px;font-weight:700;color:#33503f;margin-top:14px">{CFG['SUB']} • {len(ORDER)} أسهم • إقفال الخميس 19 نوفمبر 2026</div>
<div style="font-size:24px;font-weight:800;margin-top:10px;display:inline-block;border:2.5px solid #1F3A2C;border-radius:14px;padding:4px 20px">التوقعات صالحة للأسبوع الجاي بس: 22–26 نوفمبر 2026</div>
<div style="font-size:21px;font-weight:700;color:#33503f;margin-top:10px">ℹ️ تنويه: تقسيم القطاع والأسهم اللي فيه حسب تطبيق ثندر (Thndr)</div></div>{kp}
<div class="sec"><span class="st">📌 الخلاصة</span><ul class="b">{"".join(f"<li>{x}</li>" for x in bl)}</ul></div>
<div class="sec"><span class="st">📚 في التقرير ده</span><ul class="b"><li>جدول مقارنة لكل أسهم القطاع: الأداء، والسيولة، ومكرر الربحية، والقيمة العادلة.</li><li>توقعات القطاع والأسهم للأسبوع الجاي، وترتيب الأسهم من الأقوى للأضعف.</li><li>4 صفحات لكل سهم: الخلاصة والنشاط، والنتايج والتقييم، والشارت وأداء الأسبوع، والمؤشرات والدعم والمقاومة والسيناريوهات.</li></ul></div>'''
    tb=''
    for t in ORDER:
        A=ALL[t];fv=FV.get(t);usd=IND[t].get('usd')
        pe=(f'{A["c"]/fv["eps"]:.1f}' if fv['eps']>0 else 'خسرانة') if fv else '—'
        gp='—'
        if fv:
            x=A['c']/fv['fv']-1;gp=(f'<span class="pill up">أرخص {abs(x)*100:.0f}%</span>' if x<0 else f'<span class="pill dn">أغلى {x*100:.0f}%</span>')
        tb+=f'<tr><td><b>{E(INFO[t]["name"])}</b><br><small class="n">{t}{" • بالدولار" if usd else ""}</small></td><td class="n"><b>{f2(A["c"])}</b></td><td>{pct(A["wk"]*100)}</td><td>{money(A["val5"])}</td><td class="n">{pe}</td><td class="n">{f2(fv["c"]) if fv else "—"}</td><td class="n" style="background:#FEF3C7">{f2(fv["fv"]) if fv else "—"}</td><td class="n">{f2(fv["o"]) if fv else "—"}</td><td>{gp}</td></tr>'
    s2=f'''<div class="sec"><span class="st">🧾 جدول مقارنة أسهم القطاع</span><table style="font-size:18px"><tr><th>السهم</th><th>إقفال 19/11</th><th>الأسبوع</th><th>قيمة تداول الأسبوع</th><th>مكرر الربحية</th><th>المتحفظ</th><th>العادل</th><th>المتفائل</th><th>السعر مقابل العادل</th></tr>{tb}</table>
<div style="font-size:17px;font-weight:600;margin-top:8px">القيمة العادلة من تحديث رايل حتى إقفال 12/11/2026. الأسهم اللي مكتوب قدامها «—» ما اتقيّمتش لأن بياناتها المالية المنشورة مش كفاية.</div></div>'''
    # weekly bar chart
    mx=max(abs(ALL[t]['wk']) for t in ORDER)*100 or 1
    bars=''.join(f'<div style="display:flex;align-items:center;gap:12px;margin:4px 0;font-size:18px;font-weight:700"><span style="width:300px">{E(INFO[t]["name"])}</span><div style="flex:1;display:flex;direction:ltr"><div style="width:50%;display:flex;justify-content:flex-end">{"" if ALL[t]["wk"]>=0 else f"<div style=\"height:20px;width:{abs(ALL[t][chr(119)+chr(107)])*100/mx*100:.0f}%;background:#F87171;border-radius:6px 0 0 6px\"></div>"}</div><div style="width:50%;border-left:2px solid #1F3A2C">{"" if ALL[t]["wk"]<0 else f"<div style=\"height:20px;width:{ALL[t][chr(119)+chr(107)]*100/mx*100:.0f}%;background:#4ADE80;border-radius:0 6px 6px 0\"></div>"}</div></div><span class="n" style="width:90px">{ALL[t]["wk"]*100:+.1f}%</span></div>' for t in sorted(ORDER,key=lambda t:-ALL[t]['wk']))
    s2+=f'<div class="sec"><span class="st">🗓️ أداء الأسبوع (15–19 نوفمبر)</span>{bars}</div>'
    rk=''
    for i,t in enumerate(rank):
        A=ALL[t];pu,pr,pd=A['p'];R,S=A['R'],A['S'];lab_=scen(A["p"])
        rk+=f'<tr><td><b class="n">{i+1}</b></td><td><b>{E(INFO[t]["name"])}</b></td><td><span class="tag {"g" if lab_=="صعود" else "r" if lab_=="نزول" else "y"}">{lab_}</span></td><td class="n">{pu}% / {pr}% / {pd}%</td><td class="n">{f2(S[0][1][0])}</td><td class="n">{f2(R[0][1][1])}</td></tr>'
    upw=sum(ALL[t]['p'][0] for t in egp)/len(egp);dnw=sum(ALL[t]['p'][2] for t in egp)/len(egp)
    sv='تذبذب مع ميل للصعود' if upw>dnw+5 else 'تذبذب مع ميل للنزول' if dnw>upw+5 else 'تذبذب في نطاق'
    s3=f'''<div class="sec"><span class="st">🔮 توقعات القطاع للأسبوع الجاي (22–26 نوفمبر)</span><div style="font-size:24px;font-weight:700;line-height:1.75">
السيناريو الأقرب للقطاع: <span class="y" style="background:#FDE68A;padding:0 8px">{sv}</span>. متوسط احتمال الصعود لأسهم القطاع <b class="n">{upw:.0f}%</b> مقابل <b class="n">{dnw:.0f}%</b> للنزول.<br>
{"".join("• "+x+"<br>" for x in OUT)}</div></div>
<div class="sec"><span class="st">🏁 ترتيب الأسهم للأسبوع الجاي (من الأقوى للأضعف)</span><table><tr><th>#</th><th>السهم</th><th>الأقرب</th><th>صعود / تذبذب / نزول</th><th>الدعم الأول</th><th>المقاومة الأولى</th></tr>{rk}</table>
<div class="note">⚠️ الترتيب مبني على وضع السعر من المتوسطات والزخم وأداء الأسبوع. النسب تقدير رايل للأسبوع الجاي بس، مش مضمونة.</div></div><div class="warn">{WARN}</div>'''
    import re as _re
    def _split(html,n):
        i=html.index('<table');j=html.index('</tr>',i)+5;k=html.rindex('</table>')
        pre,head_,body,post=html[:i],html[i:j],html[j:k],html[k:]
        rows=_re.findall(r'<tr>.*?</tr>',body,flags=_re.S)
        if len(rows)<=n: return [html]
        out=[];sec_open=pre[pre.rindex('<div class="sec">'):]
        for q in range(0,len(rows),n):
            ch=rows[q:q+n]
            if q==0: out.append(pre+head_+''.join(ch)+'</table></div>')
            elif q+n>=len(rows): out.append(sec_open.replace('</span>',' (تكملة)</span>',1)+head_+''.join(ch)+post)
            else: out.append(sec_open.replace('</span>',' (تكملة)</span>',1)+head_+''.join(ch)+'</table></div>')
        return out
    if len(ORDER)>12:
        cut=s2.index('<div class="sec"><span class="st">🗓️')
        A2=_split(s2[:cut],13);bars_=s2[cut:]
        c3=s3.index('<div class="sec"><span class="st">🏁')
        A3=_split(s3[c3:],20)
        return [page(head,s1)]+[page(head,x) for x in A2]+[page(head,bars_),page(head,s3[:c3])]+[page(head,x) for x in A3]
    return [page(head,s1),page(head,s2),page(head,s3)]
pages=sector_pages()
for t in ORDER: pages+=stock_pages(t)
last='<div class="sec" style="margin-top:40px"><span class="st">📎 المصادر والملاحظات</span><ul class="b"><li>تقسيم القطاع والأسهم اللي فيه: حسب تطبيق ثندر (Thndr).</li><li>أسعار الإقفال وتغيّر اليوم: موقع البورصة المصرية، والمؤشرات الفنية: TradingView، إقفال الخميس 19/11/2026.</li><li>النتايج (المنشورة لحد 12/11/2026): إفصاحات الشركات على موقع البورصة المصرية (beta.egx.com.eg) وTradingView.</li><li>القيم العادلة: تحديث رايل للقيم العادلة حتى إقفال 12/11/2026 (raylcharts.com/fairvalue).</li><li>التوقعات للأسبوع الجاي بس (22–26 نوفمبر)، وهنحدّث القطاع ده تاني في دورة القطاعات الجاية.</li></ul></div><div class="warn" style="font-size:24px">'+WARN+'</div>'
pages.append(page(f'تقرير قطاع: {SECT}',last))
doc=f'<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><style>{PCSS}@page{{size:1240px 1754px;margin:0}}</style></head><body>{"".join(pages)}</body></html>'
open('/home/claude/sec1120l/report.html','w').write(doc)
print(len(pages),'pages')
for t in ORDER: A=ALL[t];print(t,round(A['wk']*100,2),A['p'],[round(x[0],2) for x in A['R']],[round(x[0],2) for x in A['S']])

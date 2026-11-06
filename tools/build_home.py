#!/usr/bin/env python3
# يحدّث كروت الصفحة الرئيسية index.html من أحدث عنصر في كل صفحة فرعية.
# التشغيل: python3 tools/build_home.py  (من جذر الموقع) ثم commit + push
import re,os,sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
rd=lambda f:open(f,encoding='utf-8').read()
def first(s,pat,flags=re.S):
    m=re.search(pat,s,flags); return m
def clean(h): return re.sub(r'\s+',' ',re.sub(r'<(?!/?(b|br)\b)[^>]+>','',h)).strip()
home=rd('index.html')
def card(href):
    m=re.search(r'(<section class="card"><h2><a href="%s">.*?</h2>)(.*?)(<a class="more" href="%s">)'%(href,href),home,re.S)
    return m
def setbody(href,body):
    global home
    m=card(href); assert m,href
    home=home[:m.start(2)]+body+home[m.end(2):]
def firstcard(s):
    m=first(s,r'<section class="card[^"]*" id="[^"]+">(.*?)</section>'); return m.group(1)
log=[]
# الأخبار
s=rd('news.html'); c=firstcard(s)
date=clean(first(c,r'📅 ([^<]+)<').group(1))
ps=[clean(p) for p in re.findall(r'<p>(.*?)</p>',c,re.S)]
ps=[p for p in ps if p[:1] in '✅⛔💵🎁⚠' ][:4]
setbody('news.html','<p><b>%s</b></p><ul>%s</ul>'%(date,''.join('<li>%s</li>'%p for p in ps))); log.append('news '+date)
# السوق
s=rd('market.html'); c=firstcard(s)
date=clean(first(c,r'📅 ([^<]+)<').group(1))
title=clean(first(c,r'<h2>(.*?)</h2>').group(1))
p1=first(c,r'<p>(🟢|🔴|🟡)(.*?)</p>')
lines=[clean(x) for x in re.split(r'<br>',p1.group(0)[3:-4])]
setbody('market.html','<p><b>%s</b></p><p><b>%s</b></p>'%(date,title)+''.join('<p>%s%s</p>'%('' if i==0 else '• ',l) for i,l in enumerate(lines))); log.append('market '+date)
# المؤشرات
s=rd('indices.html'); d=first(s,r'<div class="daynav">.*?<a[^>]*>([^<]+)</a>')
last=d.group(1) if d else None
if last:
    home=re.sub(r'آخر يوم: [^.<]*\.','آخر يوم: %s.'%last,home,count=1); log.append('indices '+last)
# التقارير: كل كروت أحدث تاريخ
s=rd('reports.html')
cards=re.findall(r'<section class="card day" id="([^"]+)">(.*?)</section>',s,re.S)
dt=clean(first(cards[0][1],r'📅 ([^<]+)<').group(1))
ts=[]
for i,c in cards:
    if '📅 '+dt not in c: break
    t=clean(first(c,r'<h2>(.*?)</h2>').group(1)); ts.append(t)
setbody('reports.html','<p><b>آخر التقارير (%d):</b> %s</p><p>%s</p>'%(len(ts),' • '.join(ts[:5]),dt)); log.append('reports '+dt)
# حركة الكبار
s=rd('bigmoney.html'); m=first(s,r'<section class="card day" id="[^"]+"><h2>(.*?)</h2><p>(.*?)</p>')
h=clean(m.group(1)).replace('📅 ','')
txt=clean(m.group(2)); 
home=re.sub(r'(<a href="bigmoney.html">.*?</h2><p class="note"[^>]*>.*?</p>)<p>.*?</p>',lambda x:x.group(1)+'<p>آخر %s: %s</p>'%(h.replace('جلسة ','جلسة: '),txt),home,count=1,flags=re.S); log.append('bigmoney '+h)
# التعاملات
s=rd('trades.html'); c=firstcard(s); date=clean(first(c,r'📅 ([^<]+)<').group(1))
tot=clean(first(c,r'<b>([^<]*عملية)</b>.*?<b>([^<]*جنيه)</b>').group(0))
setbody('trades.html','<p>كل سهم اتعمل عليه كام عملية واتداول بكام، يوم بيوم. <b>آخر تحديث: %s</b> — %s.</p>'%(date,tot)); log.append('trades '+date)
# النتايج
s=rd('results.html'); rows=re.findall(r'<tr data-s="[^"]*">(.*?)</tr>',s,re.S)
items=[]
for r in rows[:4]:
    tds=re.findall(r'<td[^>]*>(.*?)</td>',r,re.S)
    nm=clean(first(tds[1],r'<b>(.*?)</b>').group(1)); tk=first(tds[1],r'class="tk">(.*?)<'); 
    items.append('<li><b>%s</b> %s: %s</li>'%(nm,'<span class="tk">%s</span>'%tk.group(1) if tk else '',clean(tds[3])))
n=first(s,r'<small>شركات</small><b>(\d+)</b>').group(1)
setbody('results.html','<ul>%s</ul><p>%s شركة من أول أكتوبر لحد دلوقتي. آخر نتيجة مسجلة: %s.</p>'%(''.join(items),n,clean(re.findall(r'<td[^>]*>(.*?)</td>',rows[0],re.S)[0]))); log.append('results')
# الفيديوهات
s=rd('videos.html'); m=first(s,r'<section class="card" id="[^"]+"><p[^>]*>📅 ([^<]+)</p><h2>(.*?)</h2>')
home=re.sub(r'(<b>آخر فيديو: ).*?(</b>)',lambda x:x.group(1)+clean(m.group(2))+x.group(2),home,count=1); log.append('videos '+m.group(1))
open('index.html','w',encoding='utf-8').write(home)
print('\n'.join(log))

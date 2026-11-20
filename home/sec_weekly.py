#!/usr/bin/env python3
"""تحديث تقارير القطاعات الأسبوعي (رايل). الاستخدام: python3 sec_weekly.py [YYYY-MM-DD لإقفال الخميس] [--publish]"""
import json,sys,datetime,subprocess,os,re,shutil
M=['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']
DIRS={'h':('banks','🏦'),'k':('basic','⛏️'),'i':('realestate','🏢'),'':('tech','💻'),'b':('industrials','🏭'),'g':('food','🍞'),'j':('finance','💼'),'f':('healthcare','💊'),'l':('contracting','🏗️'),'d':('transport','🚢'),'e':('building','🧱'),'c':('education','🎓'),'n':('tourism','🏨'),'r':('distribution','🚚'),'q':('textiles','🧵'),'o':('utilities','⚡'),'m':('energy','🛢️'),'p':('packaging','📦')}
STATE='/home/claude/sec_state.json'
def rng(a,b): return f'{a.day}–{b.day} {M[b.month-1]}' if a.month==b.month else f'{a.day} {M[a.month-1]}–{b.day} {M[b.month-1]}'
def toks(T):
    F=T+datetime.timedelta(1)
    return {'Tfull':f'{T.day}/{T.month}/{T.year}','F':f'{F.day}/{F.month}/{F.year}','Tlong':f'{T.day} {M[T.month-1]} {T.year}',
            'wk':rng(T-datetime.timedelta(4),T),'nx':rng(T+datetime.timedelta(3),T+datetime.timedelta(7)),'T':f'{T.day}/{T.month}','code':f'{T.day:02d}-{T.month:02d}',
            'Fday':f'الجمعة {F.day} {M[F.month-1]} {F.year}'}
ORD=['Tfull','F','Tlong','wk','nx','T']
def sub(text,old,new):
    for i,k in enumerate(ORD): text=text.replace(old[k],f'\x00{i}\x00')
    for i,k in enumerate(ORD): text=text.replace(f'\x00{i}\x00',new[k])
    return text
def main():
    args=[a for a in sys.argv[1:] if not a.startswith('--')]
    if args: T=datetime.date.fromisoformat(args[0])
    else:
        d=datetime.date.today()
        while d.weekday()!=3: d-=datetime.timedelta(1)
        T=d
    st=json.load(open(STATE));old=st['tok'];new=toks(T)
    print('من',old['Tfull'],'إلى',new['Tfull'])
    pub_only=old['Tfull']==new['Tfull'] and '--publish' in sys.argv and st.get('prev') and not st.get('published')
    if old['Tfull']==new['Tfull'] and '--force' not in sys.argv and not pub_only:
        print('ALREADY_UPDATED');return
    if pub_only: old=st['prev']
    bad=[]
    if not pub_only:
     for s in DIRS:
        p=f'/home/claude/sec1120{s}/build.py';b=open(p).read();open(p,'w').write(sub(b,old,new))
    if not pub_only:
     r=subprocess.run(['python3','/home/claude/secfetch_gen.py']+list(DIRS),capture_output=True,text=True)
     print(r.stdout[-1500:],r.stderr[-1500:])
     L=[l.split() for l in r.stdout.splitlines() if len(l.split())==4 and l.split()[2]=='65']
     mx=max(float(x[3]) for x in L) if L else 0
     print('STALE (آخر شمعة أقدم من آخر جلسة):',[x[:2] for x in L if float(x[3])<mx])
     bad=[]
     for s in DIRS:
         d=f'/home/claude/sec1120{s}'
         a=subprocess.run(['python3','build.py'],cwd=d,capture_output=True,text=True)
         if a.returncode: bad.append((s,a.stderr[-400:]));continue
         html=open(f'{d}/report.html').read()
         html=re.sub(r'• 1 أسهم •','• سهم واحد •',html).replace('• 2 أسهم •','• سهمين •').replace('القطاع فيه 2 أسهم، وهم','القطاع فيه سهمين:').replace(' • Thndr<',' • البيانات من ثندر (مش متاح على TradingView)<')
         open(f'{d}/report.html','w').write(html)
         b=subprocess.run(['python3','shot.py'],cwd=d,capture_output=True,text=True)
         if 'overflow []' not in b.stdout: bad.append((s,'overflow '+b.stdout[-200:]))
    print('BAD',bad)
    if '--publish' in sys.argv and not bad:
        site='/home/claude/raylcharts-site';subprocess.run(['git','pull','--rebase','-q'],cwd=site)
        h=open(f'{site}/reports.html').read()
        for s,(slug,ic) in DIRS.items():
            dd=f'{site}/reports/sectors/{slug}'
            for f in os.listdir(dd):
                if f.endswith('.pdf'): os.remove(f'{dd}/{f}')
            shutil.copy(f'/home/claude/sec1120{s}/report.pdf',f'{dd}/RAYL_{slug}_{new["code"]}.pdf')
            shutil.copy(f'/home/claude/sec1120{s}/img/p01.jpg',f'{dd}/p1.jpg');shutil.copy(f'/home/claude/sec1120{s}/img/p02.jpg',f'{dd}/p2.jpg')
            n=len(os.listdir(f'/home/claude/sec1120{s}/img'))
            h=re.sub(rf'(id="sec-{slug}".*?)\(\d+ صفحة\)',lambda m:m.group(1)+f'({n} صفحة)',h,count=1,flags=re.S)
            h=re.sub(rf'(id="sec-{slug}".*?)• \d+ صفحة</p>',lambda m:m.group(1)+f'• {n} صفحة</p>',h,count=1,flags=re.S)
        h=h.replace(f'RAYL_',f'RAYL_')
        h=re.sub(r'_(\d\d-\d\d)\.pdf',f'_{new["code"]}.pdf',h) if False else h.replace(f'_{old["code"]}.pdf',f'_{new["code"]}.pdf')
        h=h.replace(f'📅 {old["Fday"]} • إقفال الخميس {old["Tfull"]}',f'📅 {new["Fday"]} • إقفال الخميس {new["Tfull"]}')
        h=h.replace(f'التوقعات صالحة للأسبوع الجاي بس ({old["nx"]}',f'التوقعات صالحة للأسبوع الجاي بس ({new["nx"]}')
        open(f'{site}/reports.html','w').write(h)
        i=open(f'{site}/index.html').read().replace(f'على إقفال {old["T"]} — توقعات أسبوع {old["nx"]}',f'على إقفال {new["T"]} — توقعات أسبوع {new["nx"]}');open(f'{site}/index.html','w').write(i)
        msg=f'تحديث تقارير القطاعات على إقفال {new["Tfull"]}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_016z8xLKiXRpNtu7he7XPkGg'
        subprocess.run(['git','add','-A'],cwd=site);subprocess.run(['git','commit','-qm',msg],cwd=site);print(subprocess.run(['git','push','-q'],cwd=site,capture_output=True,text=True).stderr)
    if not pub_only and not bad: st['prev']=old;st['tok']=new;st['published']=False
    if '--publish' in sys.argv and not bad: st['published']=True
    json.dump(st,open(STATE,'w'),ensure_ascii=False)
main()

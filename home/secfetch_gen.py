import json,subprocess,os,sys
exec(open('/home/claude/indices/fetch.py').read().split('for s in sys.argv')[0])
cols=["ADX","ATR","BB.lower","BB.upper","MACD.macd","MACD.signal","RSI","SMA20","SMA50","SMA100","Stoch.K","Stoch.D","market_cap_basic","total_shares_outstanding","total_debt","total_equity","current_ratio","description","industry","currency","close","change"]
for s in sys.argv[1:]:
    ns={};exec(open(f'/home/claude/sec1120{s}/info.py').read(),ns);order=ns['ORDER']
    body=json.dumps({"symbols":{"tickers":["EGX:"+t for t in order]},"columns":cols})
    d=json.loads(subprocess.run(['curl','-s','https://scanner.tradingview.com/egypt/scan','-H','Content-Type: application/json','-d',body],capture_output=True,text=True).stdout)
    tv={r['s'].split(':')[1]:dict(zip(cols,r['d'])) for r in d['data']}
    order=[t for t in order if t in tv]
    day=json.load(open('/home/claude/secday1120.json'))
    for t in tv:
        if tv[t]['change'] is not None: day[t]=round(tv[t]['change'],2)
    json.dump(day,open('/home/claude/secday1120.json','w'))
    D=f'/home/claude/sec1120{s}/data';os.makedirs(D,exist_ok=True);ind={};best=None
    for t in order:
        v=bars('EGX:'+t,tf="1D",n=70)[-65:];q=tv[t]
        json.dump(dict(c=[x[4] for x in v],h=[x[2] for x in v],l=[x[3] for x in v],v=[x[5] for x in v],o=[x[1] for x in v],o0=v[0][1],t=[x[0] for x in v]),open(f'{D}/{t}.json','w'))
        if len(v)==65 and (best is None or v[-1][0]>=best[-1]): best=[x[0] for x in v]
        ind[t]=dict(ADX=q['ADX'],ATR=q['ATR'],BBL=q['BB.lower'],BBU=q['BB.upper'],MACD=q['MACD.macd'],SIG=q['MACD.signal'],RSI=q['RSI'],S20=q['SMA20'],S50=q['SMA50'],S100=q['SMA100'],K=q['Stoch.K'],D=q['Stoch.D'],mcap=q['market_cap_basic'],sh=q['total_shares_outstanding'],debt=q['total_debt'],eq=q['total_equity'],cr=q['current_ratio'],desc=q['description'],ind=q['industry'])
        print(s,t,len(v),v[-1][0])
    for t in ns['ORDER']:
        if t in tv: continue
        rows=[list(map(float,x.split(','))) for x in open(f'/home/claude/thndr/{t}.txt').read().strip().split(';')]
        json.dump(dict(c=[x[4] for x in rows],h=[x[2] for x in rows],l=[x[3] for x in rows],v=[x[5] for x in rows],o=[x[1] for x in rows],o0=rows[0][1],t=[x[0] for x in rows]),open(f'{D}/{t}.json','w'))
        I=json.load(open(f'/home/claude/thndr/{t}_ind.json'))
        ind[t]=dict(ADX=None,ATR=I['ATR'],BBL=I['BBL'],BBU=I['BBU'],MACD=I['MACD'],SIG=I['SIG'],RSI=I['RSI'],S20=I['S20'],S50=I['S50'],S100=I['S100'],K=I['K'],D=I['D'],mcap=I['mcap'],sh=None,debt=None,eq=None,cr=None,desc=t,ind='Thndr')
        day[t]=round((rows[-1][4]/rows[-2][4]-1)*100,2);json.dump(day,open('/home/claude/secday1120.json','w'));print('thndr',t)
    ind={t:ind[t] for t in ns['ORDER']}
    json.dump(best,open(f'{D}/t.json','w'));json.dump(ind,open(f'/home/claude/sec1120{s}/ind.json','w'),ensure_ascii=False)

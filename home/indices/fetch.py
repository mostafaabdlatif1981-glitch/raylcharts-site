import json,random,string,re,sys,websocket
def gen(p): return p+''.join(random.choice(string.ascii_lowercase) for _ in range(12))
def msg(f,p): m=json.dumps({"m":f,"p":p},separators=(',',':')); return f"~m~{len(m)}~m~{m}"
def bars(sym,tf="5",n=600):
    ws=websocket.create_connection("wss://data.tradingview.com/socket.io/websocket",header=["Origin: https://www.tradingview.com"],timeout=25)
    cs=gen("cs_")
    for f,p in [("set_auth_token",["unauthorized_user_token"]),("chart_create_session",[cs,""]),("resolve_symbol",[cs,"s1",'={"symbol":"%s","adjustment":"splits"}'%sym]),("create_series",[cs,"sds_1","s1","s1",tf,n])]:
        ws.send(msg(f,p))
    out=""
    while True:
        r=ws.recv()
        for h in re.findall(r"~m~\d+~m~~h~\d+",r): ws.send(h)
        out+=r
        if "series_completed" in r or "symbol_error" in r: break
    ws.close()
    m=re.search(r'"s":\[(.*?)\],"ns"',out)
    v=[x["v"] for x in json.loads("["+m.group(1)+"]")]
    return v
for s in sys.argv[1:]:
    v=bars("EGX:"+s); json.dump(v,open(s+".json","w")); print(s,len(v),v[-1])

import asyncio
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1240,'height':1754})
        await pg.goto('file:///home/claude/sec1120f/report.html');await pg.wait_for_timeout(1500)
        z=await pg.evaluate('''()=>{const out=[];for(const p of document.querySelectorAll('.pg')){const bd=p.querySelector('.bd'),ft=p.querySelector('.ft');
          const fits=()=>{const r=bd.getBoundingClientRect(),f=ft.getBoundingClientRect();return r.bottom<=f.top-14 && p.scrollHeight<=1754};
          let z=1;for(let k=1.04;k<=1.40;k+=0.02){bd.style.zoom=k;bd.style.width=(1144/k)+'px';if(fits())z=k;else break}
          bd.style.zoom=z;bd.style.width=(1144/z)+'px';out.push(Math.round(z*100))}return out}''')
        print('zoom',z)
        ov=await pg.evaluate("[...document.querySelectorAll('.pg')].map((p,i)=>[i+1,p.scrollHeight]).filter(x=>x[1]>1756)")
        print('overflow',ov)
        import os;os.makedirs('img',exist_ok=True)
        els=await pg.query_selector_all('.pg')
        for i,e in enumerate(els): await e.screenshot(path=f'img/p{i+1:02d}.jpg',type='jpeg',quality=85)
        await pg.pdf(path='report.pdf',width='1240px',height='1754px',print_background=True)
        await b.close()
asyncio.run(m())

// أكاديمية رايل — دوال مشتركة: الأكواد والجلسات (KV binding: SUBS، والمفتاح السري: SEND_KEY)
const enc = new TextEncoder();
const b64u = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

export async function sign(env, s) {
  const k = await crypto.subtle.importKey('raw', enc.encode('ac|' + env.SEND_KEY), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64u(await crypto.subtle.sign('HMAC', k, enc.encode(s)));
}

export const json = (o, status = 200, extra = {}) =>
  new Response(JSON.stringify(o), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra } });

export const getUser = async (env, code) => {
  const v = await env.SUBS.get('ac:u:' + code);
  return v ? JSON.parse(v) : null;
};
export const putUser = (env, code, u) => env.SUBS.put('ac:u:' + code, JSON.stringify(u));

export function cookieVal(request, name) {
  const c = request.headers.get('cookie') || '';
  const m = c.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]+)'));
  return m ? decodeURIComponent(m[1]) : '';
}

// يرجّع {code, user} لو الجلسة سليمة والكود شغال والجهاز مسجل، وإلا null
export async function session(request, env) {
  const v = cookieVal(request, 'ra_s');
  const p = v.split('.');
  if (p.length !== 3) return null;
  const [code, dev, sig] = p;
  if (sig !== (await sign(env, code + '.' + dev))) return null;
  const user = await getUser(env, code);
  if (!user || !user.active) return null;
  if (!(user.devices || []).some((d) => d.id === dev)) return null;
  return { code, dev, user };
}

export const isAdmin = (request, env) => !!env.SEND_KEY && request.headers.get('x-key') === env.SEND_KEY;

export function newCode() {
  const A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const r = crypto.getRandomValues(new Uint8Array(8));
  const s = [...r].map((x) => A[x % A.length]).join('');
  return 'RAYL-' + s.slice(0, 4) + '-' + s.slice(4);
}

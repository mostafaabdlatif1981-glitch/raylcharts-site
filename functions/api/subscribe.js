// يحفظ توكن الإشعارات في KV (binding: SUBS)
export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch (e) {}
  const t = (b.token || '').trim();
  if (!t || t.length < 20 || t.length > 400) return new Response('bad', { status: 400 });
  await env.SUBS.put('t:' + t, JSON.stringify({ ua: (b.ua || '').slice(0, 120), at: new Date().toISOString() }));
  return new Response('ok');
}

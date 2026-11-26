// إعداد بوت تليجرام: بيحفظ الإعدادات في KV. محمي بـ SEND_KEY. الرد ما بيرجّعش التوكن.
export async function onRequestPost({ request, env }) {
  if (!env.SEND_KEY || request.headers.get('x-key') !== env.SEND_KEY) return new Response('no', { status: 403 });
  const old = JSON.parse((await env.SUBS.get('tg_cfg')) || '{}');
  const m = await request.json();
  const cfg = { ...old };
  for (const k of ['token', 'admin', 'channel', 'secret', 'instapay']) if (m[k] !== undefined) cfg[k] = m[k];
  await env.SUBS.put('tg_cfg', JSON.stringify(cfg));
  return Response.json({ ok: true, has_token: !!cfg.token, admin: cfg.admin, channel: cfg.channel, instapay: cfg.instapay || null });
}

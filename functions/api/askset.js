// إعداد بوت الأسئلة @AskRaylBot: بيحفظ {token, secret, group} في KV تحت ask_cfg. محمي بـ SEND_KEY. الرد ما بيرجّعش التوكن.
export async function onRequestPost({ request, env }) {
  if (!env.SEND_KEY || request.headers.get('x-key') !== env.SEND_KEY) return new Response('no', { status: 403 });
  const old = JSON.parse((await env.SUBS.get('ask_cfg')) || '{}');
  const m = await request.json();
  const cfg = { ...old };
  for (const k of ['token', 'secret', 'group']) if (m[k] !== undefined) cfg[k] = m[k];
  await env.SUBS.put('ask_cfg', JSON.stringify(cfg));
  return Response.json({ ok: true, has_token: !!cfg.token, has_secret: !!cfg.secret, group: cfg.group || null });
}

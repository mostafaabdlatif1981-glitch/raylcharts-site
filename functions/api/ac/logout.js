export async function onRequestPost() {
  return new Response('{"ok":true}', { headers: { 'content-type': 'application/json', 'set-cookie': 'ra_s=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax' } });
}

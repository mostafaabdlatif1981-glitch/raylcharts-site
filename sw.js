// RAYL service worker: الصفحات من النت الأول (عشان التحديث اليومي)، والصور من الكاش
const V = 'rayl-v7';
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(V).then(c => c.addAll(['/', '/style.css', '/icon-192.png']))); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET' || new URL(r.url).origin !== location.origin || /\.mp4$/i.test(new URL(r.url).pathname) || new URL(r.url).pathname.startsWith('/api/')) return;
  const img = /\.(jpg|jpeg|png|webp|svg)$/i.test(new URL(r.url).pathname);
  if (img) { e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { const c = res.clone(); caches.open(V).then(x => x.put(r, c)); return res; }))); return; }
  e.respondWith(fetch(r).then(res => { const c = res.clone(); caches.open(V).then(x => x.put(r, c)); return res; }).catch(() => caches.match(r).then(m => m || caches.match('/'))));
});
// ---- إشعارات RAYL (FCM data messages) ----
self.addEventListener('push', e => {
  let d = {}; try { d = e.data.json(); } catch (x) { try { d = { data: { body: e.data.text() } }; } catch (y) {} }
  const m = d.data || d.notification || d;
  const title = m.title || 'RAYL • البورصة بجد';
  e.waitUntil(self.registration.showNotification(title, { body: m.body || '', icon: '/icon-192.png', badge: '/badge-96.png', vibrate: [120, 60, 120], dir: 'rtl', lang: 'ar', tag: m.tag || undefined, data: { url: m.url || '/' } }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close(); const u = (e.notification.data && e.notification.data.url) || '/';
  e.waitUntil(clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => { for (const c of cs) { if ('focus' in c) { c.navigate(u); return c.focus(); } } return clients.openWindow(u); }));
});

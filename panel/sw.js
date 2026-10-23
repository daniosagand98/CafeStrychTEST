/* Cafe Strych Manager – service worker V4.6: powiadomienia push + aplikacja dostępna bez internetu */
const CACHE = 'cs-app-v4.6';
const SHELL = ['./', './index.html', './manifest.webmanifest', './logo.webp', './icon-192.png', './icon-512.png', './apple-touch-icon.png', './favicon-32.png'];
const LIB = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.allSettled([...SHELL, LIB].map(u => c.add(u)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => e.waitUntil((async () => {
  for (const k of await caches.keys()) if (k.startsWith('cs-app-') && k !== CACHE) await caches.delete(k);
  await self.clients.claim();
})()));

// Aplikacja: najpierw internet (zawsze najnowsza wersja), bez internetu – zapisana kopia.
// Dane z bazy (Supabase) NIE są tu zapisywane – tym zajmuje się sama aplikacja.
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const own = url.origin === self.location.origin && url.pathname.startsWith(new URL(self.registration.scope).pathname);
  const lib = req.url.startsWith('https://cdn.jsdelivr.net/npm/@supabase/supabase-js');
  if (!own && !lib) return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const res = await fetch(req);
      if (res && res.ok) cache.put(req.mode === 'navigate' ? './index.html' : req, res.clone());
      return res;
    } catch (err) {
      const hit = await cache.match(req.mode === 'navigate' ? './index.html' : req, { ignoreSearch: req.mode === 'navigate' });
      if (hit) return hit;
      throw err;
    }
  })());
});

self.addEventListener('push', e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch { d = { body: e.data ? e.data.text() : '' }; }
  e.waitUntil(self.registration.showNotification(d.title || 'Cafe Strych', {
    body: d.body || '',
    icon: 'icon-192.png',
    badge: 'badge-96.png',
    tag: d.tag || 'cafe-strych',
    renotify: true,
    data: { url: d.url || './' }
  }));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = new URL(e.notification.data?.url || './', self.registration.scope).href;
  e.waitUntil((async () => {
    const wins = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const w of wins) {
      if (w.url.startsWith(self.registration.scope)) {
        await w.focus();
        w.postMessage({ type: 'open-url', url });
        return;
      }
    }
    await self.clients.openWindow(url);
  })());
});

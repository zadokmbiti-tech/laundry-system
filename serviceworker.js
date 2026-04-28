const CACHE_NAME = 'freshwash-v1';
const STATIC_ASSETS = [
  '/',
  '/static/images/hero-bg.jpg',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(respond => respond || fetch(event.request))
  );
});
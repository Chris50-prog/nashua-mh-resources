// Service Worker — Greater Nashua Community MH Resources
// Caches all pages for offline access at air-gapped facilities

const CACHE_NAME = 'mh-resources-v3';
const ASSETS = [
  './',
  './index.html',
  './resources.html',
  './tools.html',
  './guide.html',
  './admin.html',
  './404.html',
  './css/style.css',
  './js/auth-gate.js',
  './js/search.js',
  './js/toc.js',
  './favicon.svg',
  './manifest.json'
];

// Install: pre-cache all assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch: cache-first, fall back to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(cached => cached || fetch(event.request)
        .then(response => {
          // Cache successful GET responses
          if (response.ok && event.request.method === 'GET') {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
      )
      .catch(() => caches.match('./404.html'))
  );
});

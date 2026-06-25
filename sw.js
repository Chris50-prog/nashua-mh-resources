// Service Worker — Greater Nashua Community MH Resources
// Caches all pages for offline access at air-gapped facilities

const CACHE_NAME = 'mh-resources-v16';
const ASSETS = [
  './',
  './index.html',
  './resources.html',
  './tools.html',
  './guide.html',
  './neurobiology.html',
  './worksheets.html',
  './activities.html',
  './games.html',
  './screening.html',
  './map.html',
  './templates.html',
  './admin.html',
  './404.html',
  './css/design-system.css',
  './css/style.css',
  './js/auth-gate.js',
  './js/search.js',
  './js/toc.js',
  './js/fontsize.js',
  './js/a11y.js',
  './favicon.svg',
  './manifest.json',
  './pdfs/thought-record.pdf',
  './pdfs/cognitive-distortions.pdf',
  './pdfs/behavioral-activation.pdf',
  './pdfs/safety-plan.pdf',
  './pdfs/coping-skills.pdf',
  './pdfs/goal-setting.pdf',
  './pdfs/anxiety-ladder.pdf',
  './pdfs/dbt-diary-card.pdf',
  './pdfs/self-care-plan.pdf',
  './pdfs/relapse-prevention.pdf',
  './pdfs/handouts/understanding-depression.pdf',
  './pdfs/handouts/understanding-anxiety.pdf',
  './pdfs/handouts/understanding-ptsd.pdf',
  './pdfs/handouts/understanding-grief.pdf',
  './pdfs/coloring/mandala-calm.pdf',
  './pdfs/coloring/feelings-faces.pdf',
  './pdfs/coloring/nature-scene.pdf',
  './pdfs/coloring/kindness-jar.pdf',
  './pdfs/coloring/coping-wheel.pdf',
  './pdfs/coloring/growth-tree.pdf',
  './pdfs/dbt/tipp-crisis-survival.pdf',
  './pdfs/dbt/dear-man.pdf',
  './pdfs/dbt/please-emotion-regulation.pdf',
  './pdfs/dbt/radical-acceptance.pdf',
  './pdfs/dbt/wise-mind.pdf',
  './pdfs/dbt/check-the-facts.pdf',
  './pdfs/act/values-clarification.pdf',
  './pdfs/act/cognitive-defusion.pdf',
  './pdfs/act/mindful-breathing-body-scan.pdf',
  './pdfs/act/observing-self-leaves.pdf',
  './pdfs/trauma/window-of-tolerance.pdf',
  './pdfs/trauma/grounding-skills.pdf',
  './pdfs/trauma/grief-continuing-bonds.pdf',
  './pdfs/trauma/trigger-tracking.pdf',
  './pdfs/skills/anger-iceberg.pdf',
  './pdfs/skills/anger-time-out-plan.pdf',
  './pdfs/skills/distress-tolerance-accepts.pdf',
  './pdfs/recovery/self-esteem-inventory.pdf',
  './pdfs/recovery/assertive-communication.pdf',
  './pdfs/recovery/urge-surfing-halt.pdf',
  './pdfs/recovery/sleep-hygiene-plan.pdf',
  './pdfs/recovery/gratitude-positive-activity.pdf'
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

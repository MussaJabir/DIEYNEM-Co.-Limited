{% load static %}/* DIEYNEM service worker — installable PWA + offline fallback.

   Deliberately conservative for a content site managed from a live dashboard:
   - navigations are NETWORK-FIRST (visitors always get fresh content; the
     cached shell/offline page is only used when the network fails),
   - static assets are CACHE-FIRST (they're content-hashed, so immutable),
   - the dashboard and admin are never touched by the worker.
   A new deploy ships content-hashed asset URLs, so this file's bytes change,
   the browser fetches the new worker, and activate() purges caches that don't
   match the current CACHE name. Bump the version below for a hard reset. */

const CACHE = "dieynem-v2";
const OFFLINE_URL = "{% url 'offline' %}";
const PRECACHE = [
  OFFLINE_URL,
  "{% static 'css/tailwind.out.css' %}",
  "{% static 'css/fonts.css' %}",
  "{% static 'js/public.js' %}",
  "{% static 'icons/icon-192.png' %}",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Only same-origin GETs; never interfere with the dashboard or admin.
  if (req.method !== "GET" || url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/dashboard/") || url.pathname.startsWith("/admin/")) return;

  // Page navigations: network-first, fall back to cache, then the offline page.
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match(OFFLINE_URL)))
    );
    return;
  }

  // Static assets (hashed → immutable): cache-first, populate on miss.
  if (url.pathname.startsWith("{% get_static_prefix %}")) {
    event.respondWith(
      caches.match(req).then(
        (hit) =>
          hit ||
          fetch(req).then((res) => {
            const copy = res.clone();
            caches.open(CACHE).then((cache) => cache.put(req, copy));
            return res;
          })
      )
    );
  }
});

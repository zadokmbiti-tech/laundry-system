self.addEventListener('install',event=> {
  console.log('Service worker installed');
});

self.addEventListener('fetch',event =>{
  event.respondWith(
    caches.match(event.request)
      .then(respond => respond|| fetch(event.request))
  );
});
// Service worker minimal pour rendre le dashboard Trends installable
// en tant que PWA (Progressive Web App). Il ne fait pas de mise en
// cache avancée pour l'instant -- juste le strict nécessaire pour que
// les navigateurs proposent l'installation sur l'écran d'accueil.

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Laisse passer toutes les requêtes normalement (pas de cache hors
  // ligne pour l'instant -- l'application nécessite une connexion pour
  // charger les données, un mode hors ligne complet n'aurait pas de sens).
  event.respondWith(fetch(event.request));
});

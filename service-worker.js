self.addEventListener('push', function(event) {
  const options = {
    body: event.data ? event.data.text() : 'A new PDF has been uploaded.',
    icon: '/icon.png', // Add an icon to show in the notification
    badge: '/badge.png' // Add a badge image for the notification
  };
  event.waitUntil(
    self.registration.showNotification('New PDF Uploaded!', options)
  );
});

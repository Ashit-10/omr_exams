importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging.js');

firebase.initializeApp({
  apiKey: "AIzaSyADJjStDyD7KFjvGPKqUlFR4ypjkgQlV7M",
  authDomain: "send-notification-2d9db.firebaseapp.com",
  projectId: "send-notification-2d9db",
  storageBucket: "send-notification-2d9db.firebasestorage.app",
  messagingSenderId: "519682556638",
  appId: "1:519682556638:web:c8c359120381dab921f84f",
  measurementId: "G-7B3BH3S308"
});

const messaging = firebase.messaging();

// Background push notification handler
messaging.onBackgroundMessage(function(payload) {
  console.log('Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: payload.notification.icon
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

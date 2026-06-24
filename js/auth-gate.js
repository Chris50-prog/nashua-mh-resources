// Site-wide authentication gate
// SHA-256 hash of access passphrase — client-side only, no data persistence
(function() {
  'use strict';

  var SITE_HASH = '55e5c8d2691facf5735fdeb1052369175b9c32e0594fc3f24630402c185253db';
  var SESSION_KEY = '__mh_auth';

  // Check if already authenticated this session
  if (sessionStorage.getItem(SESSION_KEY) === 'true') return;

  // Build the overlay
  var overlay = document.createElement('div');
  overlay.id = 'auth-overlay';
  overlay.innerHTML = [
    '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;',
    'background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 50%,#0d9488 100%);',
    'font-family:Segoe UI,system-ui,-apple-system,sans-serif;padding:24px;">',
    '<div style="background:white;border-radius:16px;padding:48px 40px;max-width:420px;width:100%;',
    'box-shadow:0 25px 50px rgba(0,0,0,0.25);text-align:center;">',
    '<div style="width:56px;height:56px;border-radius:14px;',
    'background:linear-gradient(135deg,#2563eb,#0d9488);',
    'display:flex;align-items:center;justify-content:center;margin:0 auto 20px;',
    'color:white;font-size:24px;font-weight:800;">MH</div>',
    '<h1 style="font-size:22px;font-weight:700;color:#1a1d2e;margin-bottom:6px;">',
    'Greater Nashua MH Resources</h1>',
    '<p style="font-size:14px;color:#5c6178;margin-bottom:28px;">',
    'Authorized access only. Enter the site passphrase to continue.</p>',
    '<div id="auth-error" style="display:none;background:#fef2f2;border:1px solid #fca5a5;',
    'border-radius:8px;padding:10px 14px;margin-bottom:16px;',
    'font-size:13px;color:#dc2626;font-weight:500;">Incorrect passphrase</div>',
    '<input id="auth-input" type="password" placeholder="Enter passphrase" ',
    'autocomplete="off" style="width:100%;padding:14px 16px;border:2px solid #e1e4ea;',
    'border-radius:10px;font-size:15px;outline:none;transition:border-color 0.2s;',
    'box-sizing:border-box;margin-bottom:14px;">',
    '<button id="auth-btn" style="width:100%;padding:14px;background:#2563eb;color:white;',
    'border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;',
    'transition:background 0.2s;">Access Site</button>',
    '<p style="font-size:12px;color:#8b90a0;margin-top:20px;">',
    'For authorized clinical staff only.<br>',
    'If you need access, contact your supervisor.</p>',
    '</div></div>'
  ].join('');

  // Hide body content
  document.body.style.overflow = 'hidden';
  var origDisplay = [];
  var children = document.body.children;
  for (var i = 0; i < children.length; i++) {
    origDisplay.push(children[i].style.display);
    children[i].style.display = 'none';
  }

  document.body.insertBefore(overlay, document.body.firstChild);

  var input = document.getElementById('auth-input');
  var btn = document.getElementById('auth-btn');
  var error = document.getElementById('auth-error');

  input.addEventListener('focus', function() {
    this.style.borderColor = '#2563eb';
  });
  input.addEventListener('blur', function() {
    this.style.borderColor = '#e1e4ea';
  });

  function attemptAuth() {
    var passphrase = input.value;
    if (!passphrase) return;
    btn.textContent = 'Verifying...';
    btn.disabled = true;

    // Use Web Crypto API for SHA-256
    var encoder = new TextEncoder();
    var data = encoder.encode(passphrase);
    crypto.subtle.digest('SHA-256', data).then(function(hashBuffer) {
      var hashArray = Array.from(new Uint8Array(hashBuffer));
      var hashHex = hashArray.map(function(b) { return b.toString(16).padStart(2, '0'); }).join('');

      if (hashHex === SITE_HASH) {
        // Authenticated — persist for session, reveal content
        sessionStorage.setItem(SESSION_KEY, 'true');
        overlay.style.transition = 'opacity 0.3s';
        overlay.style.opacity = '0';
        setTimeout(function() {
          overlay.remove();
          document.body.style.overflow = '';
          var ch = document.body.children;
          for (var j = 0; j < ch.length; j++) {
            ch[j].style.display = origDisplay[j] || '';
          }
        }, 300);
      } else {
        error.style.display = 'block';
        input.value = '';
        input.style.borderColor = '#dc2626';
        btn.textContent = 'Access Site';
        btn.disabled = false;
        input.focus();
        setTimeout(function() {
          input.style.borderColor = '#e1e4ea';
        }, 2000);
      }
    });
  }

  btn.addEventListener('click', attemptAuth);
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') attemptAuth();
  });

  // Focus input after render
  setTimeout(function() { input.focus(); }, 100);
})();

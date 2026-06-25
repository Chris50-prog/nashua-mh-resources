/* ============================================================
   a11y.js — WCAG 2.1 AA progressive enhancement
   ------------------------------------------------------------
   Applies three site-wide remediations that would otherwise
   require editing thousands of generated elements by hand:

     1. Keyboard operability (2.1.1, 4.1.2) — any element with an
        onclick handler that is not natively interactive is given
        role="button", tabindex="0", and Enter/Space activation.
     2. Decorative icons (1.1.1) — inline <svg> icons that carry no
        accessible name are hidden from assistive tech.
     3. Programmatic labels (1.3.1, 3.3.2, 4.1.2) — form controls
        with no associated label are wired to an adjacent <label>,
        a neighbouring text node, their column header, or their
        placeholder.

   Runs on load and re-runs (debounced) when JS injects new
   content such as the screening/template wizards and generated
   tables. Purely additive: controls that are already accessible
   are left untouched.
   ============================================================ */
(function () {
  'use strict';

  var idn = 0;
  function uid(prefix) { return (prefix || 'a11y') + '-' + (++idn); }

  function nativelyInteractive(el) {
    return /^(A|BUTTON|INPUT|SELECT|TEXTAREA|SUMMARY|DETAILS|LABEL)$/.test(el.tagName);
  }
  function hasName(el) {
    return !!(el.getAttribute('aria-label') ||
              el.getAttribute('aria-labelledby') ||
              el.getAttribute('title'));
  }
  function escId(id) {
    return (window.CSS && CSS.escape) ? CSS.escape(id) : id.replace(/"/g, '\\"');
  }

  /* 1. Make onclick'd divs/spans keyboard operable -------------- */
  function makeKeyboardOperable() {
    var nodes = document.querySelectorAll('[onclick]');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (nativelyInteractive(el)) continue;
      // Backdrops/overlays are a redundant pointer-dismiss; the real
      // control elsewhere is already keyboard reachable.
      if (/overlay|backdrop/i.test(el.className || '')) continue;
      // If it wraps a genuine control, that child handles the keyboard.
      if (el.querySelector('a[href],button,input,select,textarea')) continue;

      if (!el.hasAttribute('role')) el.setAttribute('role', 'button');
      if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
      if (el.getAttribute('data-a11y-keys')) continue;
      el.setAttribute('data-a11y-keys', '1');
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
          e.preventDefault();
          this.click();
        }
      });
    }
  }

  /* 2. Hide decorative SVG icons from assistive tech ------------ */
  function hideDecorativeSvgs() {
    var svgs = document.getElementsByTagName('svg');
    for (var i = 0; i < svgs.length; i++) {
      var svg = svgs[i];
      if (svg.hasAttribute('aria-hidden') ||
          svg.hasAttribute('aria-label') ||
          svg.getAttribute('role') === 'img') continue;
      // Leave the icon visible to AT only if it is the sole naming
      // content of an otherwise-unnamed control (so the control keeps
      // a name). All such controls on this site already carry their
      // own label, so this branch is a safety net, not the norm.
      var ctrl = svg.closest && svg.closest('button, a[href], [role="button"]');
      if (ctrl && !hasName(ctrl) && !(ctrl.textContent || '').replace(/\s+/g, '')) continue;
      svg.setAttribute('aria-hidden', 'true');
      svg.setAttribute('focusable', 'false');
    }
  }

  /* 3. Associate labels with otherwise-unlabeled controls ------- */
  function associateLabels() {
    var sel = 'input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset])' +
                ':not([aria-label]):not([aria-labelledby]),' +
              'select:not([aria-label]):not([aria-labelledby]),' +
              'textarea:not([aria-label]):not([aria-labelledby])';
    var ctrls = document.querySelectorAll(sel);
    for (var i = 0; i < ctrls.length; i++) {
      var c = ctrls[i];
      if (c.closest && c.closest('label')) continue;                       // wrapped in a label
      if (c.id && document.querySelector('label[for="' + escId(c.id) + '"]')) continue;

      // a) immediately preceding <label> sibling -> wire for/id
      var prev = c.previousElementSibling;
      while (prev && (prev.tagName === 'BR' ||
             (prev.tagName === 'SPAN' && !prev.textContent.trim()))) {
        prev = prev.previousElementSibling;
      }
      if (prev && prev.tagName === 'LABEL' && !prev.htmlFor) {
        if (!c.id) c.id = uid('fld');
        prev.htmlFor = c.id;
        continue;
      }

      // b) checkbox/radio with a following text node/element -> labelledby
      if (c.type === 'checkbox' || c.type === 'radio') {
        var next = c.nextElementSibling;
        if (next && next.textContent && next.textContent.trim()) {
          if (!next.id) next.id = uid('lbl');
          c.setAttribute('aria-labelledby', next.id);
          continue;
        }
      }

      // c) placeholder as accessible name
      if (c.placeholder && c.placeholder.trim()) {
        c.setAttribute('aria-label', c.placeholder.trim());
        continue;
      }

      // d) table cell -> use the matching column header text
      var td = c.closest && c.closest('td');
      if (td && td.cellIndex >= 0) {
        var table = c.closest('table');
        var ths = table && table.querySelectorAll('thead th, tr th');
        if (ths && ths[td.cellIndex]) {
          var t = ths[td.cellIndex].textContent.trim();
          if (t) { c.setAttribute('aria-label', t); continue; }
        }
      }
    }
  }

  function run() {
    try { makeKeyboardOperable(); } catch (e) {}
    try { hideDecorativeSvgs(); } catch (e) {}
    try { associateLabels(); } catch (e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }

  // Re-apply after JS injects new DOM (wizards, generated tables).
  // run() only adds attributes/listeners (no child nodes), so observing
  // childList cannot cause a feedback loop. Debounced to one pass/frame.
  var scheduled = false;
  function schedule() {
    if (scheduled) return;
    scheduled = true;
    (window.requestAnimationFrame || window.setTimeout)(function () {
      scheduled = false;
      run();
    }, 16);
  }
  function observe() {
    if (!document.body || !window.MutationObserver) return;
    new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var added = muts[i].addedNodes;
        if (!added) continue;
        // Only react to element insertions (wizards, generated tables).
        // Ignore text-node churn from live calculators/value displays.
        for (var j = 0; j < added.length; j++) {
          if (added[j].nodeType === 1) { schedule(); return; }
        }
      }
    }).observe(document.body, { childList: true, subtree: true });
  }
  if (document.body) observe();
  else document.addEventListener('DOMContentLoaded', observe);
})();

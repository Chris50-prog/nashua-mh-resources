// js/toc.js — Auto-generated floating Table of Contents
(function () {
  'use strict';

  var STORAGE_KEY = '__mh_toc_open';
  var HIGHLIGHT_MS = 1200;

  /* ---------- State ---------- */
  var btn, panel;
  var isOpen = false;
  var sections = [];   // { el, label }
  var observer;

  /* ---------- Bootstrap ---------- */
  document.addEventListener('DOMContentLoaded', init);

  function init() {
    sections = discoverSections();
    if (!sections.length) return; // nothing to list

    createDOM();
    wireEvents();
    setupScrollSpy();

    // Restore saved state
    if (sessionStorage.getItem(STORAGE_KEY) === 'true') {
      openPanel();
    }
  }

  /* ---------- Section discovery ---------- */
  function discoverSections() {
    var found = [];

    // tools.html pattern: .modality-section > .modality-header h2
    var modSections = document.querySelectorAll('.modality-section');
    if (modSections.length) {
      for (var i = 0; i < modSections.length; i++) {
        var header = modSections[i].querySelector('.modality-header h2');
        if (header) {
          found.push({ el: modSections[i], label: header.textContent.trim() });
        }
      }
      if (found.length) return found;
    }

    // guide.html pattern: .guide-category > .category-header h2
    var guideSections = document.querySelectorAll('.guide-category');
    if (guideSections.length) {
      for (var j = 0; j < guideSections.length; j++) {
        var catHeader = guideSections[j].querySelector('.category-header h2');
        if (catHeader) {
          found.push({ el: guideSections[j], label: catHeader.textContent.trim() });
        }
      }
      if (found.length) return found;
    }

    // Fallback: all h2 inside #main-content
    var mainContent = document.getElementById('main-content');
    var container = mainContent || document.body;
    var headings = container.querySelectorAll('h2');
    for (var k = 0; k < headings.length; k++) {
      // Use the heading's parent section if available, otherwise the heading itself
      var sectionEl = headings[k].closest('section') || headings[k];
      found.push({ el: sectionEl, label: headings[k].textContent.trim() });
    }

    return found;
  }

  /* ---------- DOM creation ---------- */
  function createDOM() {
    // Toggle button
    btn = document.createElement('button');
    btn.id = 'tocToggle';
    btn.className = 'toc-toggle';
    btn.setAttribute('aria-label', 'Table of Contents');
    btn.setAttribute('aria-expanded', 'false');
    btn.textContent = 'Contents';
    document.body.appendChild(btn);

    // Panel
    panel = document.createElement('div');
    panel.id = 'tocPanel';
    panel.className = 'toc-panel';
    panel.setAttribute('role', 'navigation');
    panel.setAttribute('aria-label', 'Table of Contents');

    var heading = document.createElement('div');
    heading.className = 'toc-panel-heading';
    heading.textContent = 'On This Page';
    panel.appendChild(heading);

    var list = document.createElement('ul');
    list.className = 'toc-list';

    for (var i = 0; i < sections.length; i++) {
      var li = document.createElement('li');
      li.className = 'toc-item';

      var link = document.createElement('button');
      link.className = 'toc-link';
      link.setAttribute('type', 'button');
      link.setAttribute('data-toc-index', String(i));
      link.textContent = sections[i].label;

      li.appendChild(link);
      list.appendChild(li);
    }

    panel.appendChild(list);
    document.body.appendChild(panel);
  }

  /* ---------- Events ---------- */
  function wireEvents() {
    btn.addEventListener('click', function () {
      if (isOpen) {
        closePanel();
      } else {
        openPanel();
      }
    });

    panel.addEventListener('click', function (e) {
      var target = e.target.closest('.toc-link');
      if (!target) return;

      var idx = parseInt(target.getAttribute('data-toc-index'), 10);
      if (isNaN(idx) || !sections[idx]) return;

      scrollToSection(idx);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen) {
        closePanel();
        btn.focus();
      }
    });
  }

  /* ---------- Open / Close ---------- */
  function openPanel() {
    isOpen = true;
    panel.classList.add('toc-panel--open');
    btn.classList.add('toc-toggle--active');
    btn.setAttribute('aria-expanded', 'true');
    sessionStorage.setItem(STORAGE_KEY, 'true');
  }

  function closePanel() {
    isOpen = false;
    panel.classList.remove('toc-panel--open');
    btn.classList.remove('toc-toggle--active');
    btn.setAttribute('aria-expanded', 'false');
    sessionStorage.setItem(STORAGE_KEY, 'false');
  }

  /* ---------- Scroll + highlight ---------- */
  function scrollToSection(idx) {
    var section = sections[idx];
    if (!section) return;

    section.el.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Brief highlight
    section.el.classList.add('toc-highlight');
    setTimeout(function () {
      section.el.classList.remove('toc-highlight');
    }, HIGHLIGHT_MS);
  }

  /* ---------- Scroll spy via IntersectionObserver ---------- */
  function setupScrollSpy() {
    if (!('IntersectionObserver' in window)) return;

    var options = {
      rootMargin: '-10% 0px -80% 0px',
      threshold: 0
    };

    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;

        // Find which section index this element corresponds to
        for (var i = 0; i < sections.length; i++) {
          if (sections[i].el === entry.target) {
            setActiveLink(i);
            break;
          }
        }
      });
    }, options);

    for (var i = 0; i < sections.length; i++) {
      observer.observe(sections[i].el);
    }
  }

  function setActiveLink(activeIdx) {
    var links = panel.querySelectorAll('.toc-link');
    for (var i = 0; i < links.length; i++) {
      if (i === activeIdx) {
        links[i].classList.add('toc-link--active');
      } else {
        links[i].classList.remove('toc-link--active');
      }
    }
  }
})();

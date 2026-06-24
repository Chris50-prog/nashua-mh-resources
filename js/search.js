/* ===== Global Site Search — Wave 4 ===== */
(function () {
  'use strict';

  /* ---------- DOM refs (injected by initSearch) ---------- */
  var overlay, input, resultsContainer, countEl, closeBtn, noResults;
  var toggle; // header button
  var isOpen = false;
  var results = [];   // current result objects
  var activeIdx = -1; // keyboard-selected index

  /* ---------- Bootstrap ---------- */
  function initSearch() {
    // Build the overlay HTML and append after header
    var header = document.querySelector('.site-header');
    if (!header) return;

    // Create overlay
    overlay = document.createElement('div');
    overlay.className = 'search-overlay';
    overlay.id = 'globalSearchOverlay';
    overlay.setAttribute('role', 'search');
    overlay.setAttribute('aria-label', 'Site search');
    overlay.innerHTML =
      '<div class="search-overlay-inner">' +
        '<div class="search-overlay-bar">' +
          '<svg class="search-overlay-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' +
          '<input type="text" class="search-overlay-input" id="globalSearchInput" placeholder="Search this page..." autocomplete="off" aria-label="Search this page">' +
          '<span class="search-overlay-count" id="globalSearchCount"></span>' +
          '<button class="search-overlay-close" id="globalSearchClose" aria-label="Close search" title="Close search">&times;</button>' +
        '</div>' +
        '<div class="search-results" id="globalSearchResults"></div>' +
        '<div class="search-no-results" id="globalSearchNoResults">' +
          '<div class="search-no-results-icon">&#128269;</div>' +
          '<p class="search-no-results-title">No results found</p>' +
          '<p class="search-no-results-hint">Try different keywords, or check <a href="resources.html">Resources</a>, <a href="tools.html">Clinical Tools</a>, or <a href="guide.html">How-To Guides</a>.</p>' +
        '</div>' +
      '</div>';

    header.parentNode.insertBefore(overlay, header.nextSibling);

    input = document.getElementById('globalSearchInput');
    resultsContainer = document.getElementById('globalSearchResults');
    countEl = document.getElementById('globalSearchCount');
    closeBtn = document.getElementById('globalSearchClose');
    noResults = document.getElementById('globalSearchNoResults');

    // Wire events
    closeBtn.addEventListener('click', closeSearch);
    input.addEventListener('input', debounce(onInput, 200));
    input.addEventListener('keydown', onKeydown);
    document.addEventListener('keydown', onGlobalKey);
    document.addEventListener('click', onDocClick);
  }

  /* ---------- Toggle open / close ---------- */
  function openSearch() {
    if (isOpen) return;
    isOpen = true;
    overlay.classList.add('open');
    input.value = '';
    resultsContainer.innerHTML = '';
    countEl.textContent = '';
    noResults.style.display = 'none';
    results = [];
    activeIdx = -1;
    // Delay focus slightly so the transition has started
    setTimeout(function () { input.focus(); }, 60);
  }

  function closeSearch() {
    if (!isOpen) return;
    isOpen = false;
    overlay.classList.remove('open');
    input.value = '';
    resultsContainer.innerHTML = '';
    countEl.textContent = '';
    noResults.style.display = 'none';
    results = [];
    activeIdx = -1;
    // Return focus to toggle button
    var btn = document.querySelector('.search-toggle');
    if (btn) btn.focus();
  }

  /* ---------- Build the page index ---------- */
  function buildIndex() {
    var sections = [];
    // Gather headings and their text blocks
    var headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headings.forEach(function (h) {
      // Skip hidden elements and elements inside the search overlay
      if (h.closest('.search-overlay')) return;
      if (h.closest('[style*="display:none"], [style*="display: none"]')) return;
      if (h.offsetParent === null && h.closest('.site-header') === null) return;

      var title = h.textContent.trim();
      if (!title) return;

      // Collect text from siblings until next heading of same or higher level
      var level = parseInt(h.tagName.charAt(1), 10);
      var texts = [];
      var node = h.nextElementSibling;
      while (node) {
        if (/^H[1-6]$/.test(node.tagName) && parseInt(node.tagName.charAt(1), 10) <= level) break;
        if (!node.closest('.search-overlay') && node.offsetParent !== null) {
          var t = node.textContent.trim();
          if (t) texts.push(t);
        }
        node = node.nextElementSibling;
      }

      // Also walk up to find a section/article/div with an id for scroll target
      var scrollTarget = h;
      if (h.id) {
        scrollTarget = h;
      } else {
        var parent = h.parentElement;
        while (parent && parent !== document.body) {
          if (parent.id) { scrollTarget = parent; break; }
          parent = parent.parentElement;
        }
        // If no id found, use the heading itself
        if (!parent || parent === document.body) scrollTarget = h;
      }

      sections.push({
        title: title,
        body: texts.join(' '),
        element: scrollTarget,
        heading: h
      });
    });

    return sections;
  }

  /* ---------- Search logic ---------- */
  function onInput() {
    var query = input.value.trim();
    if (query.length < 2) {
      resultsContainer.innerHTML = '';
      countEl.textContent = '';
      noResults.style.display = 'none';
      results = [];
      activeIdx = -1;
      return;
    }

    var index = buildIndex();
    var terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    var matches = [];

    index.forEach(function (section) {
      var fullText = (section.title + ' ' + section.body).toLowerCase();
      var score = 0;
      var allMatch = true;

      terms.forEach(function (term) {
        if (fullText.indexOf(term) === -1) {
          allMatch = false;
        } else {
          // Count occurrences for ranking
          var idx = 0;
          var count = 0;
          while ((idx = fullText.indexOf(term, idx)) !== -1) {
            count++;
            idx += term.length;
          }
          score += count;
          // Boost title matches
          if (section.title.toLowerCase().indexOf(term) !== -1) {
            score += 5;
          }
        }
      });

      if (allMatch) {
        matches.push({
          section: section,
          score: score
        });
      }
    });

    // Sort by score descending
    matches.sort(function (a, b) { return b.score - a.score; });

    // Cap at 20 results
    matches = matches.slice(0, 20);

    results = matches;
    activeIdx = -1;
    renderResults(matches, terms);
  }

  function renderResults(matches, terms) {
    if (matches.length === 0) {
      resultsContainer.innerHTML = '';
      countEl.textContent = '';
      noResults.style.display = 'block';
      return;
    }

    noResults.style.display = 'none';
    countEl.textContent = matches.length + ' result' + (matches.length === 1 ? '' : 's') + ' found';

    var html = '';
    matches.forEach(function (m, i) {
      var excerpt = getExcerpt(m.section.body || m.section.title, terms);
      html +=
        '<div class="search-result-card" data-index="' + i + '" tabindex="0" role="button">' +
          '<div class="search-result-section">' + escapeHtml(m.section.title) + '</div>' +
          '<div class="search-result-excerpt">' + excerpt + '</div>' +
          '<div class="search-result-action">Scroll to section &#8599;</div>' +
        '</div>';
    });

    resultsContainer.innerHTML = html;

    // Wire click handlers
    var cards = resultsContainer.querySelectorAll('.search-result-card');
    cards.forEach(function (card) {
      card.addEventListener('click', function () {
        var idx = parseInt(card.getAttribute('data-index'), 10);
        scrollToResult(idx);
      });
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          var idx = parseInt(card.getAttribute('data-index'), 10);
          scrollToResult(idx);
        }
      });
    });
  }

  function scrollToResult(idx) {
    if (!results[idx]) return;
    var el = results[idx].section.element;
    closeSearch();
    // Small delay to let overlay close
    setTimeout(function () {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Brief highlight
      el.classList.add('search-scroll-target');
      setTimeout(function () {
        el.classList.remove('search-scroll-target');
      }, 2000);
    }, 150);
  }

  function getExcerpt(text, terms) {
    if (!text) return '';
    // Find first occurrence of any term
    var lowerText = text.toLowerCase();
    var bestPos = text.length;
    terms.forEach(function (t) {
      var pos = lowerText.indexOf(t);
      if (pos !== -1 && pos < bestPos) bestPos = pos;
    });

    // Extract context window around match
    var start = Math.max(0, bestPos - 60);
    var end = Math.min(text.length, bestPos + 120);
    var excerpt = text.substring(start, end);
    if (start > 0) excerpt = '...' + excerpt;
    if (end < text.length) excerpt = excerpt + '...';

    // Highlight terms
    excerpt = escapeHtml(excerpt);
    terms.forEach(function (t) {
      var escaped = escapeRegex(t);
      var re = new RegExp('(' + escaped + ')', 'gi');
      excerpt = excerpt.replace(re, '<mark class="search-highlight">$1</mark>');
    });

    return excerpt;
  }

  /* ---------- Keyboard navigation ---------- */
  function onKeydown(e) {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeSearch();
      return;
    }

    if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIdx >= 0 && results[activeIdx]) {
        scrollToResult(activeIdx);
      } else if (results.length > 0) {
        scrollToResult(0);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (results.length === 0) return;
      activeIdx = Math.min(activeIdx + 1, results.length - 1);
      highlightActive();
      return;
    }

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (results.length === 0) return;
      activeIdx = Math.max(activeIdx - 1, 0);
      highlightActive();
      return;
    }
  }

  function onGlobalKey(e) {
    // Ctrl/Cmd + K to open search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      if (isOpen) {
        closeSearch();
      } else {
        openSearch();
      }
      return;
    }

    if (e.key === 'Escape' && isOpen) {
      e.preventDefault();
      closeSearch();
    }
  }

  function highlightActive() {
    var cards = resultsContainer.querySelectorAll('.search-result-card');
    cards.forEach(function (c, i) {
      if (i === activeIdx) {
        c.classList.add('active');
        c.scrollIntoView({ block: 'nearest' });
      } else {
        c.classList.remove('active');
      }
    });
  }

  /* ---------- Click outside ---------- */
  function onDocClick(e) {
    if (!isOpen) return;
    // Clicked on toggle button? Let that handler manage it.
    if (e.target.closest('.search-toggle')) return;
    // Clicked inside overlay? Stay open.
    if (e.target.closest('.search-overlay')) return;
    closeSearch();
  }

  /* ---------- Utilities ---------- */
  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function debounce(fn, ms) {
    var timer;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(fn, ms);
    };
  }

  /* ---------- Expose toggle for the header button ---------- */
  window.toggleGlobalSearch = function () {
    if (isOpen) {
      closeSearch();
    } else {
      openSearch();
    }
  };

  /* ---------- Init on DOM ready ---------- */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
  } else {
    initSearch();
  }
})();

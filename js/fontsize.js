(function () {
  var STORAGE_KEY = '__mh_fontsize';
  var DEFAULT_SIZE = 16;
  var MIN_SIZE = 13;
  var MAX_SIZE = 22;

  function currentSize() {
    var stored = sessionStorage.getItem(STORAGE_KEY);
    if (stored !== null) {
      var parsed = parseInt(stored, 10);
      if (!isNaN(parsed) && parsed >= MIN_SIZE && parsed <= MAX_SIZE) {
        return parsed;
      }
    }
    return DEFAULT_SIZE;
  }

  function applySize(size) {
    document.documentElement.style.fontSize = size + 'px';
    sessionStorage.setItem(STORAGE_KEY, String(size));
  }

  window.mhFontIncrease = function () {
    var size = currentSize();
    if (size < MAX_SIZE) {
      applySize(size + 1);
    }
  };

  window.mhFontDecrease = function () {
    var size = currentSize();
    if (size > MIN_SIZE) {
      applySize(size - 1);
    }
  };

  applySize(currentSize());
})();

// INK — scroll reveal + blog filter
(function () {
  'use strict';

  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('visible'); });
  }

  var filter = document.getElementById('blog-filter');
  if (filter) {
    var items = Array.prototype.slice.call(document.querySelectorAll('.log-row[data-cat]'));
    var years = Array.prototype.slice.call(document.querySelectorAll('.timeline-year[data-year-row]'));
    filter.addEventListener('click', function (e) {
      var btn = e.target.closest('.filter-btn');
      if (!btn) return;
      filter.querySelectorAll('.filter-btn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var cat = btn.getAttribute('data-cat');
      items.forEach(function (item) {
        item.classList.toggle('hidden', cat !== 'all' && item.getAttribute('data-cat') !== cat);
      });
      years.forEach(function (y) {
        var el = y.nextElementSibling;
        var anyVisible = false;
        while (el && el.classList.contains('log-row')) {
          if (!el.classList.contains('hidden')) { anyVisible = true; break; }
          el = el.nextElementSibling;
        }
        y.classList.toggle('hidden', !anyVisible);
      });
    });
  }
})();

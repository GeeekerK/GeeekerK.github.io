// INK — scroll reveal + blog filter + 年报横向长卷
(function () {
  'use strict';

  /* ---------- reveal on scroll ---------- */
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

  /* ---------- blog filter ---------- */
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

  /* ---------- 年报长卷 ----------
     把隐藏的 .scroll-source 按 h2 章节切成一格一格的画轴 panel，
     插到卷末 panel 之前；纵向滚轮映射为横向展卷。 */
  var viewport = document.getElementById('scroll-viewport');
  var source = document.getElementById('scroll-source');
  if (viewport && source) {
    var endPanel = viewport.querySelector('.scroll-end');
    var children = Array.prototype.slice.call(source.childNodes);
    var panel = null;

    function newPanel() {
      var s = document.createElement('section');
      s.className = 'scroll-panel scroll-chapter';
      viewport.insertBefore(s, endPanel);
      return s;
    }

    panel = newPanel();
    var panelHasContent = false;
    children.forEach(function (node) {
      if (node.nodeType === 3 && !node.textContent.trim()) return; // 空白文本
      if (node.nodeName === 'H2' && panelHasContent) {
        panel = newPanel();
        panelHasContent = false;
      }
      panel.appendChild(node.cloneNode(true));
      if (node.nodeType === 1 || node.textContent.trim()) panelHasContent = true;
    });

    // 滚轮纵向 → 横向展卷
    viewport.addEventListener('wheel', function (e) {
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
        var max = viewport.scrollWidth - viewport.clientWidth;
        var next = viewport.scrollLeft + e.deltaY;
        if ((next > 0 && next < max) || (viewport.scrollLeft > 0 && viewport.scrollLeft < max)) {
          e.preventDefault();
          viewport.scrollLeft = next;
        }
      }
    }, { passive: false });
  }
})();

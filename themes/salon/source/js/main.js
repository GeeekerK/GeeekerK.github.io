// SALON — theme toggle, generative grain canvas, blog filter
(function () {
  'use strict';

  /* ---------- dark mode ---------- */
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('salon-theme', next);
    });
  }

  /* ---------- generative grain canvas ----------
     Organic pixel-array texture in warm terracotta/olive tones.
     Slow drift + gentle mouse response. Respects reduced motion. */
  var canvas = document.getElementById('grain-canvas');
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext('2d');
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var cell = 7;              // pixel-array cell size
    var cols, rows, t = 0;
    var mouse = { x: 0.5, y: 0.5 };

    function resize() {
      var rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = Math.floor(rect.width / 2);   // half-res, CSS scales up
      canvas.height = Math.floor(rect.height / 2);
      cols = Math.ceil(canvas.width / cell);
      rows = Math.ceil(canvas.height / cell);
    }

    // cheap organic field: layered sines ≈ low-frequency noise
    function field(x, y, t) {
      return Math.sin(x * 0.9 + t * 0.4) * Math.cos(y * 1.1 - t * 0.3)
           + Math.sin((x + y) * 0.5 + t * 0.2) * 0.5
           + Math.sin(x * 0.23 - y * 0.31 + t * 0.1) * 0.8;
    }

    function draw() {
      var dark = document.documentElement.getAttribute('data-theme') === 'dark';
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      var mx = mouse.x * cols, my = mouse.y * rows;
      for (var i = 0; i < cols; i++) {
        for (var j = 0; j < rows; j++) {
          var v = field(i * 0.35, j * 0.35, t);              // -2.3 .. 2.3
          var dx = i - mx, dy = j - my;
          var mdist = Math.sqrt(dx * dx + dy * dy) / (cols * 0.35);
          v += Math.max(0, 1 - mdist) * 1.2;                  // mouse lift
          if (v > 1.15) {
            var a = Math.min((v - 1.15) * 0.5, 0.5);
            ctx.fillStyle = dark
              ? 'rgba(217, 119, 87,' + a + ')'                // coral on dark
              : 'rgba(201, 100, 66,' + a + ')';               // terracotta on parchment
            ctx.fillRect(i * cell, j * cell, cell - 1.5, cell - 1.5);
          } else if (v > 0.95) {
            var a2 = (v - 0.95) * 0.6;
            ctx.fillStyle = dark
              ? 'rgba(176, 174, 165,' + a2 * 0.25 + ')'
              : 'rgba(94, 93, 89,' + a2 * 0.22 + ')';         // olive gray
            ctx.fillRect(i * cell, j * cell, cell - 2.5, cell - 2.5);
          }
        }
      }
    }

    function loop() {
      t += 0.012;
      draw();
      requestAnimationFrame(loop);
    }

    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', function (e) {
      var rect = canvas.getBoundingClientRect();
      mouse.x = (e.clientX - rect.left) / rect.width;
      mouse.y = (e.clientY - rect.top) / rect.height;
    });

    if (reduceMotion) { draw(); } else { loop(); }
  }

  /* ---------- blog category filter ---------- */
  var filter = document.getElementById('blog-filter');
  if (filter) {
    var items = Array.prototype.slice.call(document.querySelectorAll('.timeline-item[data-cat]'));
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
      // hide year headings whose items are all hidden
      years.forEach(function (y) {
        var el = y.nextElementSibling;
        var anyVisible = false;
        while (el && el.classList.contains('timeline-item')) {
          if (!el.classList.contains('hidden')) { anyVisible = true; break; }
          el = el.nextElementSibling;
        }
        y.classList.toggle('hidden', !anyVisible);
      });
    });
  }
})();

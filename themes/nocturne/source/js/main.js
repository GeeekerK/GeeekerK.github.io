// NOCTURNE — particle field backdrop, card glow tracking, blog filter
(function () {
  'use strict';

  /* ---------- generative particle field ----------
     A drifting constellation: violet/cyan particles linked by
     hairline connections, gently attracted to the cursor.
     One fixed canvas shared by every page (the "de-coding" texture). */
  var canvas = document.getElementById('particle-field');
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext('2d');
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var W, H, particles = [];
    var mouse = { x: -9999, y: -9999 };
    var DENSITY = 14000; // px² per particle
    var LINK = 110;      // connection distance

    function resize() {
      W = canvas.width = window.innerWidth;
      H = canvas.height = window.innerHeight;
      var n = Math.min(90, Math.floor((W * H) / DENSITY));
      particles = [];
      for (var i = 0; i < n; i++) {
        particles.push({
          x: Math.random() * W,
          y: Math.random() * H,
          vx: (Math.random() - 0.5) * 0.22,
          vy: (Math.random() - 0.5) * 0.22,
          r: Math.random() * 1.6 + 0.6,
          cyan: Math.random() > 0.72   // ~28% cyan, rest violet
        });
      }
    }

    function step() {
      ctx.clearRect(0, 0, W, H);

      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];

        // gentle cursor attraction
        var dx = mouse.x - p.x, dy = mouse.y - p.y;
        var d2 = dx * dx + dy * dy;
        if (d2 < 260 * 260 && d2 > 1) {
          var d = Math.sqrt(d2);
          p.vx += (dx / d) * 0.006;
          p.vy += (dy / d) * 0.006;
        }

        p.x += p.vx; p.y += p.vy;
        p.vx *= 0.995; p.vy *= 0.995; // drag

        if (p.x < -20) p.x = W + 20; if (p.x > W + 20) p.x = -20;
        if (p.y < -20) p.y = H + 20; if (p.y > H + 20) p.y = -20;

        // links
        for (var j = i + 1; j < particles.length; j++) {
          var q = particles[j];
          var ddx = p.x - q.x, ddy = p.y - q.y;
          var dd = ddx * ddx + ddy * ddy;
          if (dd < LINK * LINK) {
            var alpha = (1 - Math.sqrt(dd) / LINK) * 0.16;
            ctx.strokeStyle = 'rgba(139, 124, 246,' + alpha + ')';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.stroke();
          }
        }

        // node
        ctx.fillStyle = p.cyan ? 'rgba(62,230,196,0.85)' : 'rgba(139,124,246,0.8)';
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }
      requestAnimationFrame(step);
    }

    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', function (e) { mouse.x = e.clientX; mouse.y = e.clientY; });
    window.addEventListener('mouseleave', function () { mouse.x = -9999; mouse.y = -9999; });

    if (reduceMotion) {
      // render one static frame only
      var frame = step;
      (function once() { ctx.clearRect(0, 0, W, H); })();
      // draw nodes without animation
      particles.forEach(function (p) {
        ctx.fillStyle = p.cyan ? 'rgba(62,230,196,0.85)' : 'rgba(139,124,246,0.8)';
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
      });
    } else {
      step();
    }
  }

  /* ---------- exhibit card glow follows cursor ---------- */
  document.querySelectorAll('.exhibit-card').forEach(function (card) {
    card.addEventListener('mousemove', function (e) {
      var rect = card.getBoundingClientRect();
      card.style.setProperty('--mx', ((e.clientX - rect.left) / rect.width * 100) + '%');
      card.style.setProperty('--my', ((e.clientY - rect.top) / rect.height * 100) + '%');
    });
  });

  /* ---------- blog category filter ---------- */
  var filter = document.getElementById('blog-filter');
  if (filter) {
    var items = Array.prototype.slice.call(document.querySelectorAll('.commit-row[data-cat]'));
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
        while (el && el.classList.contains('commit-row')) {
          if (!el.classList.contains('hidden')) { anyVisible = true; break; }
          el = el.nextElementSibling;
        }
        y.classList.toggle('hidden', !anyVisible);
      });
    });
  }
})();
